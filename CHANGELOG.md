# Changelog

One line per change, with the why. Newest first.

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
