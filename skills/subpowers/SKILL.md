---
name: subpowers
description: Use when the user or a workflow needs any generated image (picture, mockup, logo, avatar, thumbnail, hero image, illustration, product shot, concept art, a person or product placed in a new scene from reference photos, a character turnaround sheet, a storyboard), a short video clip or stop-motion loop, a HyperFrames or Agentic Cuts layer (`--into PROJECT`), or when a picture explains something better than text. Runs on the user's own ChatGPT, Google AI, Grok (The X Subscription), or opt-in Higgsfield plans through their logged-in CLIs or the shared subpowers MCP server, with zero API keys.
---

# subpowers

Most agents cannot paint. `subpowers` hands visual work to the AI subscriptions the user already pays for: ChatGPT (`codex` CLI), Google Antigravity (`agy` CLI), Grok Imagine (`grok` CLI on The X Subscription, formerly SuperGrok), and opt-in Higgsfield (`higgsfield` CLI with Soul 2.0 and video models). Zero API keys, and a provenance receipt beside every file.

Works as a CLI (`subpowers ...`), a shared stdio MCP server (`subpowers-mcp`: `subpowers_image`, `subpowers_avatar`, `subpowers_video`, `subpowers_soul`, `subpowers_refs`, `subpowers_powers`, `subpowers_doctor`), a Claude Code plugin (`.claude-plugin/`), and an Antigravity plugin (`plugin.json`).

If `subpowers` is not on PATH, prefer the `subpowers_*` MCP tools (when installed as a plugin), or run `bash "${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/skills/subpowers}/bin/subpowers" ...` (same arguments). Set the command timeout to 600000 ms, or run it in the background.

## Context-First Intake (Ground Every Visual in Reality)

Before painting from scratch, check whether the user wants to point the visual at something real:
1. **Their own photo, room, environment, or product** -> pass `--ref photo.jpg` or saved `--refs NAME` so lighting, wardrobe, and environment feel genuinely theirs.
2. **A real video set** -> pass `--match-set video.mp4[@seconds]` so overlays match the room's exact light, lens, and grain without borrowing faces.
3. **A reusable identity** -> use a saved `--refs NAME`, build a `#3A3A3C` avatar sheet (`subpowers avatar`), or use a trained Higgsfield Soul ID (`--soul-id NAME`).
4. **A real brand, logo, screenshot, YouTube video, or Instagram post** -> extract real frames or brand assets first and pass them as `--ref`; never regenerate logos, headlines, or real numbers from text alone.
5. **Instagram carousels (optional bridge)** -> if the user asks to turn an Instagram post, reel, or topic into a multi-slide carousel and the Poppy AI MCP (`create_carousel`) is installed, offer Poppy's native carousel builder alongside `subpowers` hero visuals.

## Commands

```bash
subpowers image "<prompt>" /abs/out.png [--painter chatgpt|antigravity|grok|council|higgsfield] [--with-higgsfield] [--size WxH] [--ref photo.jpg]... [--refs NAME] [--soul-id NAME] [--cinematic]
subpowers avatar NAME|--from photo.jpg /abs/sheet.png [--painter council] [--style photoreal|3d-toon]
subpowers soul list | get NAME | create NAME p1.jpg p2.jpg p3.jpg p4.jpg p5.jpg [--cinematic] [--wait]
subpowers intone /abs/talk.mp4 --character me.jpg --location room.jpg --audio voice.wav [--aspect 9:16] [--resolution 1080p]
subpowers refs add NAME photo1.jpg photo2.heic ...     # save a reference set once (a person, room, product, world)
subpowers video "<prompt>" /abs/out.mp4 [--painter grok|higgsfield] [--model seedance_2_5|gemini_omni_flash_1_2|veo3_1|kling4_0] [--first IMG] [--ref IMG|VID]... [--audio FILE]... [--refs NAME] [--duration 1-15] [--aspect 16:9|9:16]
subpowers storyboard shots.txt /abs/outdir [--refs NAME] [--painter P] [--style "..."]
subpowers powers      # connected subscriptions, video engines, and MCP readiness
subpowers doctor      # live-checks every painter and names the exact fix
subpowers --version   # installed version
```

- stdout is the saved path (for `council`: one path per painter, then the `-all.jpg` side-by-side comparison board). Beside each image: `out.prompt.txt` receipt and `out.original.*` when resized or converted.
- Always inspect every generated image before showing, describing, or building on it.
- **Offer choices when taste matters:** run `--painter council` (3 subscription options side-by-side) or add `--with-higgsfield` (4 options when Higgsfield credits are approved) so the user picks the winner.

## Pick the Painter

