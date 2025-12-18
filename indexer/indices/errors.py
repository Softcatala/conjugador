class IndexationError(Exception):  # noqa: D101
    def __init__(self, message: str) -> None:  # noqa: D107
        super().__init__(message)
