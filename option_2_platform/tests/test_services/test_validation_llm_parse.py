from types import SimpleNamespace

from src.services.validation_service import validation_service


class DummyLLM:
    def __init__(self, answers):
        self.answers = list(answers)

    def query(self, question, metadata_filter=None, system_prompt=None):
        # pop next answer; if exhausted, repeat last
        ans = self.answers.pop(0) if self.answers else self.answers[-1]
        return {"answer": ans, "citations": []}


def _criterion(prompt="Prompt"):
    return SimpleNamespace(id="KX", name="Dummy", prompt=prompt, lang=None, kurz=None)


def test_llm_eval_truncates_and_normalizes():
    long_reason = "R" * 300
    answer = '{"status": "green", "begründung": "' + long_reason + '", "dokument": "a.pdf", "referenz": "S1"}'
    llm = DummyLLM([answer])
    result = validation_service._llm_eval("p1", _criterion(), llm)
    assert result["status"] == "grün"
    assert len(result["reason"]) == 160


def test_llm_eval_retries_and_sets_warning_on_invalid():
    llm = DummyLLM(["not-json", '{"status": "rot", "begründung": "fail"}'])
    result = validation_service._llm_eval("p1", _criterion(), llm)
    assert result["status"] == "rot"
    assert "fail" in result["reason"]
