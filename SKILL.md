---
name: subpowers
description: Use when the user or a workflow needs any generated image (picture, mockup, logo, avatar, thumbnail, hero image, illustration, product shot, concept art, a person or product placed in a new scene from reference photos, a character sheet, a storyboard), when a design, carousel, deck or video skill needs a picture, when a HyperFrames or Agentic Cuts project needs a generated image, B-roll clip or stop-motion layer (`--into PROJECT`), or when a picture would explain something better than text. Runs on the user's own ChatGPT, Google AI or SuperGrok subscription through their logged-in CLIs, no API key.
---

# subpowers

Most agents cannot paint. subpowers hands the job to the image models inside subscriptions the user already pays for: ChatGPT (through the `codex` CLI), Google Antigravity (through the `agy` CLI) and Grok Imagine (through the `grok` CLI). No API key, no per-image bill, and a receipt beside every image.

If `subpowers` is not on PATH, run `bash ~/.claude/skills/subpowers/bin/subpowers ...` (same arguments). Set the command timeout to 600000 ms, or run it in the background.

## Commands

```bash
subpowers image "<prompt>" /abs/out.png [--painter chatgpt|antigravity|grok|council|higgsfield] [--size WxH] [--ref photo.jpg]... [--refs NAME]
subpowers refs add NAME photo1.jpg photo2.heic ...     # save a reference set once (a person, a product, a world)
subpowers sheet NAME /abs/sheet.png [--painter all]     # character sheet: front, profiles, 3/4, back, face close-up
subpowers storyboard shots.txt /abs/outdir [--refs NAME] [--painter P] [--style "..."]   # one frame per line + a board
subpowers powers      # which subscriptions are connected right now
subpowers doctor      # live-checks every painter and names the exact fix
subpowers --version   # which version is installed
```

- stdout is the saved path (for `all`: one path per painter, then the side-by-side sheet). Beside each image: `out.prompt.txt` (prompt, the prompt the model received, model, C2PA signer, timings) and `out.original.*` when resized or converted.
- Look at every image before you show, describe or build on it. Then open it or send it to the user.
- **Offer choices when it matters:** one version (auto), a council (`--painter council`, same as `all`: every subscription paints it and the user picks the best), or different angles (a `sheet`, or several prompts).

## Pick the painter

| | `chatgpt` (default when connected) | `antigravity` (google is an alias) | `grok` | `higgsfield` (opt-in, spends credits) |
|---|---|---|---|---|
| Model | OpenAI's server-chosen image model | Google's server-chosen Nano Banana (`gemini-3.1-flash-image` observed); actual ID in receipt | `grok-imagine-image-2.0` requested | `nano_banana_2_1` by default (`HIGGSFIELD_IMAGE_MODEL`: `gpt_image_2_6`, `grok_image_2_0`, any `higgsfield model list --image` id); the job's own id in the receipt |
| Speed | 30 to 100 s (30 s on 2026-11-13) | 20 to 120 s (42 s on 2026-11-13) | 35 to 100 s (38 s on 2026-11-13) | about 25 s (24 s on 2026-11-13, one run) |
| Best at | text in images, precise product fidelity | fast drafts, likeness from references, photoreal | bold stylized looks, a third opinion | a pinned, named model (Nano Banana 2.1 or Images 2.6) when the user asks for it |
| Sizes | 1024x1024, 1536x1024, 1024x1536 exact; near shapes resized | 1:1, 2:3, 3:2, 3:4, 4:3, 9:16, 16:9 | 1:1, 16:9, 9:16, 3:2, 2:3 | the model's own aspect list, nearest picked; 1k by default (`HIGGSFIELD_IMAGE_RESOLUTION`) |
| References | any number | up to 3 (extra ones dropped) | yes (image edit; the first photo is padded to the asked shape so the scene paints wide) | yes (`--image-references`, auto-uploaded) |
| Needs | `codex login` with ChatGPT | `agy` signed in once | SuperGrok + `grok login` | `higgsfield auth login` (browser, no API key) |

`higgsfield` is the one painter that costs per image (plan credits, about 1.5). It prices the job first, refuses above `HIGGSFIELD_IMAGE_MAX_CREDITS` (default 2), and records the estimate and the balance before and after in the receipt. `auto` and `council` never pick it: use it only when the user asks for Higgsfield or for a model only it has.

`auto` uses the first connected painter and, if it fails (a paused plan, spent quota, a logged-out CLI), moves to the next one. A cancelled subscription never breaks anything: that painter just shows OFF in `subpowers powers` and is skipped.

## References and real people

