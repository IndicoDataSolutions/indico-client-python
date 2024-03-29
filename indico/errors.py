from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from typing import Any


class IndicoError(Exception):
    pass


class IndicoRequestError(IndicoError):
    def __init__(self, error: str, code: int, extras: dict[str, "Any"] | None = None):
        super().__init__(f"Status: {code}, Error: {error}\n\tExtras: {extras}")


class IndicoTimeoutError(IndicoError):
    def __init__(self, duration: int | float):
        super().__init__(f"Request timed out after {duration:0.3f} seconds.")


class IndicoDecodingError(IndicoError):
    def __init__(self, mime: str, charset: str, content: str):
        super().__init__(f"Failed to decode with {mime}:{charset}. Content {content}")


class IndicoInputError(IndicoError):
    def __init__(self, msg: str):
        super().__init__(msg)


class IndicoInvalidConfigSetting(IndicoError):
    def __init__(
        self,
        setting_name: str,
    ):
        super().__init__(f"{setting_name} is not a valid configuration setting")


class IndicoNotFound(IndicoError):
    def __init__(self, cls: str):
        super().__init__(f"Could not find {cls}")


class IndicoAuthenticationFailed(IndicoError):
    def __init__(self) -> None:
        super().__init__("Failed to authenticate")


class IndicoHibernationError(IndicoError):
    def __init__(self, after: int):
        self.after: int = after
        super().__init__(
            f"Platform is currently hibernating. Wait {after} seconds and retry this request."
        )