| | `chatgpt` (default) | `antigravity` (`google` alias) | `grok` | `higgsfield` (opt-in, spends credits) |
|---|---|---|---|---|
| Plan | ChatGPT (`codex login`) | Google AI (`agy`) | The X Subscription (formerly SuperGrok, `grok login`) | Higgsfield (`higgsfield auth login`) |
| Model | OpenAI server-chosen image model | Nano Banana 2 (`gemini-3.1-flash-image` observed; actual ID in receipt) | `grok-imagine-image-2.0` requested; video `grok-imagine-video-1.5` | `nano_banana_2_1` default (~1.5 cr), `gpt_image_2_6` (~0.75 cr), `text2image_soul_v2` (~0.12 cr with `--soul-id`), video `seedance_2_5` (~35 cr) |
| Speed | 30 to 100 s | 20 to 120 s | 35 to 100 s | ~25 s image; 1 to 3 min video |
| Best at | text in images, product fidelity, logos | fast drafts, likeness from refs, photoreal | bold stylized looks, third opinion, included video with sound | trained Soul 2.0 character lock, pinned models, Seedance 2.5 / Kling 4.0 video |
| References | any number | up to 3 (extra dropped) | yes (first photo padded to target shape) | yes (`--image-references`, auto-uploaded; Soul 2.0 max 1 ref) |

### Honest Higgsfield Credit & Unlimited Rules
- `auto` and default `council` **never** spend Higgsfield credits. Opt in explicitly with `--painter higgsfield`, `--soul-id`, `--with-higgsfield`, or `SUBPOWERS_COUNCIL_PAINTERS` in `~/.subpowers/config`.
- Every Higgsfield image or video call prices the job first (`higgsfield generate cost`), refuses above `HIGGSFIELD_IMAGE_MAX_CREDITS` (default `2`), `HIGGSFIELD_VIDEO_MAX_CREDITS` (default `40`), or `HIGGSFIELD_INTONE_MAX_CREDITS` (default `120` for Intone ~96 cr), and logs estimated + actual balance before/after in the receipt.
- **Unlimited note:** Higgsfield gates free-unlimited (`use_unlim`) server-side to `higgsfield.ai` web, Claude chat, Claude Cowork, and ChatGPT. Calls through the `higgsfield` CLI or third-party MCP hosts spend plan credits transparently (Soul 2.0 `text2image_soul_v2` and Soul Cinematic `soul_cinematic` are only `0.12` credits). Never spoof client headers or claim CLI runs are free.
- **Multi-ref vs Soul 2.0 / Soul Cinematic on Higgsfield:** When combining multiple real room/environment + portrait `--ref` photos on Higgsfield, use `--model nano_banana_2_1` (or `gpt_image_2_6`), which accepts multiple references together. Reserve `text2image_soul_v2` / `--cinematic` (`soul_cinematic`, `21:9` anamorphic) with `--soul-id` for zero-ref text staging or a composition ref that already contains a person (an empty-room `--ref` locks Soul onto an empty room).
- **Omni Reference & Intone Video:** Use `--painter higgsfield --model gemini_omni_flash_1_2` (~18 cr; auto-routes `text-to-video`, `image-to-video`, `reference-to-video` omni ref, `edit`, `extend`) or `--model seedance_2_5` (~35 cr; `omni_reference` with `--ref` images/videos + `--audio` VO/rhythm). Use `subpowers intone out.mp4 --character IMG --location IMG --audio VOICE.wav` (~96 cr, audio 2-30s) for a 1080p talking avatar placed directly inside a real room photo. Note: Google AI Ultra's native Flow `@Character` / `@me` / 15s Omni live in the web UI (`labs.google/fx/tools/flow` and `gemini.google.com`), not yet in the `agy` CLI (`agy` gives Gemini 4 text/planning + Nano Banana 2 images).

## Avatars, Character Sheets & Soul IDs (`#3A3A3C` Neutral Gray Rule)

- `subpowers avatar` (alias `sheet`) generates a 5-view turnaround sheet (full-body front, left profile, right 3/4, back, and face close-up) on **flat dark neutral gray (`#3A3A3C`)** with shadowless soft light.
- Why `#3A3A3C` gray, never white or black: white acts like a giant reflector that bakes bright glare into faces in downstream video models; pure black crushes dark hair and wardrobe silhouettes.
- **Downstream scene guard:** whenever you pass a `#3A3A3C` character sheet as `--ref` to place the avatar in a real environment or video, include *"do not copy the plain gray background"* so the new scene lights the person naturally.
- Use `--style 3d-toon` for stylized 3D toon avatars, or train a reusable Higgsfield Soul 2.0 ID from 5 to 20 photos with `subpowers soul create NAME img1..img5 [--wait]` and call it via `--soul-id NAME`.

## References and Real People

- `--ref` / `--refs NAME` keep a person's face, a room/environment, a product, or a style consistent. iPhone HEIC converts automatically on macOS.
- **Never pass a photo of a different real person as a "setting" reference.** Painters borrow faces from every reference. Describe the set in words or crop the other person out first.
- Real proof stays real: never regenerate screenshots with numbers, logos, headlines, or real faces from scratch. Generate only the surround and composite the real pixels in.
- **Brand pictures come FROM real references, never words alone.** Pass `--ref` with the real logo/wordmark plate (cropped free of faces), product art, and a crop of the real set for light and palette.

## Match the Set (`--match-set`)

