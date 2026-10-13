# Cross-harness packaging pilot

AI SDLC is an experimental skills-only plugin named `ai-sdlc`. Its one skill
remains `ai-sdlc-skill`. The [Skills CLI and manual routes](INSTALLATION.md)
remain the recommended installation paths. No public marketplace listing,
MCP server, automatic helper, hook, or new permission is included.

## Package layout

| Entry | Purpose |
| --- | --- |
| `plugin.json` | Portable Agent Plugins identity; discovers root `skills/` |
| `.codex-plugin/plugin.json` | Codex compatibility fallback; points to `./skills/` |
| `.claude-plugin/plugin.json` | Claude identity; uses default root `skills/` discovery |
| `skills/ai-sdlc-skill/` | The only canonical bundle, including its existing optional helpers |

The thin manifests share identity and version, checked against the canonical
skill in CI. Claude's default skills directory is not also declared as a
custom directory. No skill content is copied into a harness adapter. Keep
installed copies out of this source tree. A package install changes discovery,
not the skill's authority, approval behavior, or optional helper semantics.

For a ZIP containing only the package, first commit and review the candidate,
then run from the checkout (choose a new output filename):

```sh
git rev-parse HEAD
git archive --format=zip --output=../ai-sdlc-plugin.zip HEAD \
  plugin.json .codex-plugin/plugin.json .claude-plugin/plugin.json \
  skills LICENSE NOTICE
```

This archives the committed candidate, not uncommitted edits. Record its full
SHA with the ZIP. Test fixtures, repository instructions, CI, and private local
configuration are excluded. Extract into a new disposable directory before
testing. Do not overlay an existing install or silently replace local edits.

## Isolated installation and rollback

Use one discovery route and scope per host. If a standalone copy is already
installed, test the plugin in a separate clean profile/project rather than
activating both. Keep a reviewed source SHA and preserve local edits before any
update. A new version requires rechecking discovery and the first task.

**Claude Code:** with an already installed, authenticated client, use its
native validator and session-only plugin loading:

```sh
claude plugin validate /absolute/path/to/extracted-package
claude --plugin-dir /absolute/path/to/extracted-package
```

Use a disposable Claude configuration directory through the client's supported
`CLAUDE_CONFIG_DIR` setting when feasible; do not copy credentials or sign in to
a new profile just for this pilot. In a fresh session, confirm exactly one
`/ai-sdlc:ai-sdlc-skill` entry, invoke it on the first task below, and record the
loaded file path. To roll back session-only loading, exit and launch without
`--plugin-dir`. The existing standalone invocation stays `/ai-sdlc-skill`.

**Codex:** use a disposable marketplace root with the extracted package at
`plugins/ai-sdlc/`. Create `.agents/plugins/marketplace.json` there:

```json
{
  "name": "ai-sdlc-pilot",
  "plugins": [{
    "name": "ai-sdlc",
    "source": {"source": "local", "path": "./plugins/ai-sdlc"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Productivity"
  }]
}
```

On versions with the plugin CLI, use a disposable configuration root via the
client's supported `CODEX_HOME` setting for **each** command:

```sh
codex plugin marketplace add /absolute/path/to/disposable-marketplace
codex plugin list --available --json
codex plugin add ai-sdlc@ai-sdlc-pilot --json
codex plugin list --json
```

Do not point these commands at your normal profile during this pilot. Command
availability depends on the installed client. Stop if authentication, new
permissions, or unsupported installation is needed. In a supported local client,
select the plugin's skill using the displayed skill selector; do not assume
Claude's namespace syntax. Record exactly one entry and its loaded source.
If the installed version requires desktop installation/testing, that UI step
remains a separate host check. Catalog listing alone is not skill discovery.

Rollback in that same disposable configuration: run
`codex plugin remove ai-sdlc@ai-sdlc-pilot` and
`codex plugin marketplace remove ai-sdlc-pilot`, then exit the profile. Preserve
any evidence before discarding only the task-owned temporary directories. No
global install or existing standalone skill needs to be changed.

## First task and evidence levels

In a disposable project, add a README with a deliberate typo and repository
instructions limiting changes to that README. Invoke the installed skill:

> Correct the README typo. Read the repository rules, keep the change scoped,
> and report the skill file loaded, actual checks, revision, and missing evidence.
> Do not commit, publish, or install anything.

Observe that the host loads one skill, follows repository rules, makes only the
authorized correction, and does not claim unrun tests or approvals. Record the
client version, source SHA, installation method, output and remaining limits in
the PR. Repeat independently for each host before claiming cross-host behavior.

| Evidence | What it establishes |
| --- | --- |
| `python3 scripts/test_plugin_packaging.py` | Static layout, identity consistency, one canonical skill, no default hooks; synthetic payload handling |
| Archive inventory and byte comparison | The committed bundle is packaged once without fixture contamination |
| Native plugin validator/catalog/install | Only the stages actually observed on that client |
| Fresh session and first task | Native skill discovery and observed behavior on that particular host |
| Local hook callback | Only the event and callback actually observed under local orchestration |

File layout tests are not a host schema validator. Payload fixtures are not
callbacks. No full behavior evaluation, productivity improvement, cloud hook
support, or cross-host runtime compatibility follows from static tests.

During this pilot, Codex CLI `0.159.0-alpha.3` installed and enabled the plugin
in disposable configuration. Its native app-server `skills/list` returned
exactly one enabled `ai-sdlc:ai-sdlc-skill` with the plugin ID and installed
bundle path, and no discovery errors. The isolated profile was not logged in,
so model-driven behavior was not run; no credentials were copied or created.
Claude Code was unavailable, so its native validation, discovery and behavior
were not run. Real local hook callbacks were not run on either host. Exact
candidate checks and archive evidence belong in the pilot pull request.

## Harmless hook fixture (excluded from the package)

`scripts/fixtures/plugin-hooks/` contains separate Codex and Claude hook
configurations and synthetic inputs. Both exercise only `SessionStart` with
`source: startup`. The probe reads JSON, emits a fixed stderr marker, and exits
zero for the expected event. It writes no files, reads no transcript, makes no
network call, adds no model context, and emits no permission decision. Invalid
input exits one without echoing the payload. This is not a security control.

The Codex adapter uses `PLUGIN_ROOT`; Claude uses `CLAUDE_PLUGIN_ROOT`. Other
events, tool names, payloads, trust, failure handling, and cloud support are not
assumed identical. To prepare a future authorized local callback test, copy the
probe into a separate disposable plugin and copy only the matching adapter to
its `hooks/hooks.json`. Give that fixture its own plugin identity and load it
only in disposable configuration. Review/trust it through the host's normal
mechanism; never bypass hook trust or modify live hooks. Observe the fixed
marker on a real startup and retain the client version and event evidence.

Local/plugin hooks are unsupported with cloud orchestration, even when tools
execute on a local machine. A cloud tool running this Python probe proves only
payload handling. Real local host execution must be separately observed.

## Sources

Checked against official documentation on 13 October 2026:

- [OpenAI packaging, portable schema, compatibility overlay and local marketplace](https://developers.openai.com/plugins/build/plugins)
- [OpenAI's Claude plugin import guide](https://developers.openai.com/plugins/guides/submit-claude-plugin) (import is not a claim of identical runtime behavior)
- [Claude plugins](https://code.claude.com/docs/en/plugins) and [manifest reference](https://code.claude.com/docs/en/plugins-reference)
- [Codex hooks and cloud limitations](https://learn.chatgpt.com/docs/hooks) and [Claude hook input/output](https://code.claude.com/docs/en/hooks)

No public directory submission or private-vault migration is part of this pilot.
