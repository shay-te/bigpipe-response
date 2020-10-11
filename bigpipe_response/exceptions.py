
class InvalidConfiguration(Exception):
    """bigpipe is somehow improperly configured"""
    pass


class JavascriptParseException(Exception):
    def __init__(self, message, errors):
        super(JavascriptParseException, self).__init__(message)
        self.errors = errors
