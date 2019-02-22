class NsValueIsNotDict(Exception):
    """Raised when the value of the ns topic is not dict"""
    pass


class NsUuidDoesNotExist(Exception):
    """Raised when the ns uuid key is not included in the value of the message in topic ns"""
    pass
