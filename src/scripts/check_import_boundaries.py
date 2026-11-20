"""Check direct Python imports against the gateway's ownership boundaries."""

from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from importlib.util import resolve_name
from pathlib import Path


@dataclass(frozen=True)
class ImportEdge:
    target: str
    line: int
    type_only: bool = False


@dataclass(frozen=True)
class ImportRule:
    name: str
    sources: tuple[str, ...]
    forbidden: tuple[str, ...]
    type_only_allowed: tuple[str, ...] = ()
    allowed_targets: tuple[str, ...] = ()


@dataclass(frozen=True)
class Violation:
    rule: str
    target: str
    line: int


_ADAPTERS = (
    "mayaboti.channels",
    "mayaboti.cli",
    "mayaboti.gateway",
    "mayaboti.webui",
)

_TOOL_CONFIG_MODULES = (
    "mayaboti.agent.tools.cli_apps_config",
    "mayaboti.agent.tools.filesystem_config",
    "mayaboti.agent.tools.image_generation_config",
    "mayaboti.agent.tools.self_config",
    "mayaboti.agent.tools.shell_config",
    "mayaboti.agent.tools.web_config",
)

IMPORT_RULES = (
    ImportRule(
        "update-policy-direction",
        ("mayaboti.agent", "mayaboti.session", "mayaboti.runtime_admission",
         "mayaboti.data_access", "mayaboti.installation_lock"),
        ("mayaboti.update_service", "mayaboti.update_plan", "mayaboti.update_jobs",
         "mayaboti.update_worker", "mayaboti.update_stop", "mayaboti.update_restart"),
    ),
    ImportRule(
        "update-domain",
        ("mayaboti.update_service", "mayaboti.update_plan", "mayaboti.update_jobs",
         "mayaboti.update_worker", "mayaboti.update_stop",
         "mayaboti.update_profiles", "mayaboti.update_handoff", "mayaboti.update_guidance"),
        ("mayaboti.agent", "mayaboti.session", "mayaboti.cli",
         "mayaboti.channels", "mayaboti.webui"),
    ),
    ImportRule(
        "update-restart-adapter",
        ("mayaboti.update_restart",),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.session"),
        # This protected-startup entry composes the existing CLI, not a second
        # agent runtime. Keep its frozen worker entry and launch semantics stable.
        allowed_targets=("mayaboti.gateway.runtime", "mayaboti.cli.gateway_runtime._run_gateway",
                         "mayaboti.cli.entry.configure_windows_console",
                         "mayaboti.cli.process_identity.set_cli_process_identity",
                         "mayaboti.cli.runtime_config._load_runtime_config"),
    ),
    ImportRule(
        "core-execution",
        ("mayaboti.agent.loop", "mayaboti.agent.runner", "mayaboti.agent.turn_delivery"),
        _ADAPTERS,
        allowed_targets=("mayaboti.channels.notification_routes",),
    ),
    ImportRule(
        "process-execution",
        ("mayaboti.execution.processes", "mayaboti.execution._windows_job"),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.config", "mayaboti.security", "mayaboti.session"),
    ),
    ImportRule(
        "http-execution",
        ("mayaboti.execution.http",),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.config", "mayaboti.providers", "mayaboti.session"),
    ),
    ImportRule(
        "sandbox-execution",
        ("mayaboti.execution.sandbox",),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.config", "mayaboti.session"),
        allowed_targets=("mayaboti.config.paths.get_media_dir",),
    ),
    ImportRule(
        "channel-routing-contracts",
        ("mayaboti.channels.notification_routes",),
        ("mayaboti",),
    ),
    ImportRule(
        "session-storage",
        ("mayaboti.session.manager", "mayaboti.session.history", "mayaboti.session.summary",
         "mayaboti.session.recovery"),
        (*_ADAPTERS, "mayaboti.agent"),
    ),
    ImportRule(
        "security-primitives",
        ("mayaboti.security",),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.execution", "mayaboti.session"),
    ),
    ImportRule(
        "resource-execution",
        ("mayaboti.execution",),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.session"),
    ),
    ImportRule(
        "file-tool-execution",
        ("mayaboti.agent.tools.filesystem", "mayaboti.agent.tools.apply_patch",
         "mayaboti.agent.tools.search", "mayaboti.utils.file_edit_events"),
        ("mayaboti.security", "mayaboti.agent.tools.path_utils", "os", "shutil", "glob"),
    ),
    ImportRule(
        "websocket-transport",
        ("mayaboti.channels.websocket.runtime",),
        (
            "mayaboti.bus.outbound_events",
            "mayaboti.command",
            "mayaboti.runtime_context",
            "mayaboti.security.workspace_access",
            "mayaboti.pairing.events",
            "mayaboti.session.goal_state",
            "mayaboti.session.webui_turns",
            "mayaboti.webui.metadata",
            "mayaboti.webui.outbound_wire",
            "mayaboti.webui.transcript",
            "mayaboti.webui.cli_apps_api",
            "mayaboti.webui.forking",
            "mayaboti.webui.mcp_presets_api",
            "mayaboti.webui.sidebar_state",
            "mayaboti.webui.transcription_ws",
        ),
    ),
    ImportRule(
        "tool-config-base",
        ("mayaboti.agent.tools", "mayaboti.channels"),
        ("mayaboti.config.schema.Base",),
    ),
    ImportRule(
        "configuration-contracts",
        ("mayaboti.config", "mayaboti.config_base"),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.apps", "mayaboti.session"),
        allowed_targets=_TOOL_CONFIG_MODULES,
    ),
    ImportRule(
        "tool-configuration-contracts",
        _TOOL_CONFIG_MODULES,
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.apps", "mayaboti.session", "mayaboti.config"),
        allowed_targets=_TOOL_CONFIG_MODULES,
    ),
    ImportRule(
        "shared-primitives",
        ("mayaboti.utils.file_io", "mayaboti.agent.skill_metadata", "mayaboti.providers.generation",
         "mayaboti.llm_usage.types", "mayaboti.session.automation_spec"),
        (*_ADAPTERS, "mayaboti.agent", "mayaboti.apps", "mayaboti.session", "mayaboti.config"),
    ),
    ImportRule(
        "oauth-catalog-cache",
        ("mayaboti.providers.oauth_catalog_cache",),
        ("mayaboti.providers.oauth_model_catalog", "mayaboti.providers.openai_codex_provider",
         "mayaboti.providers.github_copilot_provider", "mayaboti.providers.xai_grok_provider"),
    ),
)


