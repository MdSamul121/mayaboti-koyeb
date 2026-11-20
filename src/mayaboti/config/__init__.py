from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mayaboti.config.errors import ConfigIssue, ConfigLoadError
    from mayaboti.config.loader import get_config_path, load_config
    from mayaboti.config.paths import (
        get_cli_history_path,
        get_cron_dir,
        get_data_dir,
        get_legacy_sessions_dir,
        get_logs_dir,
        get_media_dir,
        get_runtime_subdir,
        get_webui_dir,
        get_workspace_path,
        is_default_workspace,
    )
    from mayaboti.config.schema import Config


_EXPORTS = {
    "Config": "mayaboti.config.schema",
    "ConfigIssue": "mayaboti.config.errors",
    "ConfigLoadError": "mayaboti.config.errors",
    "load_config": "mayaboti.config.loader",
    "get_config_path": "mayaboti.config.loader",
    "get_data_dir": "mayaboti.config.paths",
    "get_runtime_subdir": "mayaboti.config.paths",
    "get_media_dir": "mayaboti.config.paths",
    "get_cron_dir": "mayaboti.config.paths",
    "get_logs_dir": "mayaboti.config.paths",
    "get_webui_dir": "mayaboti.config.paths",
    "get_workspace_path": "mayaboti.config.paths",
    "is_default_workspace": "mayaboti.config.paths",
    "get_cli_history_path": "mayaboti.config.paths",
    "get_legacy_sessions_dir": "mayaboti.config.paths",
}


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_EXPORTS))


__all__ = [
    "Config",
    "ConfigIssue",
    "ConfigLoadError",
    "load_config",
    "get_config_path",
    "get_data_dir",
    "get_runtime_subdir",
    "get_media_dir",
    "get_cron_dir",
    "get_logs_dir",
    "get_webui_dir",
    "get_workspace_path",
    "is_default_workspace",
    "get_cli_history_path",
    "get_legacy_sessions_dir",
]
