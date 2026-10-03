<h1 align="center">subpowers</h1>

<p align="center"><b>Your coding agent makes images on the ChatGPT, Google and Grok plans you already pay for.</b><br>
No API key. No per-image bill. One prompt, three plans, you pick.<br>
<sub>Needs a paid ChatGPT, Google AI or SuperGrok plan. Built and tested on a Mac.</sub></p>

<p align="center"><picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/hero-still.jpg">
  <img src="assets/hero-slider.webp" alt="Parody illustration: Elon Musk, Sam Altman and Sundar Pichai hanging out as friends in three styles: taking a selfie on a Tesla at a Los Angeles overlook (GTA), fist-bumping (Street Fighter), and at a podcast table (caricature). Their phone cases show Grok, ChatGPT and Google." width="100%">
</picture></p>
<p align="center"><sub>Parody, painted by subpowers. Nobody pictured, and none of their companies, endorse it.</sub></p>

<p align="center">Paste this into Claude Code, Codex or Cursor:</p>

```text
Install https://github.com/itsluisc/subpowers for me, then tell me what I need to log in to.
```

<p align="center">Works with Claude Code, Codex, Cursor, Gemini CLI, and anything that can run a command. Built on macOS.</p>

---

## Install in one message

<p align="center"><img src="assets/demo-council.webp" alt="A terminal: the command subpowers image, a red fox in a scarf on a rooftop at night, painter council, then Grok, ChatGPT and Google each report their image, and a side-by-side sheet of three foxes appears" width="90%"></p>

Paste the message above into your coding agent. It reads the "For AI agents" section below and does the rest. The only thing you do yourself is log in to your own account (a browser window opens once).

Prefer typing it yourself? Three commands:

```bash
git clone https://github.com/itsluisc/subpowers ~/.claude/skills/subpowers
bash ~/.claude/skills/subpowers/install.sh
codex login        # ChatGPT painter: choose "Sign in with ChatGPT"
```

Using Google or Grok instead (or too)? Install their CLI and sign in once:

```bash
curl -fsSL https://antigravity.google/cli/install.sh | bash   # Google (Antigravity CLI)
agy                # sign in in the browser, then type /exit
curl -fsSL https://x.ai/cli/install.sh | bash                # Grok (needs SuperGrok)
grok login
```

Then ask any agent for an image. Or type it:

```bash
subpowers image "a red fox in a scarf on a rooftop at night" ~/Desktop/fox.png --painter council
```

## Council mode: every plan paints it, you pick the best

<p align="center"><img src="assets/council-gta.jpg" alt="One prompt painted on three plans: the ChatGPT version large on top, labeled the pick; the Google version and the Grok version below, the Grok one labeled wrong phone because it gave Elon a ChatGPT phone" width="100%"></p>

```bash
subpowers image "the three founders on a Tesla hood at a Los Angeles overlook, GTA loading-screen style" out.png --painter council
```

One prompt, three painters in parallel, one side-by-side sheet. Above: ChatGPT won this round, Google was close, and Grok handed Elon a ChatGPT phone (its receipt shows it was asked for a Grok one). The second and third opinions cost nothing extra: they come out of plans you already have.

## Same cast, every scene

<p align="center"><img src="assets/cast-slider.webp" alt="The same three friends in six scenes: selfies in a Tesla, a podcast, a loft shoot, the Venice boardwalk, a rooftop at night, a cafe" width="85%"></p>

Paint a cast once, then pass that image back with `--ref` and write "the same people as in the reference". These six scenes are one cast (all AI-generated people), painted on a ChatGPT plan.

## What it made (real outputs, real commands)

Every caption comes from the receipt saved next to the image.

