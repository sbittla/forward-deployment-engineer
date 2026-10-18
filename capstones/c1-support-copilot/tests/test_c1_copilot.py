from fde_kit import FakeLLM, LLMResponse

PACKAGE = "copilot"


def test_grounded_answer_with_citation(copilot):
    r = copilot.ask("Is water damage from a burst pipe covered?")
    assert r.intent == "policy_question" and not r.abstained and not r.escalated
    assert "burst pipe" in r.text and "[1]" in r.text
    assert r.citations == ["homeowners"] and r.chunk_ids == ["homeowners#water-damage"]
    assert r.cost_usd > 0


def test_abstains_without_calling_model(copilot, llm):
    r = copilot.ask("Does the policy cover cryptocurrency mining equipment overheating?")
    assert r.abstained and llm.calls == []


def test_routing(copilot, llm):
    r = copilot.ask("What is the status of my claim CL-20931?")
    assert r.intent == "claim_status" and "CL-20931" in r.text
    assert copilot.ask("I want to talk to a real person right now").escalated
    assert llm.calls == []


def test_pii_never_reaches_model(copilot, llm):
    r = copilot.ask("My email is ana@example.com - is jewelry theft covered?")
    assert r.redacted and "$1,500" in r.text
    sent = " ".join(m["content"] for c in llm.calls for m in c["messages"])
    assert "ana@example.com" not in sent and "[EMAIL_1]" in sent


def test_guardrail_blocks_promises(cap, cap_data):
    llm = FakeLLM(["Burst pipe damage is covered and approval is guaranteed [1]."])
    c = cap.Copilot(llm, cap.HybridRetriever(cap.load_corpus(cap_data / "policies")),
                    cap.IntentRouter.from_jsonl(cap_data / "intents.jsonl"))
    r = c.ask("Is water damage from a burst pipe covered?")
    assert r.escalated and "guaranteed" not in r.text


def test_invalid_citations_removed_and_uncited_escalates(cap, cap_data):
    retr = cap.HybridRetriever(cap.load_corpus(cap_data / "policies"))
    router = cap.IntentRouter.from_jsonl(cap_data / "intents.jsonl")
    c = cap.Copilot(FakeLLM(["Sudden water damage from a burst pipe is covered [1][9]."]), retr, router)
    r = c.ask("Is water damage from a burst pipe covered?")
    assert "[9]" not in r.text and r.citations == ["homeowners"]
    c = cap.Copilot(FakeLLM(["Burst pipe damage is covered."]), retr, router)
    assert c.ask("Is water damage from a burst pipe covered?").escalated


def test_budget_trims_sources(cap, cap_data):
    seen = []

    def respond(messages, system, tools):
        seen.append(messages[-1]["content"].count("\n["))  # one "\n[n]" per numbered source
        return LLMResponse(text="Sudden water damage from a burst pipe is covered [1].", input_tokens=100, output_tokens=20)

    c = cap.Copilot(FakeLLM(respond), cap.HybridRetriever(cap.load_corpus(cap_data / "policies")),
                    cap.IntentRouter.from_jsonl(cap_data / "intents.jsonl"), budget_usd=0.0106)
    r = c.ask("Is water damage from a burst pipe covered?")
    assert seen and 1 <= seen[0] < 4 and r.citations == ["homeowners"]
    # a budget too small for even one source abstains instead of calling the model blind
    c.budget_usd = 0.001
    assert c.ask("Is water damage from a burst pipe covered?").abstained and len(seen) == 1
