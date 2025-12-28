class BCAMError(Exception):
    pass


UnknownPositionError = BCAMError("Delta from unknown coordinate is not possible")
