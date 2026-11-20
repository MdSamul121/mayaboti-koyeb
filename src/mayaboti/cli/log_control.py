from loguru import logger

__all__ = ["_set_mayaboti_logs"]


def _set_mayaboti_logs(enabled: bool) -> None:
    if enabled:
        logger.enable("mayaboti")
    else:
        logger.disable("mayaboti")
