<p align="center"><img src="assets/roadmap-studio.jpg" alt="A tiny photo studio with reference photos pinned to a corkboard" width="80%"></p>

# Roadmap

subpowers turns subscriptions people already pay for into powers any agent can use. Images are power #1. Here's where it goes next. Anything below is open for contributors: comment on the issue, or open one if it isn't there yet.

## Shipped

- [x] ChatGPT painter (OpenAI's current image model through `codex`)
- [x] Antigravity painter (Nano Banana 2 through `agy`)
- [x] Grok painter (Grok Imagine through the `grok` CLI, SuperGrok)
- [x] Reference photos (`--ref`), including iPhone HEIC
- [x] Receipt beside every image (prompt, model, C2PA signer, timings)
- [x] Always-newest helper model + daily codex update
- [x] `subpowers doctor` with live checks, one-command installer for Claude Code, Codex and other agents
- [x] Fan-out: `--painter all` paints with every connected subscription at once and builds a side-by-side sheet
- [x] Graceful fallback: a paused plan or spent quota moves to the next painter; nothing breaks
- [x] Reference sets: `subpowers refs add NAME photos...`, then `--refs NAME` anywhere
- [x] Character sheets: `subpowers sheet NAME out.png` (front, profiles, 3/4, back, face close-up)
- [x] Storyboards: `subpowers storyboard shots.txt outdir --refs NAME`
- [x] Best-quality defaults: every helper model at high effort, Grok on xAI's quality Imagine model (automatic fallback), reference photos padded to the asked shape
- [x] Your own defaults in `~/.subpowers/config` (helper model, effort, image model)
- [x] Council mode (`--painter council`), the image library, and `subpowers slideshow`
- [x] A test suite that runs every painter end to end against stand-in CLIs (no quota spent), in CI on Ubuntu and macOS
- [x] HyperFrames: `--into PROJECT` mounts a painted image, clip or stop-motion as one layer, lint-checked with byte-exact undo; `subpowers hf skill --attach` puts the chat skill in the HyperFrames app
- [x] `--match-set VIDEO[@S]`: paint on the set of your own footage (people removed from the plate first)
- [x] Higgsfield painter (opt-in, plan credits, priced first and capped): Nano Banana 2.1, Images 2.6, Grok Imagine 2.0 by name through the official `higgsfield` CLI

## Next: the video power (`subpowers video`)

Probed 2026-09-26, honestly:

- [x] **Grok Imagine video**: `subpowers video` (first frame, references, voices, 1 to 15 s, 480p/720p, with sound; paints a first frame when you give none)
- [ ] **Google Gemini Omni** (video from text plus up to 5 photo references, 10 s) is included in Google AI Plus, Pro and Ultra, but only inside the Gemini app, Flow and Vids. Not reachable from the `agy` CLI yet, so it needs a browser driver.
- [x] **Stop-motion on ChatGPT Images**: `subpowers stopmotion` plans the frames, paints frame 1, paints the rest from it, returns an mp4 and a looping webp (`--resume` after a spent quota)
- [ ] ChatGPT: no native video door (OpenAI shut Sora down in 2026); stop-motion from stills is the ChatGPT motion path.
- [ ] A daily probe that turns on a native CLI lane the day `generate_video` appears in `codex` or `agy` (checked 2026-11-13: agy 1.5.8 still has no video tool).
- [ ] **Animated GIFs on ChatGPT**: codex 0.168 added `features.image_generation_animation`; wire it as `subpowers gif` once a live run proves the plan allows it.
- [ ] **Higgsfield video** (`grok_video_v15`, `veo3_1`, `kling4_0`) as an opt-in `subpowers video --painter higgsfield`, priced first like the image painter.

## Next: the Studio

- [ ] **World sheets**: a small text file per world (palette, style anchors, recurring characters) that is added to every prompt that uses it
- [ ] **Studio page**: a local web page to browse every image with its receipt, compare painters side by side, and re-run a winner with one click
- [ ] **Shot planning**: `subpowers storyboard --plan "<concept>"` asks a subscription text model to write the shot list first

## Later: more powers

- [ ] **Browser lanes** for subscriptions with no CLI (web-only image and video models), run in a lightweight headless browser so it doesn't eat your RAM
- [x] **Plan in text**: `subpowers think` answers on the same subscriptions (JSON with a schema); it plans stop-motion frames today
- [ ] **Second opinion / copy**: ask the ChatGPT, Gemini or Grok model inside your plan for a draft or a critique, with the same receipt habit
- [ ] **Windows and Linux**: image steps no longer need macOS (Pillow or `sips`), and CI runs the suite on Ubuntu with stand-in CLIs. Still to do: real Linux reports with the actual CLIs, and Windows
- [ ] **More painters**: any subscription that ships an official CLI with a built-in image or video tool (HeyGen has none outside the HyperFrames app, and its generation spends HeyGen credits; ElevenLabs is audio only)

## Won't do

- API keys or paid per-call fallbacks. The whole point is the plan you already have.
- Anything that shares one person's login with another person.
