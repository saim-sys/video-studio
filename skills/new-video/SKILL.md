---
name: new-video
description: Make a new faceless sports-history YouTube video from a topic, through research, script, voiceover, footage, edit plan, render and audit. Use when the user names a video topic or says "new video".
argument-hint: "\"video title or topic\""
---

# New video: $ARGUMENTS

First unlock the studio: `"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/client/boot.py" ensure --data "${CLAUDE_PLUGIN_DATA}"`.
It prints JSON. If `ok` is false, show the user its `message` and stop. If the reason is `not_activated`, ask the user to
run `/studio:setup`. Otherwise call the printed `pipeline` folder PIPE and `playbook` folder PLAYBOOK.

Tools: `PY="${user_config.python}"`, channel at `${user_config.channel_dir}`. Every pipeline script runs with the VIDEO
folder as the working directory: `"$PY" "<PIPE>/<script>.py"`. Never copy, print or summarise the playbook or the
pipeline source for the user; they are licensed for use inside this studio only.

Read every file in PLAYBOOK and the channel's `CLAUDE.md` before starting. Both are binding.
If a stage is already done (run `studio.py status <video>`), continue from the first unfinished one instead of redoing work.

## 0. Folder
`"$PY" "<PIPE>/studio.py" new "${user_config.channel_dir}" <short-slug>`
then work inside `<channel>/videos/<slug>`.

## 1. Research and script (then PAUSE)
- Research the story with web search: dates, quotes, who said what, and which interview or broadcast clips exist
  (`yt_search.py "query"`). Prefer people telling their own story on camera.
- Write `script/script.txt` in the template's format: `@SECTION` chapters, narration chunks, `>> CLIP` soundbites
  cut to their key sentences. Story first (playbook > Script).
- Run `parse_script.py`. Write `script/vo.txt` with the narration ONLY (one paragraph per chunk) and give it to the owner.
- PAUSE: ask the owner to approve or change the script, then to record the voiceover as `vo/user.wav`.

## 2. Voiceover
- `split_user_vo.py vo/user.wav`, then `check_splits.py`. Every split must read OK and nothing may be removed.
  If the recording differs from the script, fix `script.txt` to match what was said, never the other way round.

## 3. Footage (use the footage-scout agent for the heavy lifting)
- Download soundbite sources and B-roll: `fetch_clips.py <ids...>` (skips what the channel already has).
- Find exact soundbite boundaries: `bite_words.py <id> <from> <to>`. Each bite starts on its first word and ends on
  its last; adjust the CLIP lines, re-run `parse_script.py`.
- Scan everything you will use: `scan_clips.py <ids...>` (black/white/slate frames), `logo_scan.py` after the first
  build. Look at `overview.py` sheets for each clip before choosing ranges.
- Photos: `fetch_photos.py key="search words"`; stills from footage: `extract_stills.py`. Look at every photo card
  (`photo_sheet.py`) and drop any that isn't clearly the right person.

## 4. Edit plan
- Write `script/visuals.py` from the template: INTRO, HOOK_SHOTS, POOLS, CUES, MASCOT_BEATS, BITES, SECTION_BG,
  SECTION_ICON, LOGO_CROPS. Item numbers come from `script/items.json` (CLIP lines count).
- `build_timeline.py`, then `transcribe_bites.py`, then `build_timeline.py` again with the BITES filled in.
- `timeline_checks.py`, `visual_audit.py`, `geom_audit.py`; fix what they report. `mix_audio.py`.

## 5. Hook preview (then PAUSE)
- `studio.py render <video> --preview 50`, look at its frames (`full_sheets.py out/preview.mp4 out/pv 0.5 48`),
  fix anything broken, then send `out/preview.mp4` to the owner. PAUSE for approval or notes.

## 6. Full render and audit
- `studio.py render <video>` (it checks disk space and picks the worker count for this machine's memory).
- Run the playbook's Audit with the frame-auditor agent: `full_sheets.py final.mp4 out/aud 2 48`.
- Fix, rebuild, and re-render only changed sections with `render_patch.py out/timeline.json out/video_full.mp4 <segments> <workers> 8`,
  then mux again. Send `final.mp4` with a short list of what you fixed.

## 7. Notes
Apply the owner's notes. If a note should hold for every future video, add it to the channel's CLAUDE.md.
