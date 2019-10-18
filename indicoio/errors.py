class IndicoIPAError(Exception):
    pass


class IndicoRequestError(IndicoIPAError):
    def __init__(self, error, code, extras=None):
        super().__init__(f"Status: {code}, Error: {error}\n\tExtras: {extras}")


class IndicoDecodingError(IndicoIPAError):
    def __init__(self, mime, charset, content):
        super().__init__(f"Failed to decode with {mime}:{charset}. Content {content}")


class IndicoInputError(IndicoIPAError):
    def __init__(self, msg):
        super().__init__(error=msg, code=400)
