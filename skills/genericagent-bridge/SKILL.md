---
name: genericagent-bridge
description: Bridge Codex to a local GenericAgent checkout. Use this whenever the user mentions GenericAgent, wants to clone, update, inspect, or start https://github.com/lsdefine/GenericAgent.git, or asks to make GenericAgent usable from this Codex workspace. This skill does not rewrite upstream GenericAgent. It manages a local checkout, startup guidance, and boundary-safe integration.
---

# genericagent-bridge

This skill provides a safe local bridge to `GenericAgent` from the current Codex workspace.

## When to use

Use this skill when the user wants to:

- install `GenericAgent`
- update the local `GenericAgent` checkout
- inspect whether `GenericAgent` is already present
- start `GenericAgent` in CLI or UI mode
- understand why `GenericAgent` cannot be installed like a normal Codex skill

## What this skill manages

- Local checkout path: `D:\erp\external\GenericAgent`
- Upstream source: `https://github.com/lsdefine/GenericAgent.git`
- Local helper scripts under `scripts/`

## Boundaries

- Do not modify upstream GenericAgent source as part of bridge tasks unless the user explicitly asks for a fork/customization.
- Do not claim GenericAgent is a native Codex skill repository.
- Treat this bridge as a launcher/integration layer, not a reimplementation.

## Workflow

1. Run `scripts/ensure-genericagent.ps1` to clone or refresh the local checkout.
2. Run `scripts/check-genericagent.ps1` to inspect repository and config readiness.
3. If the user wants to launch it:
   - CLI mode: `scripts/start-genericagent.ps1 -Mode cli`
   - UI mode: `scripts/start-genericagent.ps1 -Mode ui`
4. If `mykey.py` is missing, stop and explain that API key configuration is still required.

## Script guide

- `scripts/ensure-genericagent.ps1`
  Ensures `D:\erp\external\GenericAgent` exists. Downloads the latest GitHub zip and refreshes the local checkout.

- `scripts/check-genericagent.ps1`
  Reports whether the local checkout exists, whether `mykey.py` is configured, and whether entry files are present.

- `scripts/start-genericagent.ps1`
  Starts `GenericAgent` in `cli` (`agentmain.py`) or `ui` (`launch.pyw`) mode if the checkout and config are ready.

## Output expectations

When using this skill, report:

1. Whether the local checkout exists
2. Whether config is ready
3. What action was taken
4. What still blocks actual runtime, if anything
