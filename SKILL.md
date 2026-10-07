---
name: subpowers
description: Use when the user or a workflow needs any generated image (picture, mockup, logo, avatar, thumbnail, hero image, illustration, product shot, concept art, a person or product placed in a new scene from reference photos, a character sheet, a storyboard), when a design, carousel, deck or video skill needs a picture, or when a picture would explain something better than text. Runs on the user's own ChatGPT, Google AI or SuperGrok subscription through their logged-in CLIs, no API key.
---

# subpowers

Most agents cannot paint. subpowers hands the job to the image models inside subscriptions the user already pays for: ChatGPT (through the `codex` CLI), Google Antigravity (through the `agy` CLI) and Grok Imagine (through the `grok` CLI). No API key, no per-image bill, and a receipt beside every image.

If `subpowers` is not on PATH, run `bash ~/.claude/skills/subpowers/bin/subpowers ...` (same arguments). Set the command timeout to 600000 ms, or run it in the background.

## Commands

```bash
subpowers image "<prompt>" /abs/out.png [--painter chatgpt|antigravity|grok|council] [--size WxH] [--ref photo.jpg]... [--refs NAME]
subpowers refs add NAME photo1.jpg photo2.heic ...     # save a reference set once (a person, a product, a world)
subpowers sheet NAME /abs/sheet.png [--painter all]     # character sheet: front, profiles, 3/4, back, face close-up
subpowers storyboard shots.txt /abs/outdir [--refs NAME] [--painter P] [--style "..."]   # one frame per line + a board
subpowers powers      # which subscriptions are connected right now
subpowers doctor      # live-checks every painter and names the exact fix
```

- stdout is the saved path (for `all`: one path per painter, then the side-by-side sheet). Beside each image: `out.prompt.txt` (prompt, the prompt the model received, model, C2PA signer, timings) and `out.original.*` when resized or converted.
- Look at every image before you show, describe or build on it. Then open it or send it to the user.
- **Offer choices when it matters:** one version (auto), a council (`--painter council`, same as `all`: every subscription paints it and the user picks the best), or different angles (a `sheet`, or several prompts).

## Pick the painter

| | `chatgpt` (default when connected) | `antigravity` | `grok` |
|---|---|---|---|
| Model | OpenAI's server-chosen image model | Google's server-chosen Nano Banana; actual ID in receipt | xAI's server-chosen Grok Imagine |
| Speed | 60 to 100 s | 17 to 40 s | 32 to 46 s |
| Best at | text in images, precise product fidelity | fast drafts, likeness from references, photoreal | bold stylized looks, a third opinion |
| Sizes | 1024x1024, 1536x1024, 1024x1536 exact; near shapes resized | 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9 | 1:1, 16:9, 9:16, 3:2, 2:3 |
| References | any number | up to 3 (extra ones dropped) | yes (image edit; the first photo is padded to the asked shape so the scene paints wide) |
| Needs | `codex login` with ChatGPT | `agy` signed in once | SuperGrok + `grok login` |

`auto` uses the first connected painter and, if it fails (a paused plan, spent quota, a logged-out CLI), moves to the next one. A cancelled subscription never breaks anything: that painter just shows OFF in `subpowers powers` and is skipped.

## References and real people

- `--ref` / `--refs NAME` keep a person's face (their own photos), a product, or a style. Strong resemblance, not an identity lock. iPhone HEIC works on macOS.
- **Never pass a photo of a different real person as a "setting" reference.** The painters borrow faces from every reference (tested: Grok blended the user with the podcast host in the setting photo). Describe the set, pose, outfit and light in words instead, or crop the other person out first.
- Real proof stays real. Screenshots with numbers, logos, headlines and real faces are never regenerated from scratch: generate only the surround (background, mockup, scene) and composite the real pixels in; discard any output where a number, word or logo changed.

## Prompts that work

- Stage it like a photographer: where the camera is and what lens, where the light comes from, who is where in the frame. Then the look ("unretouched behind-the-scenes photo on 35mm film", "isometric 3D render"). Then the moment ("laughing mid-conversation").
- Photoreal people look AI-made when the prompt only says "beautiful". Add realism cues: natural skin texture with visible pores, real flyaway hairs, authentic fabric drape and creases, light that has a real source (a window, the low sun, a bounce off a white wall).
- Make the physical scene possible. Say how many people, where each one sits or stands, and what the place has ("two separate front seats with a center console, a rear bench"). Vague group scenes come back with three people on one front seat.
- Text: say exactly what lettering exists and nothing else ("the only lettering anywhere is the logo on each phone case: plain clothing without prints, no signs"). A bare "no text" still lets painters scatter slogans on cups, shirts and screens. Put long or exact text on afterwards in code.
- Never name a model inside the prompt.

## Storyboards

Write the shot list yourself (one shot per line: framing, action, setting), save it to a text file, then run `storyboard`. Frames paint in parallel (3 at a time, `SUBPOWERS_PARALLEL`), and `storyboard.jpg` shows them in order. Use `--refs NAME` so the same person appears in every shot, and `--style` for one consistent look. Antigravity is the fastest painter for boards.

## Video

