from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mayaboti.agent.context import ContextBuilder
    from mayaboti.agent.hook import (
        AgentHook,
        AgentHookContext,
        AgentRunHookContext,
        AgentTurnHookContext,
        AgentTurnHookFactory,
        CompositeHook,
    )
    from mayaboti.agent.loop import AgentLoop
    from mayaboti.agent.memory import MemoryStore
    from mayaboti.agent.skills import SkillsLoader
    from mayaboti.agent.subagent import SubagentManager


_EXPORTS = {
    "AgentHook": "mayaboti.agent.hook",
    "AgentHookContext": "mayaboti.agent.hook",
    "AgentRunHookContext": "mayaboti.agent.hook",
    "AgentTurnHookContext": "mayaboti.agent.hook",
    "AgentTurnHookFactory": "mayaboti.agent.hook",
    "AgentLoop": "mayaboti.agent.loop",
    "CompositeHook": "mayaboti.agent.hook",
    "ContextBuilder": "mayaboti.agent.context",
    "MemoryStore": "mayaboti.agent.memory",
    "SkillsLoader": "mayaboti.agent.skills",
    "SubagentManager": "mayaboti.agent.subagent",
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
    "AgentHook",
    "AgentHookContext",
    "AgentRunHookContext",
    "AgentTurnHookContext",
    "AgentTurnHookFactory",
    "AgentLoop",
    "CompositeHook",
    "ContextBuilder",
    "MemoryStore",
    "SkillsLoader",
    "SubagentManager",
]
