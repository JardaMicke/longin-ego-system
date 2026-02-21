class LonginError(Exception):
    """Účel: Základní výjimka SDK.

    Vstupy/Výstupy: Dědí z Exception.
    Vedlejší efekty: Žádné.
    """
    pass


class ValidationError(LonginError):
    """Účel: Vyhazuje se při validačních chybách.

    Vstupy/Výstupy: Dědí z LonginError.
    Vedlejší efekty: Žádné.
    """
    pass


class PermissionError(LonginError):
    """Účel: Vyhazuje se při porušení bezpečnostních pravidel.

    Vstupy/Výstupy: Dědí z LonginError.
    Vedlejší efekty: Žádné.
    """
    pass


class ResourceError(LonginError):
    """Účel: Vyhazuje se při nedostatku zdrojů.

    Vstupy/Výstupy: Dědí z LonginError.
    Vedlejší efekty: Žádné.
    """
    pass
