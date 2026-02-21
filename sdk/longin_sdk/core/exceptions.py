class LonginError(Exception):
    pass


class ValidationError(LonginError):
    pass


class PermissionError(LonginError):
    pass


class ResourceError(LonginError):
    pass
