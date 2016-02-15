class AppNotConfigured(Exception):
    def __init__(self, message):
        super().__init__(message)


class AppException(Exception):
    def __init__(self, message):
        super().__init__(message)
