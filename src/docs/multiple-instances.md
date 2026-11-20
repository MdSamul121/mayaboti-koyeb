# Multiple Instances

Run separate mayaboti instances whenever you want completely independent settings, chat bots, and long-term memory—for example, separating personal and work agents or isolating different clients.

> [!NOTE]
> Starting a new topic or picking a different project folder inside one instance does **not** separate long-term memory. Use separate instances when data must not mix.
>
> Separate instances separate mayaboti data, not OS permissions. For mutually untrusted users, run them under separate OS accounts or containers and configure [tool restrictions](./configuration.md#security).

## Quick Start

Pass `--home <directory>` before the subcommand (without it, mayaboti uses `~/.mayaboti`). Give each running instance its own WebUI and gateway ports:

```bash
mayaboti --home ~/.mayaboti-work onboard
mayaboti --home ~/.mayaboti-work webui --port 8766 --gateway-port 18791
```

Configure this instance's models in **Settings → Models** and chat apps in **Channels**. Use the same `--home` flag for any other command targeting this instance:

```bash
mayaboti --home ~/.mayaboti-work status
mayaboti --home ~/.mayaboti-work agent
mayaboti --home ~/.mayaboti-work gateway --port 18791
```

Each concurrent instance needs distinct `--port` (WebUI, default `8765`) and `--gateway-port` (gateway health, default `18790`) values, plus its own chat-bot tokens. You can also save those ports in each instance's `config.json`.

## Where Each Instance Stores Data

| Data | Location |
|---|---|
| Config | `<home>/config.json` (or explicit `--config`) |
| Workspace (memory, skills, automations) | `<home>/workspace/` by default (or explicit `--workspace`) |
| Sessions, media, logs, and CLI history | Inside `<home>/` (or the directory of `--config`) |

Verify which paths an instance will use at any time with:

```bash
mayaboti --home ~/.mayaboti-work status
```

If you prefer custom directories instead of `--home`, pass `--config` and `--workspace` directly:

```bash
mayaboti onboard --config ~/bots/work/config.json --workspace ~/work-agent
mayaboti webui --config ~/bots/work/config.json --port 8766 --gateway-port 18791
```

Keep each instance's config file in its own directory and outside its workspace so sessions and runtime files stay cleanly separated.

## Health Check

Each gateway exposes `GET /health` on `127.0.0.1:<gateway-port>` (`18790` by default), returning HTTP `200` when the gateway and WebSocket channel are ready (or `503` if WebSocket is enabled but not ready). See [CLI Reference: Gateway](./cli-reference.md#gateway) for service management commands.
