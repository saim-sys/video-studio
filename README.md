# Video Studio

Faceless sports-history YouTube videos with Claude Code: research, script, footage, edit plan, GPU render and a
frame-by-frame audit. You pick the topic, record the voiceover and approve the hook. Claude does the rest.

Requires an active Video Studio membership: your license key is in your Whop orders.

## Install (once per computer)
1. Install [Claude Code](https://code.claude.com), Python 3.10 or newer, and ffmpeg.
2. In Claude Code:
   ```
   /plugin marketplace add saim-sys/video-studio
   /plugin install studio@video-studio
   ```
   When asked, enter how to run Python (`python`, `python3` or a full path) and choose a folder for your channel.
3. Run `/studio:setup`. It activates your license (you'll paste your key into a terminal command it gives you),
   installs what's missing, and builds your brand kit: your mascot's five poses and your music.

## Every video
Start a new Claude Code session in your channel folder, then:
```
/studio:new-video "Your video title"
```
Claude researches and writes the script, then waits. Record the voiceover, save it as `vo/user.wav` in the video's
folder, and say "voiceover is in". You'll approve a 50-second hook preview, then get the finished `final.mp4`.

| Command | What it does |
|---|---|
| `/studio:setup` | License, tools and brand kit. Run it again any time something seems off |
| `/studio:new-video "title"` | Starts a video and takes it all the way to the final file |
| `/studio:status` | Shows where a video is and continues it (after a break or a usage limit) |

## Your responsibilities
- Use only footage, photos and music you're allowed to publish. The studio crops logos and skips bad frames, but
  it doesn't make footage licensed.
- Your mascot and music must be your own (or properly licensed). Never copy another channel's.

## Membership
The studio checks your license once a day and works offline for up to 3 days. If your membership ends, it stops
working and removes the downloaded studio from your computer. Changing computers? Reset your key from your Whop
orders, then run `/studio:setup` on the new one.