<table>
<tr>
<td width="33%"><img src="assets/product-before.jpg" alt="Black bottle on a concrete block"><br><sub><b>Your product shot</b> (the reference)</sub></td>
<td width="33%"><img src="assets/product-after.jpg" alt="The same bottle on a mossy rock by a stream"><br><sub><b>ChatGPT</b> · <code>--ref</code> the bottle, "on a mossy rock by a mountain stream". Same cap, same finish.</sub></td>
<td width="33%"><img src="assets/key-map.jpg" alt="Brass key on a folded paper map"><br><sub><b>ChatGPT</b> · product macro · <code>--size 1024x1024</code> · 61 s</sub></td>
</tr>
<tr>
<td><img src="assets/grok-fox-before.jpg" alt="A red fox sitting in snow"><br><sub><b>Grok</b> · a fox (the reference)</sub></td>
<td><img src="assets/grok-fox-after.jpg" alt="The same fox in a red scarf on a rooftop at night"><br><sub><b>Grok</b> · <code>--ref</code> the fox, "red scarf, rooftop at night" · 35 s</sub></td>
<td><img src="assets/portrait-lighthouse.jpg" alt="Flat illustration of a lighthouse at night"><br><sub><b>ChatGPT</b> · poster · <code>--size 1024x1536</code> exact</sub></td>
</tr>
</table>

## Every image comes with a receipt

Every image gets a receipt: a plain-text file saved next to it that says who made it and how. It holds your prompt, the prompt the model actually received, which painter and helper model ran, the content credential (C2PA) the provider embedded in the image, sizes and timings. A real one, from the first scene in "Same cast, every scene" (folder paths trimmed):

```text
PROMPT (as given):
Recreate the reference photo as the same moment: the same parked Tesla Model Y with the white interior, ...
Change only how real the blonde and the brunette look. ...

provenance:
  door: subpowers/bin/chatgpt-image
  codex: codex-cli 0.157.0
  driver model: gpt-6-sol (chain: gpt-6-sol:gpt-5.6-sol; reasoning high)
  image model: OpenAI's current ChatGPT image model, chosen server-side | C2PA says: ChatGPT/gpt-image (signed by OpenAI)
  references: 1 (car-chatgpt.png)
  requested size: 1536x1024
  painter size: 1536x1024
  delivered size: 1536x1024
  image_gen saved_path: ~/.codex/generated_images/01a0db4a-.../exec-77922a9d-....png
```

The receipt also says when an image was cropped or upscaled on your machine.

## It tells you exactly what's wrong

<p align="center"><img src="assets/doctor.png" alt="subpowers doctor, trimmed: the ChatGPT, Google and Grok painters each pass, then READY: your agents can make images with chatgpt, antigravity and grok" width="90%"></p>

`subpowers doctor` checks every painter, your logins, and where your agents can find the skill, then prints the exact command for anything that's off. `subpowers doctor --smoke` makes one real test image per painter.

## FAQ

**Will this get my account banned?** subpowers drives the official `codex`, `agy` and `grok` command-line tools on your own login, the same way you would by hand. API-key auth is switched off for every call, so it can only use your plan, and images count against your plan's normal limits. Use your own login on your own machine; don't share it or resell access.

