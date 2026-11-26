# Changelog

One line per change, with the why. Newest first.

## [0.5.0] - 2026-11-25

### Added
- **Universal Dual Plugin (Claude Code + Antigravity + Codex + Cursor + Grok + Hermes):** `.claude-plugin/{plugin.json,marketplace.json}`, `.mcp.json`, `commands/{paint,council,avatar,video,doctor}.md`, root `plugin.json`, `mcp_config.json`, `assets/icon.svg`, `rules/subpowers.mdc`, and `skills/subpowers/SKILL.md`.
- **Shared Zero-Dependency Stdio MCP Server (`bin/subpowers-mcp`):** pure Python 3 JSON-RPC 2.0 server supporting both newline-delimited JSON and `Content-Length` framing, exposing `subpowers_powers`, `subpowers_doctor`, `subpowers_image`, `subpowers_avatar`, `subpowers_video`, `subpowers_refs`, and `subpowers_soul`.
- **Higgsfield Soul IDs & Video:** `--soul-id NAME_OR_UUID` + `--style-id` in `bin/higgsfield-image` (auto-routes to `text2image_soul_v2`, ~0.12 credits, respecting `1.5k`/`2k` quality enum and 1-ref limit), `bin/higgsfield-soul` (`subpowers soul list|get|create`), and `bin/higgsfield-video` (`subpowers video --painter higgsfield`, default `seedance_2_5`, auto `omni_reference`/`t2v` mode selection, priced first and capped by `HIGGSFIELD_VIDEO_MAX_CREDITS`).
- **4-Painter Council opt-in:** `--with-higgsfield` on `subpowers image --painter council` and `SUBPOWERS_COUNCIL_PAINTERS` config override, while keeping default `auto` and `council` strictly free of Higgsfield credit spend.
- **Dark Neutral Gray (`#3A3A3C`) Avatar Turnaround Sheets:** `subpowers avatar` (alias for `sheet`) supports `--from IMG` (single-photo shortcut) and `--style photoreal|3d-toon`, using flat `#3A3A3C` neutral gray shadowless lighting for clean downstream scene relighting.
- **`install.sh --link` & multi-harness wiring:** symlinks into `~/.gemini/config/skills`, `~/.cursor/skills`, `~/.grok/skills`, and `~/.hermes/skills` when present, and links `subpowers-mcp`, `grok-video`, `higgsfield-image`, `higgsfield-video`, and `higgsfield-soul` into `~/.local/bin`.

### Changed
- Updated Grok / xAI subscription wording and error matching for **The X Subscription** (formerly SuperGrok, Oct 2026 rename) across CLI, doctor, installer, SKILL.md, and README.
- Documented honest Higgsfield Unlimited (`use_unlim`) boundary: Higgsfield gates free-unlimited server-side to web, Claude chat, Claude Cowork, and ChatGPT; CLI calls always price credits transparently first.

### Fixed
- `bin/grok-video` executable permission bit (`+x`).
- `bin/higgsfield-image` quality enum validation so models like `text2image_soul_v2` (`1.5k`/`2k`) no longer receive invalid `--quality high`.

## [0.4.0] - 2026-11-13

### Added
- `--painter higgsfield` (`bin/higgsfield-image`): the official `higgsfield` CLI on your Higgsfield plan, browser sign-in, no API key. Default model Nano Banana 2.1 (`nano_banana_2_1`); `HIGGSFIELD_IMAGE_MODEL` picks any image job id (`gpt_image_2_6`, `grok_image_2_0`). It is the one painter that costs per image, so it prices the job first, refuses above `HIGGSFIELD_IMAGE_MAX_CREDITS` (default 2), writes the estimate and the balance before and after into the receipt, flags a job that reports a different model, and is never picked by `auto` or `council`.
- HyperFrames: `--into PROJECT` for image, video and stop-motion, `subpowers hf add|remove|skill`, and `subpowers hf skill --project P --attach`, which also attaches the chat skill to that project in the HyperFrames app (`chat-skills.json`, only adds, keeps a .bak).
- `--match-set VIDEO[@SECONDS]` and `bin/set-plate`: paint on the set of your own footage, with the people removed from the plate.
- `bin/cliproxy-image`: an explicit, opt-in Antigravity fallback through a loopback OAuth proxy (never a Google API key).
- `subpowers doctor` reports Higgsfield (opt-in) and which Grok image and video models are requested.