`--match-set VIDEO[@SECONDS]` extracts a frame, finds faces with YuNet, removes the people cleanly into a set plate, and passes that plate as a reference so overlays match the room's exact lighting, color palette, lens, and grain. Prefer raw horizontal footage.

## Prompts That Work

- Stage like a photographer: camera position, lens, light source and direction, who sits where, then look and moment.
- Photoreal realism cues: natural skin texture with visible pores, real flyaway hairs, authentic fabric creases, real motivated light sources (window, tungsten practical, bounce).
- Text control: state the exact allowed lettering and explicitly ban stray text on cups, shirts, and screens. Put long or exact typography on afterward in code.
- Never name a model inside the prompt.

## Storyboards, Video & Stop-Motion

- **Storyboards:** one shot per line in `shots.txt`, parallel painting into `storyboard.jpg`.
- **Video:** `subpowers video "<prompt>" out.mp4` defaults to **Grok Imagine 1.5** (included in The X Subscription, 1 to 15 s, 480p or 720p, sound + `--voice`). With no `--first`/`--ref`, it paints the first frame on your image plan first. Pass `--painter higgsfield [--model seedance_2_5|kling4_0|veo3_1]` for Higgsfield video (priced first, capped at `HIGGSFIELD_VIDEO_MAX_CREDITS`).
- **Stop-motion:** `subpowers stopmotion "<concept>" out.mp4` plans frames via `subpowers think`, anchors every frame to frame 1 (`--chain` optional), and encodes H.264 `.mp4` + looping `.webp` (`--resume` skips finished frames).

## Into a HyperFrames Project (`--into PROJECT`)

```bash
subpowers image "<prompt>" --into PROJECT --at 12.4 --duration 4 --layer-name "hero card" --snapshot
subpowers video "<prompt>" --into PROJECT --at 30 --place full --duration 6 --snapshot
subpowers stopmotion "<concept>" --into PROJECT --at 45 --frames 8 --snapshot
subpowers hf add --project PROJECT --file /abs/picture.png --at 12.4 --duration 4
subpowers hf remove --project PROJECT --layer gen-<slug>
```

- Validates `index.html` and runs `hyperframes lint` before and after; any lint error restores `index.html` byte for byte while keeping the painted media.
- `--place lower` (default) sits inside the safe box below captions; `full` is a cutaway; `box:x,y,w,h` is exact. Always inspect `--snapshot` before declaring done.

## Always the Best Model & Per-User Config

- Receipts distinguish requested and observed model IDs.
- User overrides live in `~/.subpowers/config` (`KEY=value`): `CHATGPT_IMAGE_DRIVERS`, `CHATGPT_IMAGE_EFFORT`, `AGY_IMAGE_EFFORT`, `GROK_IMAGE_EFFORT`, `GROK_IMAGE_MODEL`, `HIGGSFIELD_IMAGE_MODEL`, `HIGGSFIELD_IMAGE_RESOLUTION`, `HIGGSFIELD_IMAGE_MAX_CREDITS`, `HIGGSFIELD_VIDEO_MODEL`, `HIGGSFIELD_VIDEO_MAX_CREDITS`, `SUBPOWERS_COUNCIL_PAINTERS`. Respect them.

## Errors

| Message | Fix |
|---|---|
| `no painter is connected` | `subpowers doctor` lists what to install and log in |
| `not logged in with ChatGPT` / `live check ... rejected` | `codex logout && codex login` |
| `agy returned no models` | run `agy` once in a terminal and sign in |
| `grok is not logged in` (exit 3) | `grok login` with a grok.com account |
| `SuperGrok feature` / `X Subscription` (exit 4) | that grok.com plan tier lacks Grok Imagine; upgrade on The X Subscription |
| `unavailable under zero data retention` | run `grok`, type `/privacy`, choose Opt in, or add a video storage bucket |
| `not signed in to Higgsfield` / `over the cap` | `higgsfield auth login`; or raise `HIGGSFIELD_IMAGE_MAX_CREDITS` / `HIGGSFIELD_VIDEO_MAX_CREDITS` only with user approval |
| `dry (quota)` | plan quota spent; `auto` moves to the next painter |
| `no reference set 'NAME'` | `subpowers refs add NAME photo1.jpg ...` |
| `hf-into: refused` | check `index.html` and `hyperframes lint`; re-mount with `subpowers hf add` |

## Files

- `bin/subpowers`: front door CLI. `bin/subpowers-mcp`: shared zero-dependency stdio MCP server.
- `bin/chatgpt-image`, `bin/antigravity-image`, `bin/grok-image`, `bin/grok-video`, `bin/higgsfield-image`, `bin/higgsfield-video`, `bin/higgsfield-soul`: painters and Soul ID manager.
- `.claude-plugin/` + `.mcp.json` + `commands/`: Claude Code native plugin.
- `plugin.json` + `mcp_config.json` + `rules/subpowers.mdc` + `skills/subpowers/SKILL.md`: Antigravity & cross-harness native plugin.
- `bin/doctor`, `bin/canary`, `bin/hf-into`, `bin/set-plate`, `install.sh`.
