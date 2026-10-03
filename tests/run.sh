#!/usr/bin/env bash
# tests/run.sh: every painter and the front door end to end, against stand-in CLIs.
#
# Nothing real is called and no plan is spent: tests/stubs/{codex,agy,grok} replay what the
# real CLIs print and write real image files. Everything runs on a minimal PATH of symlinks
# with no sips and no timeout, like stock Linux (and stock macOS for timeout).
#
#   bash tests/run.sh                              sips hidden
#   SUBPOWERS_TEST_SIPS=1 bash tests/run.sh        the host's sips on that PATH too (macOS)
#   SUBPOWERS_TEST_NO_PILLOW=1 bash tests/run.sh   Pillow hidden from every python3 it starts
#
# Exit 0 when every check passes.
set -uo pipefail

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bin="$repo/bin"; stubs="$repo/tests/stubs"
# Physical path: install.sh compares HOME against `pwd -P`.
T="$(cd "$(mktemp -d "${TMPDIR:-/tmp}/subpowers-test.XXXXXX")" && pwd -P)"
trap 'rm -rf "$T"' EXIT
export PYTHONDONTWRITEBYTECODE=1

tools="bash sh env python3 perl cat cp mv rm ln mkdir mktemp dirname basename readlink date grep sed awk tr wc head tail ls find sort touch chmod sleep tar uname cut"
mkpath() {  # mkpath DIR [stub...]: symlinks to the basic tools plus the named stand-in CLIs
  local d="$1" t p; shift; mkdir -p "$d"
  for t in $tools; do p="$(type -P "$t" 2>/dev/null)" && ln -sf "$p" "$d/$t"; done
  for t in "$@"; do ln -sf "$stubs/$t" "$d/$t"; done
}
mkpath "$T/path" codex agy grok curl
if [[ -n "${SUBPOWERS_TEST_SIPS:-}" ]] && p="$(type -P sips)"; then ln -sf "$p" "$T/path/sips"; fi
mkpath "$T/path-nosips" codex agy grok curl
mkpath "$T/path-noclis"
mkdir -p "$T/nopil/PIL"
echo 'raise ImportError("Pillow hidden by tests/run.sh")' >"$T/nopil/PIL/__init__.py"
for d in path path-nosips path-noclis; do
  if [[ -e "$T/$d/sips" && "$d" != path ]] || [[ -e "$T/$d/timeout" ]]; then echo "setup: sips or timeout leaked into $d" >&2; exit 2; fi
done

pass=0; fail=0; failed=""; n=0; cur=""; rc=0; took=0
P="$T/path"; PYP=""
[[ -n "${SUBPOWERS_TEST_NO_PILLOW:-}" ]] && PYP="$T/nopil"

