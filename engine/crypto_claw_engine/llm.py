from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def complete(
        self,
        messages: list[dict],
        *,
        tag: str = "",
        model: str | None = None,
    ) -> str:
        ...


class FakeLLM:
    """Deterministic LLM used in tests and the today-only CLI default.

    Returns a scripted rationale keyed by `tag` (agent name). Falls back to a
    generic sentence that includes the tag so agents can still produce human-
    readable output without any API cost.
    """

    def __init__(self, scripts: dict[str, str] | None = None):
        self.scripts = scripts or {}
        self.calls: list[dict] = []

    def complete(
        self,
        messages: list[dict],
        *,
        tag: str = "",
        model: str | None = None,
    ) -> str:
        self.calls.append({"messages": messages, "tag": tag, "model": model})
        if tag in self.scripts:
            return self.scripts[tag]
        return f"[fake-llm:{tag or 'default'}] synthesized rationale based on evidence."
