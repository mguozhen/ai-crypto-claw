class EngineError(Exception):
    """Base class for engine errors."""


class DataGap(EngineError):
    """Raised when a data source cannot supply required data for an agent."""

    def __init__(self, source: str, key: str, reason: str = ""):
        self.source = source
        self.key = key
        self.reason = reason
        super().__init__(f"data gap: {source}/{key} ({reason})")


class AgentFailure(EngineError):
    """Raised when an agent fails after retries."""
