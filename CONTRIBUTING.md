<p align="center"><img src="assets/contribute-highfive.jpg" alt="Two robots high-fiving over a laptop" width="70%"></p>

# Contributing

Thanks for building on subpowers. Small, tested pull requests win.

## Ground rules

1. **No API keys, ever.** Powers run only on logins the user already has, through the provider's official CLI.
2. **Receipts stay.** Every generated file gets its `.prompt.txt` receipt with the model and signer.
3. **Prove it.** A PR that changes a painter includes one real output image and its receipt (drag them into the PR description).
4. **Keep it light.** Bash + Python 3 standard library. No new runtime dependencies without a good reason in the PR.
5. **Plain words.** The README is for business owners and creators as much as for coders.

## Set up

```bash
git clone https://github.com/<you>/subpowers ~/.claude/skills/subpowers
bash ~/.claude/skills/subpowers/install.sh
subpowers doctor --smoke
```

## Before you open a PR

```bash
for f in bin/subpowers bin/chatgpt-image bin/antigravity-image bin/grok-image bin/doctor bin/update-codex install.sh; do /bin/bash -n "$f"; done
python3 -m py_compile bin/resolve-drivers bin/library bin/slideshow bin/imgops
bash tests/run.sh   # every painter end to end against stub CLIs; paints nothing, spends no quota
bash install.sh --dest /tmp/subpowers-test --no-doctor   # installer dry run
subpowers doctor
```

Scripts must run on macOS's built-in bash 3.2: guard empty arrays with `${arr[@]+"${arr[@]}"}`.

## Adding a painter

A painter is `bin/<name>-image` with the same contract as `bin/chatgpt-image`:

- `"<prompt>" <out> [--size WxH] [--ref IMG]...`
- output path on stdout, progress and warnings on stderr, a `<out>.prompt.txt` receipt
- it calls the provider CLI's own built-in image tool (never a script that fakes an image, never an API key)
- exit codes: 2 usage, 3 not logged in, 5 painted but not delivered (the front door never paints again), 127 CLI missing, 1 anything else

Then add it to `bin/subpowers`, `bin/doctor`, the README painter table, `SKILL.md` and a line in `CHANGELOG.md`.

## Where to start

Look at [ROADMAP.md](ROADMAP.md) and the issues labeled `good first issue`. Video (`subpowers video`) and the Studio page are the big ones.
