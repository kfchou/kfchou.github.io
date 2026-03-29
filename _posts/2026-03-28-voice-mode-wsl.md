---
layout: post
title: "Enabling Claude Code's voice mode in WSL"
categories: [LLMs, Claude Code]
excerpt: "Claude Code now ships with a native `/voice` command, which performs speech-to-text (poorly) within the Claude Code CLI. Nevertheless, this feature is not available in WSL by default because Claude Code isn't able to detect audio input. This post is a fix."
---

Claude Code now ships with a native `/voice` command, which performs speech to text (poorly) within the Claude Code CLI. Nevertheless, this feature is not available in WSL by default because Claude Code isn't able to detect audio input.

To fix this, we bridge ALSA → PulseAudio:

1. Install the required utils:
```bash
sudo apt install libasound2-plugins pulseaudio-util alsa-utils
```

2. Create or edit `~/.soundrc`:
```bash
touch ~/.soundrc # create
nano ~/.soundrc # edit
```

3. Then paste:
```bash
pcm.default pulse
ctl.default pulse
pcm.!default pulse
ctl.!default pulse
```
Note: if you followed the `nano ~/.soundrc` command blindly, save and exit the editor with `ctrl+s` then `crtl+x`.

4. Verify it works:
```bash
arecord -L        # should list devices via PulseAudio
aplay -L          # same for playback
```

Then restart Claude Code and try `/voice` again. The ALSA plugin routes all ALSA calls through PulseAudio, so apps that check for ALSA devices will find them.