```bash
subpowers video "<prompt>" /abs/out.mp4 [--first IMG] [--last IMG] [--ref IMG]... [--refs NAME] [--voice ID] [--duration 1-15] [--aspect 16:9|9:16|1:1] [--resolution 480p|720p]
```

- Grok Imagine video on the user's SuperGrok plan: an MP4 with sound. Video starts from an image: with no `--first`/`--ref`, subpowers paints the first frame on the default image plan (in the clip's shape), then animates it. About 1 to 2 minutes.
- Describe motion as a change of position ("turns from the city toward the camera"), one clear action per clip.
- `grok-video` fails with "unavailable under zero data retention" when the user's Grok account is in privacy mode: tell them to run `grok`, type `/privacy`, choose Opt in (xAI then keeps that data), or set up a video storage bucket. Never fake a video from stills.

## Stop-motion

```bash
subpowers stopmotion "<concept>" /abs/out.mp4 [--frames 8] [--fps 6] [--painter P] [--refs NAME] [--style "..."] [--chain] [--plan frames.txt] [--audio bed.m4a] [--resume]
```

- One sentence in, a handmade stop-motion clip out: a subscription plans the frames (`subpowers think`), frame 1 is painted, then every later frame is painted with frame 1 as its reference so the set and the character stay the same (`--chain` paints each from the one before instead, slower and more drift). Delivers `out.mp4` (H.264, yuv420p, faststart, needs ffmpeg), a looping `out.webp` (needs Pillow), `out.frames/` with every frame and its receipt, and `out.prompt.txt`.
- One painter per clip (a council would redraw the set three ways). ChatGPT keeps characters most consistent; Antigravity is fastest.
- Frames can fail on a spent quota: `--resume` keeps the plan and the painted frames and paints only what is missing. `--plan FILE` (one frame per line) skips the planner.
- Look at `out.frames/` before showing the clip. The planner is told never to draw paths or marks, but check anyway.
- The clip is silent unless you pass `--audio`.

## Plan with `think`

`subpowers think "<question>" [--json-schema FILE]` answers in text on the same subscriptions (ChatGPT first, then Google, then Grok; no shell, no web, no API key). With a schema it prints one JSON object that parses, or fails loudly.

## Always the best model

- Server-side selection is not proof of the newest model. Receipts distinguish requested and observed image IDs. Do not rename an old result after a product announcement. Grok asks for xAI's quality Imagine model and falls back to xAI's default when a plan lacks it.
- Helper models run at high effort (they write the prompt the painter sees). ChatGPT: codex's own per-account model list, newest first; codex updates itself daily (`SUBPOWERS_NO_AUTOUPDATE=1` opts out). Antigravity: the newest Gemini Flash at High. Grok: the newest non-fast model in `grok models`.
- The user's own picks live in `~/.subpowers/config` (`KEY=value`: `CHATGPT_IMAGE_DRIVERS`, `CHATGPT_IMAGE_EFFORT`, `AGY_IMAGE_EFFORT`, `GROK_IMAGE_EFFORT`, `GROK_IMAGE_MODEL`). Respect them; don't override them with flags unless the user asks.

## Errors

| Message | Fix |
|---|---|
| `no painter is connected` | `subpowers doctor` lists what to install and log in |
| `not logged in with ChatGPT` / `live check ... rejected` | `codex logout && codex login` |
| `agy returned no models` | run `agy` once in a terminal and sign in |
| `grok is not logged in` / exit 4 `SuperGrok feature` | `grok login` with a grok.com account that has SuperGrok |
| `dry (quota)` | that plan's usage is spent; `auto` already moves to the next painter |
| `no image_gen output` / `no generate_image output` / `never called image_gen` | the helper skipped the tool; rerun, or reword a prompt that reads like a policy refusal |
| `WARNING ... aspect` / `UPSCALED` | not an error: the receipt says exactly what was cropped or enlarged |
| `no reference set 'NAME'` | `subpowers refs add NAME photo1.jpg ...` |

## Files

- `bin/subpowers`: the front door. `bin/chatgpt-image`, `bin/antigravity-image`, `bin/grok-image`: the painters (same contract, callable directly).
- `bin/doctor`, `bin/resolve-drivers`, `bin/update-codex`: health check, newest-model choice, codex freshness.
- Reference sets live in `$SUBPOWERS_HOME/refs/NAME/` (default `~/.subpowers`).
- `install.sh`, `README.md`, `ROADMAP.md`, `CONTRIBUTING.md`.

## Change Log

- 2026-10-07: AGY 1.3.1 may advertise `generate_image` while its executor cannot run it. Added explicit `AGY_IMAGE_TRANSPORT=cliproxy` fallback using an existing loopback Antigravity OAuth proxy, never Google API keys. Default remains native; unofficial proxy access can violate provider terms. `AGY_PROXY_IMAGE_MODEL` must be exposed by that provider; default verified ID is `gemini-3.1-flash-image` (Nano Banana 2), not a guessed 2.1 alias. Higgsfield lists Nano Banana 2.1 under its own ID `nano_banana_2_1`; that does not establish the AGY ID. See README for setup and limitations.
