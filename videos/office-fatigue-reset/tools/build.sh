#!/usr/bin/env bash
# Rebuild pipeline: frames → index → transitions → local GSAP (CDN is unreachable from the render sandbox).
set -euo pipefail
cd "$(dirname "$0")/.."
S=../../.agents/skills/faceless-explainer/scripts
python3 tools/build_frames.py
node $S/assemble-index.mjs --storyboard ./STORYBOARD.md --hyperframes .
node $S/transitions.mjs inject --storyboard ./STORYBOARD.md --hyperframes .
node $S/transitions.mjs verify --storyboard ./STORYBOARD.md --index ./index.html
sed -i 's|https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js|assets/vendor/gsap.min.js|g' index.html
