# Demo video kit

Proven on Playhead and Parity. Narration in your voice clone, word timings drive every animation.

1. Write the script in `vo.json` as `[name, narration]` lines (under 3 minutes in total; 90+ s of the product on screen).
2. `python make_vo.py` makes `vo/<name>.mp3` + word timings (ElevenLabs + AssemblyAI; keys come from Bots/hackathon_scout/.env).
   Spell years out in words ("twenty twenty"), or the voice may read "2020" oddly.
3. Slides: `scenes/<name>.html` with `data-cue="word"` on elements (they appear when that word is spoken). Uses `p.css` + `anim.js`.
4. Screen recordings of the real app: add scenes to `rec.py` (`SCENES`), times are cue WORDS, not seconds.
   Schedule steps yourself with setTimeout (absolute times); don't rely on an app's own sequential `run()` helper.
5. `python render.py` → `demo.mp4` (1080p, crossfades, -16 LUFS). For 4K, copy render.py/rec.py with device_scale_factor=2.
