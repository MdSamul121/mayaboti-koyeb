import subprocess
import sys

import pytest


@pytest.mark.parametrize("first_module", ["mayaboti.goal.command", "mayaboti.command.builtin"])
def test_goal_and_builtin_commands_import_in_either_order(first_module):
    script = f"""
import {first_module}
from mayaboti.goal.command import register_goal_command
from mayaboti.command import CommandRouter, register_builtin_commands

router = CommandRouter()
register_builtin_commands(router)
assert router.is_dispatchable_command('/goal ship it')
standalone = CommandRouter()
register_goal_command(standalone)
assert standalone.is_dispatchable_command('/goal ship it')
"""
    subprocess.run([sys.executable, "-B", "-c", script], check=True)