### Changed
- Grok images ask for `grok-imagine-image-2.0`. xAI retired `grok-imagine-image-quality` on 2026-11-02 (that id quietly served 2.0 at low quality).
- Grok video receipts name `grok-imagine-video-1.5`, the model grok 1.0.77 asks for (still 480p or 720p through the CLI).
- Antigravity paints through agy's built-in image-generator subagent (agy 1.2.16+ moved `generate_image` there); the receipt reads the painter id back from the job.
- The HyperFrames chat skill says it works on any model the app chat runs on, and that the app's own generation (Nano Banana 2.1 since app 0.9.38) spends HeyGen credits.

### Checked, no change needed
- codex 0.169 turns off project config and MCP servers for `codex exec` in untrusted folders. The ChatGPT painter already passes its own isolation (`mcp_servers={}`, `project_doc_max_bytes=0`) on the command line, and a live run on 0.169.0 painted normally.
- `hyperframes snapshot --at` adds an end frame by default; `--into --snapshot` already passes `--no-end`.

## [0.3.2] - 2026-09-26

### Added
- `subpowers --version` (also `version`, `-v`): prints the version and the git commit, so a bug report can say exactly what ran.
- `docs/diagrams/architecture.md`: one diagram of how an image request flows from your agent to a saved file.
- Tests for `--version`, storyboard flags with no value, the `google` alias, the config opt-out and empty-plan messages.

### Changed
- One set of measured speeds in the README, SKILL.md and the help (they disagreed). The painter id stays `antigravity`; `google` remains an alias.
- README says up top that you need a paid plan and a Mac, instead of 100 lines down.
- README and CONTRIBUTING no longer call reference sets "next" (they shipped in 0.2).

### Fixed
- `subpowers storyboard` with no value for `--painter`, `--style`, `--size`, or `--refs` crashed with `$2: unbound variable`. Those flags now use the same guard as stopmotion and exit 2.
- The unknown-painter error names the painter id: chatgpt, antigravity, grok, council. `google` is still accepted and still maps to antigravity.
- CONTRIBUTING's pre-PR check skipped `bin/grok-image` and the Python helpers.
- `SUBPOWERS_NO_AUTOUPDATE=1` in `~/.subpowers/config` was ignored (the reader only took painter keys), so a Homebrew-managed codex could only opt out from the shell.
- An empty Google or Grok plan said the image tool "may not have been called" or hinted at a policy refusal. Both now say `dry (quota)`: Google gives the reset time, Grok quotes its reason (e.g. `402 ... usage balance exhausted`). Seen live on 2026-09-26.
- Google's speed range starts at 20 s: a real 1024x1024 run on 2026-09-26 took 20 s, below the old 40 s floor.

## [0.3.1] - 2026-09-25

### Fixed
- Fixes from the Dave and Drey audits: SIGPIPE under pipefail read a logged-in plan as OFF, timeouts on stock macOS, a paid paint is always delivered (exit 5, never painted twice), a dry helper model falls through, a fresh install with no logins exits 0.

### Added
- Stand-in CLIs and an end-to-end test of every painter, in CI on Ubuntu and macOS.

## [0.3] - 2026-09-25

### Added
- Council mode, the image library, `subpowers slideshow`, best-quality defaults, honest plan detection.

## [0.2] - 2026-09-25

### Added
- Grok painter, fan-out, fallback, reference sets, character sheets, storyboards.
