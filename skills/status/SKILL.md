---
name: status
description: Show where a video is in the pipeline and continue it from the first unfinished stage. Use after a break, a usage limit, or in a new session.
argument-hint: "[video folder or slug]"
---

# Video status

1. Unlock the studio: `"${user_config.python}" "${CLAUDE_PLUGIN_ROOT}/client/boot.py" ensure --data "${CLAUDE_PLUGIN_DATA}"`.
   If `ok` is false, show its `message` and stop (for `not_activated`, point the user to `/studio:setup`).
   Call the printed `pipeline` folder PIPE.
2. If no video was named, list `${user_config.channel_dir}/videos/` and pick the most recently changed one.
3. Run `"${user_config.python}" "<PIPE>/studio.py" status <video folder>`.
4. Tell the user in one or two lines what's done and what's next, then continue with the `new-video` skill's steps
   from that stage. Don't redo finished stages, and re-read `script/visuals.py` and the channel's CLAUDE.md first.
