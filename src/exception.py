class TTSError(Exception):
    def __init__(self, title: str, message: str) -> None:
        super().__init__(message)
        self.title = title
        self.message = message
