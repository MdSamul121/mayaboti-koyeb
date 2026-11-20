from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mayaboti.agent.tools.base import Schema, Tool, ToolResult, tool_parameters
    from mayaboti.agent.tools.context import ToolContext
    from mayaboti.agent.tools.loader import ToolLoader
    from mayaboti.agent.tools.registry import ToolRegistry
    from mayaboti.agent.tools.schema import (
        ArraySchema,
        BooleanSchema,
        IntegerSchema,
        NumberSchema,
        ObjectSchema,
        StringSchema,
        tool_parameters_schema,
    )


_EXPORTS = {
    "Schema": "mayaboti.agent.tools.base",
    "ArraySchema": "mayaboti.agent.tools.schema",
    "BooleanSchema": "mayaboti.agent.tools.schema",
    "IntegerSchema": "mayaboti.agent.tools.schema",
    "NumberSchema": "mayaboti.agent.tools.schema",
    "ObjectSchema": "mayaboti.agent.tools.schema",
    "StringSchema": "mayaboti.agent.tools.schema",
    "Tool": "mayaboti.agent.tools.base",
    "ToolContext": "mayaboti.agent.tools.context",
    "ToolLoader": "mayaboti.agent.tools.loader",
    "ToolResult": "mayaboti.agent.tools.base",
    "ToolRegistry": "mayaboti.agent.tools.registry",
    "tool_parameters": "mayaboti.agent.tools.base",
    "tool_parameters_schema": "mayaboti.agent.tools.schema",
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
    "Schema",
    "ArraySchema",
    "BooleanSchema",
    "IntegerSchema",
    "NumberSchema",
    "ObjectSchema",
    "StringSchema",
    "Tool",
    "ToolContext",
    "ToolLoader",
    "ToolResult",
    "ToolRegistry",
    "tool_parameters",
    "tool_parameters_schema",
]
