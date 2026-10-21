COO = "We need an AI that makes support faster and better for all our customers, ideally real-time, soon."


def test_vague_terms_in_order(impl):
    a = impl.analyze(COO)
    assert a.vague_terms == ["faster", "better", "all", "real-time", "soon"]


def test_missing_dimensions(impl):
    a = impl.analyze(COO)
    # "customers" pins down users; nothing else is specified
    assert a.missing == ["metric", "data", "deadline", "volume"]


def test_questions_and_assumptions(impl):
    a = impl.analyze(COO)
    assert a.questions[0] == impl.QUESTIONS["metric"]
    assert a.questions[4] == 'What does "faster" mean in measurable terms?'
    assert len(a.questions) == 4 + 5
    assert a.assumptions == [impl.DEFAULT_ASSUMPTIONS[d] for d in a.missing]


def test_well_specified_request(impl):
    req = ("Cut average handle time for our 40 support agents from 11 min to 7 min using Zendesk tickets "
           "and help-center documents by 2026-12-01; volume is about 3000 tickets per day.")
    a = impl.analyze(req)
    assert a.missing == [] and a.vague_terms == [] and a.questions == []


def test_quarter_and_month_count_as_deadline(impl):
    assert "deadline" not in impl.analyze("live in Q3 please").missing
    assert "deadline" not in impl.analyze("before March").missing


def test_whole_words_only(impl):
    # "overall" and "smartphone" must not match "all"/"smart"
    assert impl.analyze("overall smartphone usage").vague_terms == []
