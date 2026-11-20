from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_import_boundaries import Violation, find_violations


@pytest.mark.parametrize("module", [
    "mayaboti.agent.loop", "mayaboti.session.state", "mayaboti.runtime_admission",
    "mayaboti.data_access", "mayaboti.installation_lock",
])
def test_runtime_owners_do_not_depend_on_update_policy(module: str) -> None:
    assert find_violations("from mayaboti.update_service import UpdateService", module) == [
        Violation("update-policy-direction", "mayaboti.update_service.UpdateService", 1),
    ]


def test_updater_uses_process_contracts_not_agent_or_client_implementations() -> None:
    assert find_violations("from mayaboti.agent.loop import AgentLoop", "mayaboti.update_stop") == [
        Violation("update-domain", "mayaboti.agent.loop.AgentLoop", 1),
    ]
    assert find_violations(
        "from mayaboti.gateway.runtime import GatewayRuntime", "mayaboti.update_stop",
    ) == []
    assert find_violations(
        "from mayaboti.update_stop import watch_gateway_stop", "mayaboti.cli.gateway_runtime",
    ) == []
    assert find_violations(
        "from mayaboti.cli.gateway_runtime import _run_gateway", "mayaboti.update_restart",
    ) == []
    assert find_violations(
        "from mayaboti.agent.loop import AgentLoop", "mayaboti.update_restart",
    ) == [Violation("update-restart-adapter", "mayaboti.agent.loop.AgentLoop", 1)]


@pytest.mark.parametrize(
    ("source", "target", "line"),
    [
        ("import mayaboti.webui.metadata", "mayaboti.webui.metadata", 1),
        ("from mayaboti import webui", "mayaboti.webui", 1),
        ("from mayaboti.webui import metadata", "mayaboti.webui.metadata", 1),
        ("from .. import webui", "mayaboti.webui", 1),
        ("from ..webui import metadata", "mayaboti.webui.metadata", 1),
        (
            "def load():\n    from mayaboti.cli import gateway",
            "mayaboti.cli.gateway", 2,
        ),
        (
            "import importlib\nimportlib.import_module('mayaboti.webui.metadata')",
            "mayaboti.webui.metadata", 2,
        ),
        (
            "import importlib as modules\n"
            "modules.import_module(name='mayaboti.webui.metadata')",
            "mayaboti.webui.metadata", 2,
        ),
        (
            "from importlib import import_module as load\n"
            "load('..webui.metadata', __package__)",
            "mayaboti.webui.metadata", 2,
        ),
        (
            "from importlib import import_module\n"
            "import_module('..webui.metadata', package='mayaboti.agent')",
            "mayaboti.webui.metadata", 2,
        ),
        ("__import__('mayaboti.webui.metadata')", "mayaboti.webui.metadata", 1),
        (
            "import builtins as imports\nimports.__import__('mayaboti.webui.metadata')",
            "mayaboti.webui.metadata", 2,
        ),
    ],
)
def test_core_rejects_adapter_imports_in_supported_spellings(
    source: str, target: str, line: int,
) -> None:
    assert find_violations(source, "mayaboti.agent.loop") == [
        Violation("core-execution", target, line),
    ]


@pytest.mark.parametrize(
    "source",
    [
        "from typing import TYPE_CHECKING as TC\n"
        "if TC:\n    from mayaboti.webui import metadata",
        "import typing as t\n"
        "if t.TYPE_CHECKING:\n    from mayaboti.webui import metadata",
    ],
)
def test_core_boundary_includes_type_dependencies(source: str) -> None:
    assert find_violations(source, "mayaboti.agent.runner") == [
        Violation("core-execution", "mayaboti.webui.metadata", 3),
    ]


@pytest.mark.parametrize(
    ("module", "rule"),
    [
        ("mayaboti.session.manager", "session-storage"),
        ("mayaboti.session.recovery", "session-storage"),
        ("mayaboti.security.workspace_policy", "security-primitives"),
        ("mayaboti.agent.turn_delivery", "core-execution"),
        ("mayaboti.channels.notification_routes", "channel-routing-contracts"),
        ("mayaboti.config.schema", "configuration-contracts"),
        ("mayaboti.agent.tools.cli_apps_config", "tool-configuration-contracts"),
        ("mayaboti.utils.file_io", "shared-primitives"),
    ],
)
def test_storage_and_security_do_not_depend_on_adapters(module: str, rule: str) -> None:
    assert find_violations("from mayaboti.cli import gateway", module) == [
        Violation(rule, "mayaboti.cli.gateway", 1),
    ]


@pytest.mark.parametrize(
    "dependency",
    [
        "mayaboti.bus.outbound_events.ProgressEvent",
        "mayaboti.command.router",
        "mayaboti.pairing.events.PairingChanged",
        "mayaboti.session.webui_turns.clear_websocket_turn_if_current",
        "mayaboti.webui.transcript.WebUITranscriptRecorder",
        "mayaboti.webui.outbound_wire.project_notification",
    ],
)
def test_websocket_transport_leaves_event_and_history_policy_to_delivery(dependency: str) -> None:
    module, name = dependency.rsplit(".", 1)
    source = f"from {module} import {name}\n"
    assert find_violations(source, "mayaboti.channels.websocket.runtime") == [
        Violation("websocket-transport", dependency, 1),
    ]
    assert find_violations(source, "mayaboti.webui.outbound_delivery") == []


