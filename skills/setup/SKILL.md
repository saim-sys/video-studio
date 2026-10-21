---
name: setup
description: First-time Video Studio setup on this computer, or a health check. Activates the license, checks Python packages, ffmpeg, GPU encoder, memory and disk, installs what's missing, and creates or checks the channel folder and brand kit.
---

# Video Studio setup

`PY="${user_config.python}"`, channel at `${user_config.channel_dir}`.

1. License. Run `"$PY" "${CLAUDE_PLUGIN_ROOT}/client/boot.py" ensure --data "${CLAUDE_PLUGIN_DATA}"`.
   - If the reason is `not_activated`: ask the user to open a terminal and run this themselves, pasting the license
     key from their Whop orders in place of `YOUR-KEY` (don't ask them to paste the key into this chat):
     `"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/client/boot.py" activate YOUR-KEY --data "${CLAUDE_PLUGIN_DATA}"`
     Then run `ensure` again.
   - Any other failure: show its `message` and stop.
   - On success, call the printed `pipeline` folder PIPE and `bundle` folder BUNDLE.
2. Run `"$PY" "<PIPE>/studio.py" doctor "${user_config.channel_dir}"` and read the JSON.
3. Missing Python packages: `"$PY" -m pip install -r "<BUNDLE>/requirements.txt"`.
   If ffmpeg is missing, tell the user how to install it (Windows: `winget install Gyan.FFmpeg`; macOS:
   `brew install ffmpeg`) and wait; don't install system software without asking.
4. If the channel folder doesn't exist yet: `"$PY" "<PIPE>/studio.py" init-channel "${user_config.channel_dir}"`.
   It comes with the studio's fonts and sound effects.
5. Brand kit, with the user:
   - Mascot: five PNGs with transparent backgrounds in `brand/mascot/`: point, thumbsdown, shocked, laugh, angry.
     Images on a flat green background can be keyed with `"$PY" "<PIPE>/chroma_key.py" in.png out.png`.
     If they need a new character, help them write one prompt for their image tool (same character, five poses,
     chest-up, thick outlines, flat green background) and key the results. Never copy another channel's mascot.
   - Music: looping background tracks as `brand/music/track_0.wav`, `track_1.wav`, ... (each chapter's `@SECTION`
     line picks one by number). Only music they have the rights to, such as the YouTube Audio Library or a paid
     licence (Epidemic Sound, Artlist). Never extract music from someone else's video.
   - Fill in the channel's `CLAUDE.md` (name, niche, voice) and `channel.json`.
6. Run doctor again and report in plain words: what's ready, what's still missing, and how fast renders will be
   on this machine (GPU or CPU, number of workers).