**Which plans work?** Tested on ChatGPT Pro, Google AI Pro and SuperGrok. A ChatGPT plan needs Codex access; Grok images need SuperGrok. `subpowers doctor` tells you what your login can do. Found a plan that works (or doesn't)? Open an issue.

**Linux or Windows?** Built and tested on macOS. Linux reports are welcome. Windows is untested.

**Is this related to obra/superpowers?** No. superpowers teaches coding agents better workflows. subpowers turns the AI plans you already pay for into tools your agents can use. They work fine together.

**Is the receipt signed?** The receipt is a plain text file. The image itself carries the provider's content credential (C2PA); subpowers reads who signed it but does not cryptographically verify it.

**Can it make photos of real people?** Please don't use it for photorealistic fakes of real people. Nothing in the code stops you, so it's on you. Your own face (`--refs me`) and made-up characters are what it's for.

## The three painters

<details>
<summary>What each plan needs, how fast it is, what shapes it paints</summary>

| | ChatGPT | Google (Nano Banana) | Grok |
|---|---|---|---|
| You need | a ChatGPT plan with Codex access + `codex login` | a Google AI plan with Antigravity + `agy` signed in | SuperGrok + the Grok CLI + `grok login` |
| Model | OpenAI's current image model | Nano Banana 2 (Gemini 3.1 Flash Image) | Grok Imagine (quality model) |
| Speed (measured) | 60 to 100 s | 20 to 120 s | 45 to 100 s |
| Shapes | square, 3:2, 2:3 exact; others requested | 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9 | 1:1, 16:9, 9:16, 3:2, 2:3 |
| Reference photos | yes, any number | yes, up to 3 | yes (image edit) |

</details>

`subpowers image` uses ChatGPT when it's connected, then Google, then Grok. Pick one with `--painter chatgpt|google|grok`, all of them with `--painter council`, or set `SUBPOWERS_PAINTER`. Every painter runs with API-key auth switched off, so it can only ever use your plan.

**Video.** `subpowers video "<prompt>" out.mp4` makes a short clip with sound on your SuperGrok plan (Grok Imagine video, 1 to 15 s, 480p or 720p). Give it a first frame with `--first img.png`, people or products with `--ref`/`--refs`, or nothing at all and it paints the first frame for you on your image plan, then animates it. Accounts in Grok's privacy mode (`/privacy` set to Opt out) need to opt in or add a video storage bucket first. Google's Gemini Omni video is on the [roadmap](ROADMAP.md).

**Stop-motion.** `subpowers stopmotion "a small clay fox tiptoes across a felt meadow and waves" out.mp4` plans the frames on your subscription, paints frame 1, then paints every other frame from frame 1 so the set and the character stay put, and hands back an mp4 plus a looping webp. `--resume` picks up after a spent quota without repainting what is done.

<p align="center"><img src="assets/stopmotion-clay-fox.webp" width="360" alt="Eight ChatGPT-painted frames of a clay fox waving, played as a stop-motion loop"></p>
<p align="center"><sub>One sentence, 8 frames on a ChatGPT plan, 4 min 38 s. Real output, not retouched.</sub></p>

## Beyond one image

```bash
subpowers image "..." out.png --painter council      # every connected plan at once + a side-by-side sheet
subpowers refs add me selfie.heic event.jpg          # save who you are once (or a product, or a world)
subpowers image "me on a rooftop at golden hour" out.png --refs me
subpowers sheet me sheet.png --painter council       # character sheet: front, profiles, 3/4, back, face close-up
subpowers storyboard shots.txt board/ --refs me --style "35mm, deep blue palette"
subpowers library find podcast                       # every image you have made, newest first, with its tags
subpowers slideshow slider.webp a.png b.png c.png    # one looping slider of your picks (plays in any README)
```

- **Reference sets** keep the same person (or product) consistent across every image, sheet and storyboard frame.
- **Storyboards:** write one shot per line (framing, action, setting). Frames paint in parallel and land in `storyboard.jpg` in order.
- **Cancel a plan, nothing breaks.** A logged-out or cancelled plan shows OFF in `subpowers powers`, and the default mode moves to the next painter when one fails or runs out of quota.
- **One rule for real people:** never pass a photo of someone *else* as a setting reference. The painters borrow faces from every reference. Describe the set in words instead.
- **Every image is indexed** in `~/.subpowers/library.jsonl`: where it is, the painter, the image model, the helper model and effort, the prompt, references, sizes and the C2PA signer, plus your own tags (`SUBPOWERS_TAGS=project=launch`). Nothing is copied. Want backups? Drop an executable script at `~/.subpowers/hooks/after-image` (it gets the image, its receipt and its id) and send them to B2, S3 or Drive.

<details>
<summary>Always the best model, and how to pick your own</summary>

| Piece | How it stays current |
|---|---|
| The painters | OpenAI and Google pick the image model on their side on every call, so it can't go stale. Grok is asked for xAI's quality Imagine model (`grok-imagine-image-quality`); a plan without it falls back to xAI's default by itself. |
| The helper models | The text model that hands your prompt to the painter runs at **high** effort, because it writes what the painter actually sees. ChatGPT: read fresh from codex's own model list on *your* account, newest first, retiring models skipped. Google: the newest Gemini Flash at its High setting. Grok: the newest non-fast Grok model. |
| The codex CLI | Checked once a day and updated automatically. Turn it off with `SUBPOWERS_NO_AUTOUPDATE=1`, in your shell or in `~/.subpowers/config` (do this if Homebrew or npm manages your codex). |

Your own picks go in `~/.subpowers/config`, one `KEY=value` per line; anything you set in the shell still wins. For example, to keep the image helper off your most expensive model so its quota stays free for real work:

```bash
CHATGPT_IMAGE_DRIVERS=gpt-6-sol     # ChatGPT helper model chain, first one tried first
CHATGPT_IMAGE_EFFORT=high           # low | medium | high | xhigh
AGY_IMAGE_EFFORT=high               # low | medium | high
GROK_IMAGE_MODEL=                   # empty = xAI's default Imagine model instead of the quality one
```

</details>

<details>
<summary>Use it in Cursor, Gemini CLI, or any agent's rules</summary>

- **Claude Code**: automatic. It loads `~/.claude/skills/subpowers` at startup (restart open sessions).
- **Codex**: automatic, via `~/.codex/skills` and `~/.agents/skills` (the installer links both).
- **Cursor, Gemini CLI, custom agents, your `AGENTS.md` / `CLAUDE.md`**: paste this block into the agent's rules:

```markdown
## Making images
To make any image, run:
  subpowers image "<detailed prompt>" /absolute/path/out.png [--size 1536x1024] [--ref photo.jpg] [--painter council|chatgpt|google|grok]
- Uses my own ChatGPT / Google AI / SuperGrok subscription. No API key.
- Takes 1 to 2 min: use a 10-minute command timeout.
- It prints the saved path. Look at the image before saying it is done.
- Full instructions: ~/.claude/skills/subpowers/SKILL.md
```

</details>

Update anytime with `subpowers update` (check what you have with `subpowers --version`). If a copy installed before v0.3.1 stops with "commit your changes", run `git -C ~/.claude/skills/subpowers -c core.fileMode=false pull --ff-only` once (the old installer's `chmod` looked like an edit). Uninstall: delete `~/.claude/skills/subpowers` plus the links in `~/.agents/skills`, `~/.codex/skills` and `~/.local/bin`.

## For AI agents: how to install this for your user

1. `git clone https://github.com/itsluisc/subpowers ~/.claude/skills/subpowers` (if it already exists, `git -C ~/.claude/skills/subpowers pull` instead).
2. `bash ~/.claude/skills/subpowers/install.sh`. It links the skill for other agents, puts `subpowers` on PATH, installs the codex CLI if npm or Homebrew is present, and runs the doctor.
3. Read the doctor's last lines. If no painter is ready, tell your user to run **one** of these themselves (each opens a browser to sign in, which you must not do for them): `codex login` (ChatGPT), `agy` (Google; install it first with `curl -fsSL https://antigravity.google/cli/install.sh | bash`) or `grok login` (Grok, SuperGrok; install with `curl -fsSL https://x.ai/cli/install.sh | bash`).
4. After they log in, run `subpowers doctor --smoke` and show them the test image.
5. From then on, read `~/.claude/skills/subpowers/SKILL.md` before making images.

Never ask the user for an API key, and never put one in. subpowers only uses the logins they own.

## Good to know

- Images use your plan's normal usage limits; an image costs more of your allowance than a text message. If a plan runs out, that painter says so and the default mode moves to your next plan. It never switches to a paid API.
- This rides on the official `codex`, `agy` and `grok` command-line tools, not on a published image API, so providers can change behavior. The doctor and the daily codex update are there for exactly that.
- The `agy` CLI has no per-tool allowlist, so the Google painter cannot limit its helper to the image tool. Each call skips agy's permission prompts, so it runs with `--sandbox`, an empty temporary profile (no MCP servers) and a temporary folder.
- subpowers is an independent open-source project. ChatGPT and Codex are trademarks of OpenAI; Antigravity, Gemini and Nano Banana are trademarks of Google; Grok and Grok Imagine are trademarks of xAI. None of them made or endorses this.

## What's next: build it with us

This is the first power. Next up is video, then a **Studio** page to browse every image with its receipt and re-run a winner in one click. See the [roadmap](ROADMAP.md).

Want to build a piece of it? Read [CONTRIBUTING.md](CONTRIBUTING.md), open an issue, send a pull request, or say hi in [Discussions](https://github.com/itsluisc/subpowers/discussions). Every good idea that ships gets credited.

## Credits

The ChatGPT painter started as [oakplank/gpt-image-bridge](https://github.com/oakplank/gpt-image-bridge) (MIT) and was rebuilt from there: newest-model resolver, receipts, reference photos, doctor, installer, and two more painters. Built by [Luis Carrillo](https://github.com/itsluisc) with his agent team. MIT licensed. How the pieces fit: [architecture diagram](docs/diagrams/architecture.md). What changed: [CHANGELOG](CHANGELOG.md).