@pytest.mark.parametrize(
    "source",
    [
        "from mayaboti.config.schema import Base",
        "from ...config.schema import Base as ConfigBase",
    ],
)
def test_tool_configs_import_the_shared_base_directly(source: str) -> None:
    assert find_violations(source, "mayaboti.agent.tools.shell") == [
        Violation("tool-config-base", "mayaboti.config.schema.Base", 1),
    ]
    assert find_violations(
        "from mayaboti.config_base import Base", "mayaboti.agent.tools.shell",
    ) == []


def test_configuration_imports_the_six_tool_owned_config_contracts() -> None:
    source = (
        "from mayaboti.agent.tools.cli_apps_config import CliAppsToolConfig\n"
        "from mayaboti.agent.tools.filesystem_config import FileToolsConfig\n"
        "from mayaboti.agent.tools.image_generation_config import ImageGenerationToolConfig\n"
        "from mayaboti.agent.tools.self_config import MyToolConfig\n"
        "from mayaboti.agent.tools.shell_config import ExecToolConfig\n"
        "from mayaboti.agent.tools.web_config import WebToolsConfig\n"
    )
    assert find_violations(source, "mayaboti.config.schema") == []


@pytest.mark.parametrize(
    ("module", "source"),
    [
        ("mayaboti.agent.loop", "from mayaboti.session.recovery import RecoveryAdmission"),
        ("mayaboti.session.manager", "from mayaboti.providers.base import ProviderConversationState"),
        ("mayaboti.session.webui_turns", "from mayaboti.webui import transcript"),
        ("mayaboti.cli.gateway_runtime", "from mayaboti.agent.loop import AgentLoop"),
        ("mayaboti.channels.websocket.runtime", "from mayaboti.webui import inbound_commands"),
        ("mayaboti.agent.tools.cli_apps_config", "from mayaboti.config_base import Base"),
        (
            "mayaboti.agent.turn_delivery",
            "from mayaboti.channels.notification_routes import notification_metadata",
        ),
    ],
)
def test_existing_runtime_and_composition_dependencies_remain_allowed(
    module: str, source: str,
) -> None:
    assert find_violations(source, module) == []


@pytest.mark.parametrize(
    ("relative", "source", "rule", "target", "line"),
    [
        (
            "mayaboti/agent/runner.py", "import mayaboti.webui.metadata",
            "core-execution", "mayaboti.webui.metadata", 1,
        ),
        (
            "mayaboti/agent/loop.py",
            "import importlib\nif importlib.import_module('mayaboti.webui.metadata'):\n    pass",
            "core-execution", "mayaboti.webui.metadata", 2,
        ),
        (
            "mayaboti/agent/loop.py", "if __import__('mayaboti.webui.metadata'):\n    pass",
            "core-execution", "mayaboti.webui.metadata", 1,
        ),
        (
            "mayaboti/session/manager.py", "from mayaboti.cli import gateway",
            "session-storage", "mayaboti.cli.gateway", 1,
        ),
        (
            "mayaboti/channels/notification_routes.py",
            "from mayaboti.channels.slack.runtime import SlackChannel",
            "channel-routing-contracts", "mayaboti.channels.slack.runtime.SlackChannel", 1,
        ),
        (
            "mayaboti/channels/notification_routes.py",
            "from mayaboti.agent.turn_delivery import TurnRoute",
            "channel-routing-contracts", "mayaboti.agent.turn_delivery.TurnRoute", 1,
        ),
        (
            "mayaboti/security/__init__.py", "from ..cli import gateway",
            "security-primitives", "mayaboti.cli.gateway", 1,
        ),
        (
            "mayaboti/channels/websocket/runtime.py",
            "import importlib as modules\nmodules.import_module('mayaboti.command.router')",
            "websocket-transport", "mayaboti.command.router", 2,
        ),
        (
            "mayaboti/agent/tools/shell.py", "from ...config.schema import Base as ConfigBase",
            "tool-config-base", "mayaboti.config.schema.Base", 1,
        ),
        (
            "mayaboti/channels/telegram/runtime.py", "from mayaboti.config.schema import Base",
            "tool-config-base", "mayaboti.config.schema.Base", 1,
        ),
        (
            "mayaboti/config/schema.py", "from mayaboti.agent.tools.shell import ExecTool",
            "configuration-contracts", "mayaboti.agent.tools.shell.ExecTool", 1,
        ),
        (
            "mayaboti/agent/tools/cli_apps_config.py", "from .cli_apps import CliAppsTool",
            "tool-configuration-contracts", "mayaboti.agent.tools.cli_apps.CliAppsTool", 1,
        ),
        (
            "mayaboti/agent/tools/web_config.py", "from mayaboti.config.schema import Config",
            "tool-configuration-contracts", "mayaboti.config.schema.Config", 1,
        ),
        (
            "mayaboti/providers/oauth_catalog_cache.py",
            "from mayaboti.providers import openai_codex_provider",
            "oauth-catalog-cache", "mayaboti.providers.openai_codex_provider", 1,
        ),
    ],
)
def test_cli_rejects_a_violation_and_reports_its_source_location(
    tmp_path: Path, relative: str, source: str, rule: str, target: str, line: int,
) -> None:
    path = tmp_path / relative
    path.parent.mkdir(parents=True)
    path.write_text(source + "\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_import_boundaries", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stderr.strip() == f"{relative}:{line}: [{rule}] must not import {target}"


def test_cli_accepts_a_tool_owned_config_import(tmp_path: Path) -> None:
    path = tmp_path / "mayaboti/config/schema.py"
    path.parent.mkdir(parents=True)
    path.write_text(
        "from mayaboti.agent.tools.cli_apps_config import CliAppsToolConfig\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-m", "scripts.check_import_boundaries", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