- `--ref` / `--refs NAME` keep a person's face (their own photos), a product, or a style. Strong resemblance, not an identity lock. iPhone HEIC works on macOS.
- **Never pass a photo of a different real person as a "setting" reference.** The painters borrow faces from every reference (tested: Grok blended the user with the podcast host in the setting photo). Describe the set, pose, outfit and light in words instead, or crop the other person out first.
- Real proof stays real. Screenshots with numbers, logos, headlines and real faces are never regenerated from scratch: generate only the surround (background, mockup, scene) and composite the real pixels in; discard any output where a number, word or logo changed.
- **Brand pictures are painted FROM real references, never from words alone** (words alone come back looking like stock). Pass `--ref` with the brand's real assets (logo plate, card or product art, a crop of the real set or studio for light and palette). Crop every person out of a reference first, including faces inside a logo file. Use `chatgpt` for logos, cards and lettering; check each one by eye and reject any that drift. Then paste the real logo or card art over the painted one (perspective warp plus a matching grade) and offer both versions on a before/after board. Measured: words only gave a stock scene; ChatGPT with a studio-wall crop, the real card art and the wordmark gave an on-brand shot with both reading correctly; Antigravity with the same references garbled the card.

## Match the set (overlays that look filmed in the room)

`--match-set VIDEO[@SECONDS]` (image) paints on the set of the client's own footage: `bin/set-plate` grabs that
frame (default the middle), finds every face with YuNet, covers each person and fills the hole from the set, and the
plate goes in as one more reference with a line telling the painter to match its light, palette, lens and grain.
Use the RAW horizontal footage (no captions or title burned in, more set visible); a tight vertical frame leaves
little set (the receipt prints `covered`, warn past 0.85). People are removed on purpose: to put the on-camera people
in the shot, add their own photos with `--refs NAME` and say where they are; real people stay real (their own
footage first, a generated likeness only as a labelled concept the person approves). Proof 2026-10-31: the same
cash-stack prompt on a creator's set came back on that light-wood desk with the same pink side light and the clothing
rack behind; the plain prompt came back stock.

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

## Into a HyperFrames project (Agentic Cuts door projects too)

```bash
subpowers image "<prompt>" --into PROJECT --at 12.4 --duration 4 --layer-name "credit card on a desk" --snapshot
subpowers video "<prompt>" --into PROJECT --at 30 --place full --duration 6 --snapshot
subpowers stopmotion "<concept>" --into PROJECT --at 45 --frames 8 --snapshot
subpowers hf add --project PROJECT --file /abs/picture.png --at 12.4 --duration 4   # mount an existing file, no painting
subpowers hf remove --project PROJECT --layer gen-<slug>                             # the media stays
```

