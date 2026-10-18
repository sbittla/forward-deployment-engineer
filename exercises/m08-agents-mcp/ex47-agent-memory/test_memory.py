from fde_kit import FakeLLM


def test_no_summary_under_budget(impl):
    m = impl.ConversationMemory(FakeLLM([]), max_tokens=1000)
    m.add("user", "hi")
    m.add("assistant", "hello")
    addendum, msgs = m.context()
    assert addendum == "" and msgs == [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]


def test_rolls_up_oldest(impl):
    llm = FakeLLM(["SUMMARY-1: policy P-77, customer Ana", "SUMMARY-2: policy P-77, refund approved"])
    m = impl.ConversationMemory(llm, max_tokens=100, keep_recent=2)
    for i in range(4):
        m.add("user" if i % 2 == 0 else "assistant", f"msg{i} " + "x" * 120)  # ~32 tokens each
    assert m.summaries_made == 1
    addendum, msgs = m.context()
    assert "Conversation summary:\nSUMMARY-1" in addendum
    assert [x["content"][:4] for x in msgs] == ["msg2", "msg3"]
    prompt = llm.calls[0]["messages"][0]["content"]
    assert "<previous_summary></previous_summary>" in prompt and "user: msg0" in prompt and "msg2" not in prompt
    assert "numbers" in llm.calls[0]["system"].lower()
    for i in range(4, 6):
        m.add("user" if i % 2 == 0 else "assistant", f"msg{i} " + "x" * 120)
    assert m.summaries_made == 2
    assert "<previous_summary>SUMMARY-1: policy P-77, customer Ana</previous_summary>" in llm.calls[1]["messages"][0]["content"]


def test_keep_recent_respected(impl):
    llm = FakeLLM(["S"])
    m = impl.ConversationMemory(llm, max_tokens=10, keep_recent=3)
    for i in range(3):
        m.add("user", "y" * 200)
    assert m.summaries_made == 0  # cannot fold below keep_recent
    m.add("assistant", "z")
    assert m.summaries_made == 1 and len(m.context()[1]) == 3


def test_pins(impl):
    m = impl.ConversationMemory(FakeLLM(["S"]), max_tokens=1000)
    m.pin("policy", "P-77")
    m.pin("customer", "Ana")
    m.pin("policy", "P-78")
    addendum, _ = m.context()
    assert addendum == "Pinned facts:\n- customer: Ana\n- policy: P-78"