def _within(name: str, prefix: str) -> bool:
    return name == prefix or name.startswith(prefix + ".")


def _qualified_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_qualified_name(node.value)}.{node.attr}"
    return ""


def _argument(call: ast.Call, position: int, name: str) -> ast.expr | None:
    if len(call.args) > position:
        return call.args[position]
    return next((keyword.value for keyword in call.keywords if keyword.arg == name), None)


def _literal_string(node: ast.expr | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


class ImportCollector(ast.NodeVisitor):
    """Resolve static imports and literal dynamic imports without loading modules."""

    def __init__(self, tree: ast.Module, module: str, *, is_package: bool = False) -> None:
        self.package = module if is_package else module.rpartition(".")[0]
        self.edges: list[ImportEdge] = []
        self.type_only = False
        self.type_guards: set[str] = set()
        self.import_module_calls: set[str] = set()
        self.builtin_import_calls = {"__import__"}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    binding = alias.asname or alias.name
                    if alias.name == "importlib":
                        self.import_module_calls.add(f"{binding}.import_module")
                    elif alias.name == "typing":
                        self.type_guards.add(f"{binding}.TYPE_CHECKING")
                    elif alias.name == "builtins":
                        self.builtin_import_calls.add(f"{binding}.__import__")
            elif isinstance(node, ast.ImportFrom) and not node.level:
                for alias in node.names:
                    binding = alias.asname or alias.name
                    if node.module == "importlib" and alias.name == "import_module":
                        self.import_module_calls.add(binding)
                    elif node.module == "typing" and alias.name == "TYPE_CHECKING":
                        self.type_guards.add(binding)
                    elif node.module == "builtins" and alias.name == "__import__":
                        self.builtin_import_calls.add(binding)

    def _add(self, target: str, line: int) -> None:
        if _within(target, "mayaboti"):
            self.edges.append(ImportEdge(target, line, self.type_only))

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._add(alias.name, node.lineno)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if node.level:
            module = resolve_name("." * node.level + module, self.package)
        for alias in node.names:
            target = module if alias.name == "*" else f"{module}.{alias.name}"
            self._add(target, node.lineno)

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        previous = self.type_only
        self.type_only = previous or _qualified_name(node.test) in self.type_guards
        for statement in node.body:
            self.visit(statement)
        self.type_only = previous
        for statement in node.orelse:
            self.visit(statement)

    def visit_Call(self, node: ast.Call) -> None:
        name = _qualified_name(node.func)
        target = _literal_string(_argument(node, 0, "name"))
        if target is not None and name in self.import_module_calls:
            if target.startswith("."):
                package_arg = _argument(node, 1, "package")
                package = _literal_string(package_arg)
                if isinstance(package_arg, ast.Name) and package_arg.id == "__package__":
                    package = self.package
                if package is not None:
                    self._add(resolve_name(target, package), node.lineno)
            else:
                self._add(target, node.lineno)
        elif target is not None and name in self.builtin_import_calls:
            level = _argument(node, 4, "level")
            if level is None or (isinstance(level, ast.Constant) and level.value == 0):
                self._add(target, node.lineno)
        self.generic_visit(node)


def find_violations(
    source: str, module: str, *, is_package: bool = False,
) -> list[Violation]:
    tree = ast.parse(source, filename=module)
    collector = ImportCollector(tree, module, is_package=is_package)
    collector.visit(tree)
    violations: list[Violation] = []
    for rule in IMPORT_RULES:
        if not any(_within(module, prefix) for prefix in rule.sources):
            continue
        for edge in collector.edges:
            if edge.type_only and edge.target in rule.type_only_allowed:
                continue
            if any(_within(edge.target, prefix) for prefix in rule.allowed_targets):
                continue
            if any(_within(edge.target, prefix) for prefix in rule.forbidden):
                violations.append(Violation(rule.name, edge.target, edge.line))
    return violations


def check_repository(root: Path) -> tuple[int, list[str]]:
    checked = 0
    violations: list[str] = []
    for path in sorted((root / "mayaboti").rglob("*.py")):
        relative = path.relative_to(root)
        if "tests" in relative.parts:
            continue
        parts = relative.with_suffix("").parts
        is_package = parts[-1] == "__init__"
        module = ".".join(parts[:-1] if is_package else parts)
        if not any(
            _within(module, prefix) for rule in IMPORT_RULES for prefix in rule.sources
        ):
            continue
        checked += 1
        for violation in find_violations(
            path.read_text(encoding="utf-8"), module, is_package=is_package,
        ):
            violations.append(
                f"{relative.as_posix()}:{violation.line}: [{violation.rule}] "
                f"must not import {violation.target}"
            )
    return checked, violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1],
        help="repository root containing mayaboti/",
    )
    args = parser.parse_args()
    if not (args.root / "mayaboti").is_dir():
        parser.error(f"{args.root} does not contain mayaboti/")
    checked, violations = check_repository(args.root)
    if checked == 0:
        parser.error(f"{args.root} contains no protected Python modules")
    if violations:
        for violation in violations:
            print(violation, file=sys.stderr)
        return 1
    print(f"Import boundaries passed ({len(IMPORT_RULES)} rules, {checked} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