- PROJECT is any HyperFrames folder with `index.html` (a door project from `drop_one.py`, a V2 ANIM copy, a new `hyperframes init`). No `index.html`, a time outside the video or a lint failure is refused before anything is painted.
- What lands: `assets/generated/<slug>/<slug>.png|mp4` with its painter receipt `<slug>.prompt.txt` and `<slug>.layer.json` (box, times, lint before and after, the undo command); one scene `compositions/gen-<slug>.html` (hidden starting state in CSS, so no flash before the fade in); one host line in `index.html` between `<!-- subpowers:begin/end gen-<slug> -->` on its own graphics lane. Nothing else changes; a taken name gets -2, -3, never an overwrite.
- `hyperframes lint` runs before and after; a new error puts `index.html` back byte for byte and keeps the painted media.
- `--place lower` (default) sits under the caption rail inside the safe box, never on a face; `full` is a cutaway under captions and titles; `box:x,y,w,h` is exact. With no `--size`/`--aspect`, lower paints 16:9 and full paints the canvas shape.
- Video and stop-motion layers are muted (the speaker is the soundtrack); `--keep-audio` keeps the clip's sound. For `video`, `--duration` is the clip's own length; `--layer-duration` shortens the layer.
- `--snapshot` runs `hyperframes snapshot --at` inside the layer and prints the PNG: read it before you say it is done. Real proof stays real (`hf add` the real asset, never a regenerated one).
- A later door rebuild (`drop_one.py --fix-project`) writes `index.html` from `layers.json` and drops generated layers like any overlay: add them last, or re-mount with `hf add`.
- The HyperFrames app chat: `subpowers-hyperframes` (in `hyperframes/`, linked at `~/.claude/skills/subpowers-hyperframes`, or `subpowers hf skill --project PROJECT --attach`, which also attaches it to that project's chat in the HyperFrames app) tells the in-app agent to use subpowers instead of paid HeyGen generation unless the person asks for HeyGen.

## Plan with `think`

`subpowers think "<question>" [--json-schema FILE]` answers in text on the same subscriptions (ChatGPT first, then Google, then Grok; no shell, no web, no API key). With a schema it prints one JSON object that parses, or fails loudly.

## Always the best model

- Server-side selection is not proof of the newest model. Receipts distinguish requested and observed image IDs. Do not rename an old result after a product announcement. Grok asks for `grok-imagine-image-2.0` (xAI retired `grok-imagine-image-quality` on 2026-11-02; that id quietly served 2.0 at low quality) and falls back to xAI's default when a plan lacks it. Grok video asks for `grok-imagine-video-1.5` (set inside the grok CLI, not by subpowers).
- Helper models run at high effort (they write the prompt the painter sees). ChatGPT: codex's own per-account model list, newest first; codex updates itself daily (`SUBPOWERS_NO_AUTOUPDATE=1` opts out). Antigravity: the newest Gemini Flash at High. Grok: the newest non-fast model in `grok models`.
- The user's own picks live in `~/.subpowers/config` (`KEY=value`: `CHATGPT_IMAGE_DRIVERS`, `CHATGPT_IMAGE_EFFORT`, `AGY_IMAGE_EFFORT`, `GROK_IMAGE_EFFORT`, `GROK_IMAGE_MODEL`, `HIGGSFIELD_IMAGE_MODEL`, `HIGGSFIELD_IMAGE_RESOLUTION`, `HIGGSFIELD_IMAGE_MAX_CREDITS`). Respect them; don't override them with flags unless the user asks.

## Errors

| Message | Fix |
|---|---|
| `no painter is connected` | `subpowers doctor` lists what to install and log in |
| `not logged in with ChatGPT` / `live check ... rejected` | `codex logout && codex login` |
| `agy returned no models` | run `agy` once in a terminal and sign in |
| `grok is not logged in` / exit 4 `SuperGrok feature` | `grok login` with a grok.com account that has SuperGrok |
| `not signed in to Higgsfield` / `over the cap` | `higgsfield auth login`; or raise `HIGGSFIELD_IMAGE_MAX_CREDITS` only when the user agrees to the price |
| `dry (quota)` | that plan's usage is spent; `auto` already moves to the next painter |
| `no image_gen output` / `no generate_image output` / `never called image_gen` | the helper skipped the tool; rerun, or reword a prompt that reads like a policy refusal |
| native AGY 1.3.1 `unknown tool: generate_image` | permissions cannot register the missing executor; the full official Linux app 2.21.0 was verified as a native alternative, but desktop auth is separate and its observed painter was Nano Banana 2, not 2.1 |
| `WARNING ... aspect` / `UPSCALED` | not an error: the receipt says exactly what was cropped or enlarged |
| `no reference set 'NAME'` | `subpowers refs add NAME photo1.jpg ...` |
| `hf-into: refused: not a HyperFrames project` | `--into` needs the folder that holds `index.html` |
| `hf-into: refused: the layer added lint errors` | `index.html` is back as it was; the painted file stays; fix and `subpowers hf add` it |

## Files

- `bin/subpowers`: the front door. `bin/chatgpt-image`, `bin/antigravity-image`, `bin/grok-image`, `bin/higgsfield-image`: the painters (same contract, callable directly).
- `bin/doctor`, `bin/resolve-drivers`, `bin/update-codex`: health check, newest-model choice, codex freshness.
- `bin/hf-into`: `--into` and `subpowers hf` (mounts one layer in a HyperFrames project, lints, undoes). `hyperframes/subpowers-hyperframes/SKILL.md`: the HyperFrames app chat skill.
- Reference sets live in `$SUBPOWERS_HOME/refs/NAME/` (default `~/.subpowers`).
- `install.sh`, `README.md`, `ROADMAP.md`, `CONTRIBUTING.md`.

## Change Log

- 2026-10-02 (Claude, for Luis): two speed fixes in `bin/subpowers`, found by timing every painter alone.
  1. A login probe that TIMES OUT (exit 124 or 142) is no longer read as "logged out" and cached OFF for 10 minutes. On a busy Mac that skipped Nano Banana ("not connected") while it was logged in. Timeout now means assume connected; the real call tells the truth.
  2. `--refs` and `--ref` pictures are shrunk once to 1280 px JPEG and cached in `~/.cache/subpowers/refs-small/`. A 4096 px phone photo kept Nano Banana busy for over 400 s with three references; shrunk, the same job takes 25 s. Measured with the luis shelf: Nano Banana 25 s, Grok 43 s, ChatGPT 60 s.
  Backup: `~/.claude/backups/subpowers.before-timeout-fix-2026-10-02`.
- 2026-10-07: explicit `AGY_IMAGE_TRANSPORT=cliproxy` fallback through an existing loopback Antigravity OAuth proxy, never a Google API key (opt-in; unofficial proxy access can break provider terms). See README.
- 2026-10-23: native Antigravity painter fixed: since agy 1.2.16 `generate_image` lives only in agy's built-in `image-generator` subagent, so the painter delegates to it with the prompt verbatim and reads the painter model back from the job.
- 2026-10-23: `--into PROJECT` for image, video and stop-motion, `subpowers hf add|remove|skill`, the `subpowers-hyperframes` chat skill; doctor reports codex, agy, grok and hyperframes versions.
- 2026-10-31: `--match-set VIDEO[@SECONDS]` and `bin/set-plate` (faces found with YuNet, covered and filled from the set, so no face is borrowed).
- 2026-11-13 (0.4.0): `--painter higgsfield` (opt-in, plan credits, priced first, capped at 2, requested vs reported model in the receipt, never in auto or council); Grok asks for `grok-imagine-image-2.0` (the quality id was retired 2026-11-02); grok video receipts name `grok-imagine-video-1.5`; `subpowers hf skill --attach` adds the chat skill to the HyperFrames app; live smoke on codex 0.169.0, agy 1.5.8, grok 1.0.77, higgsfield 1.2.2: all four painted in 24 to 42 s. Full list: CHANGELOG.md.
