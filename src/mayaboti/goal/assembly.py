"""Assemble the built-in sustained-goal feature at application entrypoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mayaboti.goal.command import register_goal_command
from mayaboti.goal.runtime import GOAL_GENERATION_VOLATILE_KEYS, GoalExecutionPolicy
from mayaboti.goal.tools import CreateGoalTool, UpdateGoalTool

if TYPE_CHECKING:
    from mayaboti.agent.tools.registry import ToolRegistry
    from mayaboti.bus.queue import MessageBus
    from mayaboti.command.router import CommandRouter
    from mayaboti.session.manager import SessionManager


def install_goal(
    sessions: SessionManager, bus: MessageBus, tools: ToolRegistry, commands: CommandRouter,
) -> GoalExecutionPolicy:
    register_goal_command(commands)
    sessions.exclude_generation_metadata(GOAL_GENERATION_VOLATILE_KEYS)
    for tool in (CreateGoalTool.bind(sessions, bus), UpdateGoalTool.bind(sessions, bus)):
        if not tools.has(tool.name):
            tools.register(tool)
    return GoalExecutionPolicy(sessions.state)
