from crypto_claw_engine.llm import FakeLLM, LLMClient


def test_fake_llm_returns_canned_response():
    llm = FakeLLM({"technicals": "Scripted technicals rationale"})
    out = llm.complete(
        messages=[{"role": "user", "content": "anything"}],
        tag="technicals",
    )
    assert out == "Scripted technicals rationale"


def test_fake_llm_default_fallback():
    llm = FakeLLM()
    out = llm.complete(
        messages=[{"role": "user", "content": "anything"}],
        tag="unknown-agent",
    )
    assert "fake" in out.lower()


def test_fake_llm_records_calls():
    llm = FakeLLM()
    llm.complete(messages=[{"role": "user", "content": "hi"}], tag="x")
    llm.complete(messages=[{"role": "user", "content": "hi"}], tag="y")
    assert len(llm.calls) == 2
    assert llm.calls[0]["tag"] == "x"


def test_llm_client_protocol_shape():
    llm: LLMClient = FakeLLM()
    assert hasattr(llm, "complete")