newcase() {  # newcase NAME: a fresh HOME, TMPDIR and stub logs
  cur="$1"; n=$((n+1)); C="$T/case$n"
  mkdir -p "$C/home" "$C/tmp" "$C/out"
  : >"$C/stub.log"; : >"$C/paints"
  echo "$cur"
}
run() {  # run [VAR=value...] CMD...: CMD in the case sandbox, bounded to $BOUND s; sets rc, took, $C/stdout, $C/stderr
  local t0; t0=$(date +%s)
  ( perl -e 'alarm shift; exec @ARGV' "${BOUND:-60}" \
      env -i HOME="$C/home" PATH="$P" TMPDIR="$C/tmp" STUB_LOG="$C/stub.log" STUB_PAINTS="$C/paints" \
        SUBPOWERS_NO_AUTOUPDATE=1 PYTHONDONTWRITEBYTECODE=1 ${PYP:+"PYTHONPATH=$PYP"} "$@" \
      >"$C/stdout" 2>"$C/stderr" </dev/null; exit $? ) 2>/dev/null   # a second command keeps the kill notice in here
  rc=$?; took=$(( $(date +%s) - t0 ))
}
ok()  { pass=$((pass+1)); printf '  ok    %s\n' "$1"; }
bad() { fail=$((fail+1)); failed="${failed}  ${cur}: $1
"; printf '  FAIL  %s\n' "$1"; }
check() { local what="$1"; shift; if "$@"; then ok "$what"; else bad "$what"; fi; }
exits() { [[ "$rc" == "$1" ]] || { echo "        exit $rc; stderr tail:"; tail -n 3 "$C/stderr" | cut -c1-160 | sed 's/^/          /'; return 1; }; }
has() { grep -qsE -- "$2" "$1"; }
hasnt() { [[ -f "$1" ]] && ! grep -qE -- "$2" "$1"; }
paints() {  # paints N [cli]: the stand-in CLIs painted exactly N images (of that CLI)
  local got; got="$(grep -c -- "${2:-.}" "$C/paints")"
  [[ "$got" == "$1" ]] || { echo "        painted $got times"; return 1; }
}
img() {  # img PATH FORMAT WxH
  local got; got="$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import fakeimg
f, w, h = fakeimg.dims(sys.argv[2]); print("%s %dx%d" % (f, w, h))' "$stubs" "$1" 2>/dev/null || echo missing)"
  [[ "$got" == "$2 $3" ]] || { echo "        $(basename "$1") is $got"; return 1; }
}
magic() {  # magic PATH HEX: the file starts with these bytes
  local got; got="$(python3 -c 'import sys; print(open(sys.argv[1], "rb").read(3).hex())' "$1" 2>/dev/null || echo missing)"
  [[ "$got" == "$2" ]] || { echo "        $(basename "$1") starts with $got"; return 1; }
}
printed() { [[ "$(tail -n 1 "$C/stdout")" == "$1" ]] || { echo "        printed: $(tail -n 1 "$C/stdout")"; return 1; }; }
called() { local m; m="$(grep -F -- "$1" "$C/stub.log")"; grep -qF -- "$2" <<<"$m"; }   # called <a stub call matching> <that also has>
pillow() { env -i HOME="$T" PATH="$P" ${PYP:+"PYTHONPATH=$PYP"} python3 -c 'import PIL' 2>/dev/null; }   # as the cases see it: no user site-packages

# Image ops exist when Pillow imports or sips is on the PATH. Without them a painter
# delivers its own file, in its own format and size, and says so.
OPS=""; { [[ -e "$P/sips" ]] || pillow; } && OPS=1
echo "== painters (sips $([[ -e "$P/sips" ]] && echo present || echo hidden), Pillow $(pillow && echo present || echo hidden))"

newcase "chatgpt: text to png at an asked size"
run bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png" --size 1024x1024
check "exit 0" exits 0
check "prints the image path" printed "$C/out/mug.png"
if [[ -n "$OPS" ]]; then check "png 1024x1024" img "$C/out/mug.png" png 1024x1024
else check "png at the painter's 1254x1254" img "$C/out/mug.png" png 1254x1254; fi
check "receipt" test -f "$C/out/mug.prompt.txt"
check "one paint" paints 1 codex
check "receipt carries token usage" has "$C/out/mug.prompt.txt" "tokens: input=25000 output=120$"

newcase "chatgpt: a helper that burns 200k input tokens is flagged"
run STUB_CODEX_INPUT_TOKENS=200000 bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png"
check "exit 0" exits 0
check "warns on stderr" has "$C/stderr" "the helper did more than paint"

newcase "chatgpt: a .jpg ask delivers JPEG bytes"
run bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.jpg"
check "exit 0" exits 0
if [[ -n "$OPS" ]]; then
  check "prints the jpg" printed "$C/out/mug.jpg"
  check "JPEG magic bytes" magic "$C/out/mug.jpg" ffd8ff
  check "receipt says it was converted" has "$C/out/mug.prompt.txt" "converted png -> jpg"
  check "signed png original kept" img "$C/out/mug.original.png" png 1254x1254
else
  check "prints the delivered png" printed "$C/out/mug.png"
  check "PNG magic bytes" magic "$C/out/mug.png" 89504e
  check "no mislabeled jpg" test ! -e "$C/out/mug.jpg"
fi
check "one paint" paints 1 codex

newcase "antigravity: text to png at an asked size"
run bash "$bin/antigravity-image" "a red mug" "$C/out/mug.png" --size 1024x1024
check "exit 0" exits 0
if [[ -n "$OPS" ]]; then
  check "prints the image path" printed "$C/out/mug.png"
  check "png 1024x1024" img "$C/out/mug.png" png 1024x1024
else
  check "prints the delivered jpg" printed "$C/out/mug.jpg"
  check "jpeg 1024x1024" img "$C/out/mug.jpg" jpeg 1024x1024
fi
check "receipt" test -f "$C/out/mug.prompt.txt"
check "one paint" paints 1 agy

newcase "antigravity: 16:9 jpg cropped and resized to 1600x900"
run bash "$bin/antigravity-image" "a harbor at dawn" "$C/out/harbor.jpg" --size 1600x900
check "exit 0" exits 0
check "prints the image path" printed "$C/out/harbor.jpg"
if [[ -n "$OPS" ]]; then check "jpeg 1600x900" img "$C/out/harbor.jpg" jpeg 1600x900
else check "jpeg at the painter's 1376x768" img "$C/out/harbor.jpg" jpeg 1376x768; fi
check "receipt" test -f "$C/out/harbor.prompt.txt"
check "one paint" paints 1 agy

newcase "grok: text only, png at 1920x1080"
run bash "$bin/grok-image" "a fox on a rooftop" "$C/out/fox.png" --size 1920x1080
check "exit 0" exits 0
if [[ -n "$OPS" ]]; then
  check "prints the image path" printed "$C/out/fox.png"
  check "png 1920x1080" img "$C/out/fox.png" png 1920x1080
else
  check "prints the delivered jpg" printed "$C/out/fox.jpg"
  check "jpeg at the painter's 1376x768" img "$C/out/fox.jpg" jpeg 1376x768
fi
check "receipt" test -f "$C/out/fox.prompt.txt"
check "one paint" paints 1 grok
check "receipt labels the Imagine model as requested" has "$C/out/fox.prompt.txt" "^  image model requested: grok-imagine-image-quality"
check "receipt claims no answering model" hasnt "$C/out/fox.prompt.txt" "^  image model:"

newcase "grok-video: a first frame becomes a clip"
fakepng="$C/first.png"; python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import fakeimg; fakeimg.png(sys.argv[2], 1080, 1920)' "$stubs" "$fakepng"
run bash "$bin/grok-video" "the fox turns toward the camera" "$C/out/fox.mp4" --first "$fakepng" --aspect 9:16 --duration 6 --resolution 720p
check "exit 0" exits 0
check "prints the video path" printed "$C/out/fox.mp4"
check "an mp4 was delivered" has "$C/out/fox.mp4" "ftyp"
check "receipt" test -f "$C/out/fox.prompt.txt"
check "receipt names the tool" has "$C/out/fox.prompt.txt" "reference_to_video"
check "receipt records the ask" has "$C/out/fox.prompt.txt" "asked: 6s 720p 9:16"
check "one paint" paints 1 grok

newcase "grok-video: needs an image or a voice"
run bash "$bin/grok-video" "a fox" "$C/out/fox.mp4"
check "exit 2" exits 2
check "says why" has "$C/stderr" "video starts from an image"
check "no paint" paints 0 grok

newcase "grok-video: privacy mode names the fix"
run STUB_GROK_ZDR=1 bash "$bin/grok-video" "a fox" "$C/out/fox.mp4" --first "$fakepng"
check "exit 1" exits 1
check "names /privacy" has "$C/stderr" "/privacy and choose Opt in"
check "nothing delivered" test ! -e "$C/out/fox.mp4"

newcase "video: no image, so it paints a first frame, then animates it"
run bash "$bin/subpowers" video "a fox on a snowy rooftop" "$C/out/clip.mp4" --aspect 9:16
check "exit 0" exits 0
check "prints the clip path" printed "$C/out/clip.mp4"
check "a first frame was painted" test -n "$(ls "$C/out"/clip.first.* 2>/dev/null)"
check "says it painted the first frame" has "$C/stderr" "painting the first frame"
check "the clip exists" has "$C/out/clip.mp4" "ftyp"

newcase "grok: --ref edits into a 4:3 png"
python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import fakeimg; fakeimg.png(sys.argv[2], 800, 600)' "$stubs" "$C/ref.png"
run bash "$bin/grok-image" "the same product on a beach" "$C/out/beach.png" --size 1024x768 --ref "$C/ref.png"
check "exit 0" exits 0
if [[ -n "$OPS" ]]; then check "png 1024x768" img "$C/out/beach.png" png 1024x768
else check "jpeg at the painter's 1184x864" img "$C/out/beach.jpg" jpeg 1184x864; fi
check "receipt" test -f "$C/out/beach.prompt.txt"
check "one paint" paints 1 grok
check "image_edit got the reference" called '"grok-paint"' '"tool": "image_edit", "aspect": "4:3", "images": 1'

newcase "front door: auto paints once"
run bash "$bin/subpowers" image "a red mug" "$C/out/mug.png"
check "exit 0" exits 0
check "one paint in total" paints 1

echo "== think: a text answer on the same subscriptions"
newcase "think: chatgpt answers"
run bash "$bin/think" "name one color"
check "exit 0" exits 0
check "prints the answer" printed "stub answer"
check "asked codex for text, read-only, no shell" called '"codex"' '"-o"'
check "the call is read-only" called '"codex"' '"read-only"'
check "no image was painted" paints 0

newcase "think: --json-schema returns one clean JSON object"
echo '{"type":"object","properties":{"a":{"type":"integer"}},"required":["a"]}' >"$C/schema.json"
run STUB_THINK_ANSWER='Sure! ```json
{"a": 1}
```' bash "$bin/think" "give me a" --json-schema "$C/schema.json"
check "exit 0" exits 0
check "prints only the object" printed '{"a": 1}'
check "codex was held to the schema" called '"codex"' '"--output-schema"'

newcase "think: an answer that is not JSON fails loudly"
echo '{"type":"object","properties":{"a":{"type":"integer"}},"required":["a"]}' >"$C/schema.json"
run STUB_THINK_ANSWER='no json here' bash "$bin/think" "give me a" --json-schema "$C/schema.json" --thinker chatgpt
check "exit 1" exits 1
check "says why" has "$C/stderr" "did not answer with valid JSON"

newcase "think: ChatGPT logged out, Google answers"
run STUB_CODEX_LOGGED_OUT=1 bash "$bin/think" "name one color"
check "exit 0" exits 0
check "antigravity answered" called '"agy-think"' 'stub answer'
check "says who answered" has "$C/stderr" "antigravity answered"

newcase "think: nothing connected"
P="$T/path-noclis" run bash "$bin/think" "name one color"
check "exit 3" exits 3
check "points at doctor" has "$C/stderr" "subpowers doctor"

echo "== stopmotion: frames painted from frame 1, then a clip"
mkpath "$T/path-ff" codex agy grok curl ffmpeg
if [[ -n "${SUBPOWERS_TEST_SIPS:-}" ]] && p="$(type -P sips)"; then ln -sf "$p" "$T/path-ff/sips"; fi

newcase "stopmotion: plans 4 frames, paints frame 1, then 3 from it, makes an mp4"
P="$T/path-ff" run bash "$bin/subpowers" stopmotion "a paper boat crosses a wooden desk" "$C/out/boat.mp4" --frames 4 --fps 4
check "exit 0" exits 0
check "prints the clip" printed "$C/out/boat.mp4"
check "the clip exists" has "$C/out/boat.mp4" "ftyp"
check "four frames painted" paints 4 codex
check "four frame files" test "$(ls "$C/out/boat.frames"/frame-0[1-4].png 2>/dev/null | wc -l | tr -d ' ')" = 4
check "the plan was asked for exactly 4 frames" called '"codex"' 'exactly 4 frames'
check "the plan is kept" has "$C/out/boat.frames/plan.txt" "stub frame 4"
check "the planner is told never to draw the path" called '"codex"' 'no dotted lines, paths, arrows or marks'
check "every frame is told to add no marks" has "$C/out/boat.frames/frame-03.prompt.txt" "no lines, paths, arrows or marks"
check "frame 2 was painted from frame 1" has "$C/out/boat.frames/frame-02.prompt.txt" "references: 1 .*frame-01"
check "frame 4 was painted from frame 1" has "$C/out/boat.frames/frame-04.prompt.txt" "references: 1 .*frame-01"
check "encoded for every phone" called '"ffmpeg"' '"yuv420p"'
check "starts playing before it downloads" called '"ffmpeg"' '"+faststart"'
check "encodes an image sequence, never the concat demuxer (the cut guard's line)" called '"ffmpeg"' '"-framerate"'
check "no concat anywhere" hasnt "$C/stub.log" '"concat"'
check "receipt names the door" has "$C/out/boat.prompt.txt" "door: subpowers stopmotion \(chatgpt\)"
check "receipt keeps the concept" has "$C/out/boat.prompt.txt" "a paper boat crosses a wooden desk"
check "indexed in the library" has "$C/home/.subpowers/library.jsonl" "boat.mp4"
if pillow; then check "a looping webp too" magic "$C/out/boat.webp" 524946; fi

newcase "stopmotion --chain: each frame is painted from the one before"
P="$T/path-ff" run bash "$bin/subpowers" stopmotion "a paper boat crosses a wooden desk" "$C/out/boat.mp4" --frames 3 --chain
check "exit 0" exits 0
check "frame 3 was painted from frame 2" has "$C/out/boat.frames/frame-03.prompt.txt" "references: 1 .*frame-02"
check "receipt says chained" has "$C/out/boat.prompt.txt" "mode: chained"

newcase "stopmotion --plan: your own frame list, no planner call"
printf 'a boat at the left edge of a desk\nthe boat in the middle\n\nthe boat at the right edge\n' >"$C/plan.txt"
P="$T/path-ff" run bash "$bin/subpowers" stopmotion "boat" "$C/out/boat.mp4" --plan "$C/plan.txt"
check "exit 0" exits 0
check "three frames, one per line" paints 3 codex
check "no planner call" hasnt "$C/stub.log" '"codex-think"'

newcase "stopmotion without ffmpeg: the loop still ships"
run bash "$bin/subpowers" stopmotion "a paper boat" "$C/out/boat.mp4" --frames 3
check "exit 0" exits 0
check "names ffmpeg" has "$C/stderr" "ffmpeg"
check "receipt does not claim an mp4" hasnt "$C/out/boat.prompt.txt" "in the mp4"
if pillow; then check "prints the webp" printed "$C/out/boat.webp"
else check "prints the frames folder" printed "$C/out/boat.frames"; fi

newcase "stopmotion --resume: keeps the plan and the painted frames, paints only what is missing"
P="$T/path-ff" run bash "$bin/subpowers" stopmotion "a paper boat" "$C/out/boat.mp4" --frames 3
rm -f "$C/out/boat.frames/frame-03.png" "$C/out/boat.mp4"; : >"$C/paints"; : >"$C/stub.log"
P="$T/path-ff" run bash "$bin/subpowers" stopmotion "a paper boat" "$C/out/boat.mp4" --frames 3 --resume
check "exit 0" exits 0
check "only the missing frame was painted" paints 1 codex
check "no new plan" hasnt "$C/stub.log" '"codex-think"'
check "the clip is back" has "$C/out/boat.mp4" "ftyp"

newcase "stopmotion: one painter per clip"
P="$T/path-ff" run bash "$bin/subpowers" stopmotion "a paper boat" "$C/out/boat.mp4" --painter council
check "exit 2" exits 2
check "says why" has "$C/stderr" "one painter per clip"
check "nothing painted" paints 0

echo "== a paint that cannot be delivered"
for p in chatgpt antigravity grok; do
  newcase "$p: delivery fails after the paint"
  mkdir -p "$C/out/x.prompt.txt"   # the receipt cannot be written
  run bash "$bin/$p-image" "a red mug" "$C/out/x.png"
  check "exit 5" exits 5
  check "one paint" paints 1
done
newcase "front door: exit 5 is final, no second paint on another plan"
mkdir -p "$C/out/x.prompt.txt"
run bash "$bin/subpowers" image "a red mug" "$C/out/x.png"
check "exit 5" exits 5
check "one paint in total" paints 1

echo "== no image ops (no Pillow, no sips)"
P="$T/path-nosips"; PYP="$T/nopil"

newcase "antigravity: delivers its own jpg when asked for png"
run bash "$bin/antigravity-image" "a red mug" "$C/out/mug.png" --size 1024x1024
check "exit 0" exits 0
check "prints the delivered jpg" printed "$C/out/mug.jpg"
check "jpeg 1024x1024" img "$C/out/mug.jpg" jpeg 1024x1024
check "no mislabeled png" test ! -e "$C/out/mug.png"
check "warns on stderr" has "$C/stderr" "WARNING"
check "receipt says why" has "$C/out/mug.prompt.txt" "image ops"
check "one paint" paints 1 agy

newcase "grok: delivers its own jpg when asked for png"
run bash "$bin/grok-image" "a fox on a rooftop" "$C/out/fox.png"
check "exit 0" exits 0
check "prints the delivered jpg" printed "$C/out/fox.jpg"
check "jpeg 1024x1024" img "$C/out/fox.jpg" jpeg 1024x1024
check "receipt says why" has "$C/out/fox.prompt.txt" "image ops"
check "one paint" paints 1 grok

newcase "chatgpt: delivers its own png when asked for jpg"
run bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.jpeg"
check "exit 0" exits 0
check "prints the delivered png" printed "$C/out/mug.png"
check "PNG magic bytes" magic "$C/out/mug.png" 89504e
check "no mislabeled jpeg" test ! -e "$C/out/mug.jpeg"
check "warns on stderr" has "$C/stderr" "WARNING"
check "receipt says why" has "$C/out/mug.prompt.txt" "image ops"

newcase "chatgpt: keeps the painter's size"
run bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png" --size 1024x1024
check "exit 0" exits 0
check "png 1254x1254" img "$C/out/mug.png" png 1254x1254
check "receipt says why" has "$C/out/mug.prompt.txt" "NOT resized.*image ops"
check "one paint" paints 1 codex

newcase "front door: indexes the file it delivered"
run bash "$bin/subpowers" image "a red mug" "$C/out/mug.png" --painter antigravity
check "exit 0" exits 0
check "prints the delivered jpg" printed "$C/out/mug.jpg"
run python3 "$bin/library" find --json
check "library holds the jpg" has "$C/stdout" 'mug\.jpg'

newcase "storyboard: counts shots delivered as jpg"
printf 'a fox wakes up\na fox finds a scarf\n' >"$C/shots.txt"
run bash "$bin/subpowers" storyboard "$C/shots.txt" "$C/out/board" --painter grok
check "exit 0" exits 0
check "2 of 2 shots" has "$C/stderr" "2 of 2 shots painted"
check "says the sheet needs Pillow" has "$C/stderr" "no side-by-side sheet.*Pillow"

newcase "council: says why there is no side-by-side sheet"
run bash "$bin/subpowers" image "a red mug" "$C/out/mug.png" --painter council
check "exit 0" exits 0
check "three paints" paints 3
check "says the sheet needs Pillow" has "$C/stderr" "no side-by-side sheet.*Pillow"

newcase "doctor: names what needs Pillow"
run bash "$bin/doctor"
check "exit 0 (painters are ready)" exits 0
check "WARN line names the Pillow features and the install" has "$C/stdout" "WARN .*Pillow.*council.*slideshow.*pip install"

P="$T/path"; PYP=""; [[ -n "${SUBPOWERS_TEST_NO_PILLOW:-}" ]] && PYP="$T/nopil"

echo "== no timeout(1) on PATH"
newcase "grok: GROK_IMAGE_TIMEOUT still ends a call that never answers"
BOUND=20 run STUB_GROK_HANG=25 GROK_IMAGE_TIMEOUT=2 bash "$bin/grok-image" "a fox" "$C/out/fox.jpg"
check "exit 1" exits 1
check "says it timed out" has "$C/stderr" "timed out"
check "within 12 s (took ${took}s)" test "$took" -lt 12

echo "== CLIs that keep talking after the answer (SIGPIPE under pipefail)"
newcase "powers: every logged-in plan is ON"
run STUB_CHATTY=1 bash "$bin/subpowers" powers
check "chatgpt ON" has "$C/stdout" "chatgpt +ON"
check "antigravity ON" has "$C/stdout" "antigravity +ON"
check "grok ON" has "$C/stdout" "grok +ON"
newcase "chatgpt: paints, isolated with --ignore-user-config"
run STUB_CHATTY=1 bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png"
check "exit 0" exits 0
check "--ignore-user-config passed" called '"exec"' '"--ignore-user-config"'
newcase "grok: paints"
run STUB_CHATTY=1 bash "$bin/grok-image" "a fox" "$C/out/fox.jpg"
check "exit 0" exits 0
newcase "doctor: sees the ChatGPT login"
run STUB_CHATTY=1 bash "$bin/doctor"
check "login PASS" has "$C/stdout" "PASS +login stored: ChatGPT"

echo "== doctor drives the same car as the painters"
newcase "doctor: live check isolated like chatgpt-image"
run bash "$bin/doctor"
check "exit 0" exits 0
for flag in 'model_provider=\"openai\"' 'openai_base_url=' 'mcp_servers={}' 'project_doc_max_bytes=0' 'features.shell_tool=false' '--ignore-user-config'; do
  check "pong call has $flag" called 'Reply with exactly: pong' "$flag"
done
check "antigravity helper is the painter's default (high)" has "$C/stdout" "helper model: gemini-[0-9.]+-flash-high"
newcase "doctor: reads ~/.subpowers/config"
mkdir -p "$C/home/.subpowers"
printf 'CHATGPT_IMAGE_DRIVERS=gpt-test-sol:default\nAGY_IMAGE_EFFORT=low\n' >"$C/home/.subpowers/config"
run bash "$bin/doctor"
check "pong call pinned to the configured helper" called 'Reply with exactly: pong' '"-m", "gpt-test-sol"'
check "reports the configured ChatGPT helper" has "$C/stdout" "gpt-test-sol"
check "reports the configured antigravity helper" has "$C/stdout" "helper model: gemini-[0-9.]+-flash-low"
newcase "doctor: a dry first helper falls through, like the painter"
mkdir -p "$C/home/.subpowers"
printf 'CHATGPT_IMAGE_DRIVERS=gpt-test-sol:default\n' >"$C/home/.subpowers/config"
run STUB_CODEX_DRY_MODEL=gpt-test-sol bash "$bin/doctor"
check "live check PASS on the next helper" has "$C/stdout" "PASS +live check"
newcase "chatgpt: a dry first helper falls through to the next, one paint"
run STUB_CODEX_DRY_MODEL=gpt-test-sol CHATGPT_IMAGE_DRIVERS=gpt-test-sol:default bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png"
check "exit 0" exits 0
check "one paint" paints 1 codex
check "receipt names the helper that painted" has "$C/out/mug.prompt.txt" "driver model: default"
newcase "doctor: a spent quota is not a login problem"
run STUB_CODEX_LIVE_ERROR="You've hit your usage limit. Try again in 3 hours." bash "$bin/doctor"
check "names the quota" has "$C/stdout" "FAIL .*(quota|usage limit)"
check "no logout advice" hasnt "$C/stdout" "codex logout"
newcase "doctor: a network failure is named as one"
run STUB_CODEX_LIVE_ERROR="error sending request for url (https://chatgpt.com/backend-api/codex/responses)" bash "$bin/doctor"
check "names the network" has "$C/stdout" "FAIL .*network"
check "no logout advice" hasnt "$C/stdout" "codex logout"
newcase "doctor: an auth failure keeps the login advice"
run STUB_CODEX_LIVE_ERROR="unexpected status 401 Unauthorized" bash "$bin/doctor"
check "logout and login" has "$C/stdout" "FAIL .*codex logout && codex login"

echo "== codex daily update"
newcase "update-codex: a report does not stamp the daily check"
stamp="$C/home/.cache/subpowers/codex-update-check"
run STUB_NPM_VERSION=0.158.0 bash "$bin/doctor"
check "doctor leaves no stamp" test ! -e "$stamp"
run STUB_NPM_VERSION=0.158.0 bash "$bin/update-codex"
check "report exits 1 (behind)" exits 1
check "report leaves no stamp" test ! -e "$stamp"
run STUB_NPM_VERSION=0.158.0 bash "$bin/update-codex" --daily --apply
check "apply exits 0" exits 0
check "apply ran codex update" called '"codex"' '["update"]'
check "apply stamps" test -e "$stamp"

echo "== canary: the drift radar"
# The canary talks to launchctl and osascript through PATH; stubs stand in so
# no test ever touches the real ~/Library or shows a real notification.
ln -sf "$stubs/launchctl" "$P/launchctl"
ln -sf "$stubs/osascript" "$P/osascript"

newcase "canary: every contract item present"
run python3 "$bin/canary"
check "exit 0" exits 0
check "codex line OK" has "$C/stdout" "codex +0\\.157\\.0 +11/11 +OK"
check "agy line OK" has "$C/stdout" "agy +1\\.2\\.11 +9/9 +OK"
check "grok line OK" has "$C/stdout" "grok +1\\.0\\.41 +13/13 +OK"
check "no drift" has "$C/stdout" "OK: no drift"
check "state saved" test -f "$C/home/.subpowers/canary/state.json"
check "no drift file on a clean run" test -z "$(ls "$C/home/.subpowers/canary"/drift-*.md 2>/dev/null)"

newcase "canary: a grok --help that lost --disallowed-tools is drift"
run STUB_GROK_HELP_DROP=--disallowed-tools python3 "$bin/canary"
check "exit 1" exits 1
check "names the CLI and the exact flag" has "$C/stdout" "DRIFT grok .*--disallowed-tools"
check "codex and agy still OK" has "$C/stdout" "codex .*OK"
driftmd="$(ls "$C/home/.subpowers/canary"/drift-*.md 2>/dev/null | head -n 1)"
check "drift report written" test -s "$driftmd"
check "report path printed" has "$C/stdout" "drift report written"
check "report carries a vendor-drift issue body" has "$driftmd" "vendor-drift"
check "report names the flag" has "$driftmd" "--disallowed-tools"
check "report says it stays local" has "$driftmd" "never posts"

newcase "canary: a model list that fails once is retried, not called drift"
run STUB_AGY_MODELS_FAIL=1 SUBPOWERS_CANARY_RETRY_PAUSE=0 python3 "$bin/canary"
check "exit 0" exits 0
check "agy line OK after the retry" has "$C/stdout" "agy +1\\.2\\.11 +9/9 +OK"
check "no drift" has "$C/stdout" "OK: no drift"

newcase "canary: a model list that keeps failing is drift that quotes the answer"
run STUB_AGY_MODELS_FAIL=9 SUBPOWERS_CANARY_RETRY_PAUSE=0 python3 "$bin/canary"
check "exit 1" exits 1
check "says what agy answered" has "$C/stdout" "answered: Error: failed to fetch models"

newcase "canary: a version change between two runs is reported"
run STUB_GROK_VERSION=1.0.40 python3 "$bin/canary"
check "first run exit 0" exits 0
run STUB_GROK_VERSION=1.0.42 python3 "$bin/canary"
check "second run exit 0 (contract holds)" exits 0
check "reports old -> new" has "$C/stdout" "1\\.0\\.40 -> 1\\.0\\.42"
check "still no drift" has "$C/stdout" "OK: no drift.*version change"

newcase "canary: --json is machine-readable"
run python3 "$bin/canary" --json
check "exit 0" exits 0
check "one JSON object, status ok, versions in it" python3 -c '
import json, sys
d = json.load(open(sys.argv[1]))
assert d["status"] == "ok" and d["exit"] == 0 and d["drift_file"] is None
assert d["clis"]["codex"]["version"] == "0.157.0" and d["clis"]["grok"]["items_ok"] == 13' "$C/stdout"

newcase "canary: --live also runs the doctor"
run python3 "$bin/canary" --live
check "exit 0" exits 0
check "doctor verdict in the report" has "$C/stdout" "doctor: READY"

newcase "canary: --notify on drift calls osascript"
if [[ "$(uname -s)" == "Darwin" ]]; then
  run STUB_GROK_HELP_DROP=--prompt-file python3 "$bin/canary" --notify
  check "exit 1" exits 1
  check "osascript showed the notification" called '"osascript"' 'display notification'
else
  ok "skipped on $(uname -s) (notifications are macOS-only)"
fi

newcase "canary: --install-launchagent writes and loads the agent"
plist="$C/home/Library/LaunchAgents/com.subpowers.canary.plist"
run python3 "$bin/canary" --install-launchagent
check "exit 0" exits 0
check "plist written under the (temp) HOME" test -f "$plist"
check "daily StartCalendarInterval" has "$plist" "StartCalendarInterval"
check "at 07:15" has "$plist" "<key>Hour</key>"
check "minute 15" has "$plist" "<integer>15</integer>"
check "runs --live --notify" has "$plist" "--notify"
check "logs under SUBPOWERS_HOME" has "$plist" "\.subpowers/canary/launchd\.log"
check "explicit PATH EnvironmentVariables" has "$plist" "/opt/homebrew/bin"
check "keeps your shell's PATH order first (checks the CLIs you actually use)" has "$plist" "<string>$P:"
check "launchctl bootstrap called" called '"launchctl"' '"bootstrap"'
run python3 "$bin/canary" --install-launchagent
check "second install exit 0 (idempotent)" exits 0
check "reload bootouts the old agent first" called '"launchctl"' '"bootout"'

newcase "doctor: sees the canary LaunchAgent once installed"
run python3 "$bin/canary" --install-launchagent
run bash "$bin/doctor"
check "exit 0" exits 0
check "INFO says installed" has "$C/stdout" "INFO +canary LaunchAgent installed"

newcase "canary: --uninstall-launchagent reverses it"
plist="$C/home/Library/LaunchAgents/com.subpowers.canary.plist"
run python3 "$bin/canary" --install-launchagent
run python3 "$bin/canary" --uninstall-launchagent
check "exit 0" exits 0
check "plist removed" test ! -e "$plist"
check "launchctl bootout called" called '"launchctl"' '"bootout"'
run python3 "$bin/canary" --uninstall-launchagent
check "uninstall is idempotent" exits 0

newcase "doctor: INFO, never a failure, when the canary agent is missing"
run bash "$bin/doctor"
check "exit 0" exits 0
check "INFO names the install command" has "$C/stdout" "INFO +canary LaunchAgent not installed.*--install-launchagent"
check "no WARN or FAIL about it" hasnt "$C/stdout" "(WARN|FAIL) +canary"

newcase "subpowers canary: wired in the front door"
run bash "$bin/subpowers" canary
check "exit 0" exits 0
check "the report" has "$C/stdout" "OK: no drift"

newcase "canary: no CLIs installed is not drift"
P="$T/path-noclis"
run python3 "$bin/canary"
check "exit 0" exits 0
check "says absent, not drift" has "$C/stdout" "absent"
P="$T/path"

newcase "canary: usage errors exit 2"
run python3 "$bin/canary" --nonsense
check "exit 2" exits 2

newcase "update-codex: a post-update contract break warns loudly"
run STUB_NPM_VERSION=0.158.0 bash "$bin/update-codex" --apply
check "exit 0" exits 0
check "no warning when the contract holds" hasnt "$C/stderr" "rollback"
run STUB_NPM_VERSION=0.159.0 STUB_CODEX_HELP_DROP=--json bash "$bin/update-codex" --apply
check "exit 0 still (no automatic rollback)" exits 0
check "loud warning names the break" has "$C/stderr" "WARNING codex .*broke the subpowers contract"
check "warning names the missing flag" has "$C/stderr" "--json"
check "warning names the rollback with the previous version" has "$C/stderr" "npm i -g @openai/codex@0\\.158\\.0"
newcase "update-codex: the painter updates codex daily by default"
run env -u SUBPOWERS_NO_AUTOUPDATE STUB_NPM_VERSION=0.158.0 bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png"
check "exit 0" exits 0
check "ran codex update" called '"codex"' '["update"]'
newcase "update-codex: SUBPOWERS_NO_AUTOUPDATE=1 in ~/.subpowers/config turns it off"
mkdir -p "$C/home/.subpowers"; printf 'SUBPOWERS_NO_AUTOUPDATE=1\n' >"$C/home/.subpowers/config"
run env -u SUBPOWERS_NO_AUTOUPDATE STUB_NPM_VERSION=0.158.0 bash "$bin/chatgpt-image" "a red mug" "$C/out/mug.png"
check "exit 0" exits 0
check "no codex update" bash -c '! grep -F "\"codex\"" "$1" | grep -qF "[\"update\"]"' _ "$C/stub.log"

echo "== install and help"
newcase "install: a fresh machine with no CLIs"
P="$T/path-noclis"
run bash "$repo/install.sh"
check "exit 0" exits 0
check "its next steps name all three logins" has "$C/stdout" "Grok: +grok login"
P="$T/path"
newcase "help: prints the header only"
run bash "$bin/subpowers" help
check "exit 0" exits 0
check "usage text" has "$C/stderr" "Usage:"
check "no code in the help" hasnt "$C/stderr" "set -euo"
newcase "version: --version prints the version"
run bash "$bin/subpowers" --version
check "exit 0" exits 0
check "names the version" has "$C/stdout" "^subpowers [0-9]+\.[0-9]+\.[0-9]+"

echo "== an empty plan says so"
newcase "antigravity: the image tool is out of quota"
run STUB_AGY_IMAGE_QUOTA=1 bash "$bin/antigravity-image" "a red mug" "$C/out/mug.png" --size 1024x1024
check "exit 1" exits 1
check "says dry (quota)" has "$C/stderr" "dry \\(quota\\)"
check "says when it resets" has "$C/stderr" "resets in 3h57m27s"
check "no never-called guess" hasnt "$C/stderr" "may not have been called"
newcase "grok: the CLI usage balance is empty"
run STUB_GROK_BALANCE=1 bash "$bin/grok-image" "a red mug" "$C/out/mug.png" --size 1024x1024
check "exit 1" exits 1
check "says dry (quota)" has "$C/stderr" "dry \\(quota\\)"
check "quotes grok's reason" has "$C/stderr" "usage balance exhausted"
check "no policy-refusal guess" hasnt "$C/stderr" "policy refusal"
newcase "auto: an empty plan hands off to the next painter"
run STUB_AGY_IMAGE_QUOTA=1 STUB_GROK_BALANCE=1 bash "$bin/subpowers" image "a red mug" "$C/out/mug.png" --painter auto
check "exit 0" exits 0

echo "== bad input gets a plain answer"
printf 'a wide shot\n' >"$T/shots.txt"
newcase "storyboard: a flag with no value"
run bash "$bin/subpowers" storyboard "$T/shots.txt" "$C/out/board" --painter
check "exit 2" exits 2
check "names the flag" has "$C/stderr" "--painter needs a value"
check "no bash internals" hasnt "$C/stderr" "unbound variable"
newcase "image: an unknown painter lists the real names"
run bash "$bin/subpowers" image "a red mug" "$C/out/mug.png" --painter dalle
check "exit 2" exits 2
check "offers google and council" has "$C/stderr" "chatgpt, google, grok, council"

echo
echo "$pass passed, $fail failed"
[[ $fail -eq 0 ]] && exit 0
printf 'failed:\n%s' "$failed"
exit 1
