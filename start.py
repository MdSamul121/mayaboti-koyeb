import json
import os
import secrets
import shutil
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _parse_bool(raw: str, default: bool = True) -> bool:
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() in ("1", "true", "yes", "on")


def _first_env(*names: str) -> str:
    for name in names:
        val = (os.getenv(name) or "").strip()
        if val:
            return val
    return ""


def _select_model_and_provider(providers: dict) -> tuple[str, str]:
    explicit_model = _first_env("MAYABOTI_MODEL", "NANOBOT_MODEL")
    explicit_provider = _first_env("MAYABOTI_PROVIDER", "NANOBOT_PROVIDER")
    if explicit_model:
        if explicit_model.startswith("groq/"):
            return explicit_model[len("groq/"):], (explicit_provider or "groq")
        if explicit_model.startswith("gemini/"):
            return explicit_model[len("gemini/"):], (explicit_provider or "gemini")
        return explicit_model, (explicit_provider or "auto")
    if "groq" in providers:
        return "qwen/qwen3.8-27b", "groq"
    if "gemini" in providers:
        return "gemini-3.1-flash-lite", "gemini"
    if "openrouter" in providers:
        return "openrouter/free", "openrouter"
    if "nvidia" in providers:
        return "minimaxai/minimax-m3.1-flash", "nvidia"
    return "qwen/qwen3.8-27b", "groq"


def build_mayaboti_config() -> tuple[Path, dict]:
    home_dir = Path(os.path.expanduser("~"))
    mayaboti_dir = home_dir / ".mayaboti"
    workspace_dir = mayaboti_dir / "workspace"
    mayaboti_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir.mkdir(parents=True, exist_ok=True)

    groq_key = _first_env("GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3", "GROQ_API_KEY_4", "GROQ_API_KEY_5")
    openrouter_key = _first_env("OPENROUTER_API_KEY", "OPENROUTER_API_KEY_3")
    nvidia_key = _first_env("NVIDIA_API_KEY")
    gemini_key = _first_env("GOOGLE_API_KEY_5", "GOOGLE_API_KEY_11", "GEMINI_API_KEY", "GEMINI_API_KEY_2")
    hf_key = _first_env("HUGGINGFACE_API_KEY", "HF_TOKEN")

    providers: dict[str, dict] = {}
    if groq_key:
        providers["groq"] = {"apiKey": groq_key}
    if openrouter_key:
        providers["openrouter"] = {"apiKey": openrouter_key}
    if nvidia_key:
        providers["nvidia"] = {"apiKey": nvidia_key}
    if gemini_key:
        providers["gemini"] = {"apiKey": gemini_key}
    if hf_key:
        providers["huggingface"] = {"apiKey": hf_key}

    selected_model, selected_provider = _select_model_and_provider(providers)

    fallback_candidates = []
    if "groq" in providers:
        fallback_candidates.append({"model": "qwen/qwen3.8-27b", "provider": "groq"})
        fallback_candidates.append({"model": "openai/gpt-oss-120b", "provider": "groq"})
    if "gemini" in providers:
        fallback_candidates.append({"model": "gemini-3.1-flash-lite", "provider": "gemini"})
        fallback_candidates.append({"model": "gemini-3-flash-preview", "provider": "gemini"})
    if "openrouter" in providers:
        fallback_candidates.append({"model": "nvidia/nemotron-3.5-super-vl:free", "provider": "openrouter"})
        fallback_candidates.append({"model": "openrouter/free", "provider": "openrouter"})
    if "nvidia" in providers:
        fallback_candidates.append({"model": "minimaxai/minimax-m3.1-flash", "provider": "nvidia"})

    fallback_models = [
        candidate
        for candidate in fallback_candidates
        if (candidate["model"], candidate["provider"]) != (selected_model, selected_provider)
    ]

    tg_token = _first_env("TELEGRAM_BOT_TOKEN")
    raw_allow = _first_env("TELEGRAM_ALLOW_FROM", "ADMIN_ID")
    allow_from = [item.strip() for item in raw_allow.split(",") if item.strip()]

    raw_port = _first_env("MAYABOTI_WEBUI_PORT", "PORT", "SERVER_PORT") or "8080"
    try:
        port = int(raw_port)
    except ValueError:
        port = 8080

    web_token = _first_env("MAYABOTI_WEB_TOKEN", "NANOBOT_WEB_TOKEN")
    if not web_token:
        web_token = secrets.token_urlsafe(24)
        os.environ["MAYABOTI_WEB_TOKEN"] = web_token
        print("ℹ️ MAYABOTI_WEB_TOKEN was not set; generated an ephemeral WebUI secret for this session.")

    config = {
        "agents": {
            "defaults": {
                "workspace": str(workspace_dir),
                "model": selected_model,
                "provider": selected_provider,
                "fallbackModels": fallback_models,
                "maxTokens": 4096,
                "temperature": 0.7,
                "maxToolIterations": 15,
                "timezone": "Asia/Dhaka",
                "timezoneMode": "manual",
                "botName": "Mayaboti",
            }
        },
        "providers": providers,
        "channels": {
            "websocket": {
                "enabled": True,
                "host": "0.0.0.0",
                "port": port,
                "tokenIssueSecret": web_token,
                "websocketRequiresToken": True,
            },
            "telegram": {
                "enabled": bool(tg_token),
                "token": tg_token,
                "allowFrom": allow_from,
            },
        },
        "gateway": {
            "host": "127.0.0.1",
            "port": 18790,
        },
        "tools": {
            "restrictToWorkspace": _parse_bool(os.getenv("RESTRICT_TO_WORKSPACE"), default=True)
        },
    }

    config_path = mayaboti_dir / "config.json"
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    try:
        os.chmod(config_path, 0o600)
    except OSError:
        pass

    return config_path, config


def main():
    config_path, config = build_mayaboti_config()
    model = config["agents"]["defaults"]["model"]
    provider = config["agents"]["defaults"]["provider"]
    web_port = config["channels"]["websocket"]["port"]
    providers_loaded = list(config["providers"].keys())
    fallbacks_count = len(config["agents"]["defaults"]["fallbackModels"])
    tg_enabled = config["channels"]["telegram"]["enabled"]

    print(
        f"✅ Mayaboti config ready at {config_path} | provider={provider} | model={model} | "
        f"providers={providers_loaded} | fallbacks={fallbacks_count} | "
        f"telegram={tg_enabled} | webui_port={web_port}"
    )

    if "--dry-run" in sys.argv:
        return

    mayaboti_bin = shutil.which("mayaboti")
    if mayaboti_bin:
        os.execvp(mayaboti_bin, [mayaboti_bin, "gateway"])
    else:
        os.execvp(sys.executable, [sys.executable, "-m", "mayaboti", "gateway"])


if __name__ == "__main__":
    main()
