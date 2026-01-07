---
layout: post
title:  Tower Defense
categories: [AI Coding]
pinned: true
---

I used to spend my time before classes playing the original Desktop Tower Defense. It had a long loading screen, it lagged when there are too many units, and it was written in Flash. I wanted to make a modern JavaScript version that's smoother and more optimized, but I wasn't a web developer... until LLMs came along.

It still took me about 30-40 hours to arrive at a playable, relatively bug-free state. Along the way, I picked up a lot of best practices for coding with Claude, which will be documented [here]({% post_url 2025-08-13-tower-defense-learnings %}). BUT the end result is a highly configurable, extendable, fast, browser-based tower defense game.

<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">

<style>
.iframe-container {
  position: relative;
  width: 100%;
  padding-bottom: 75%; /* 4:3 aspect ratio (adjust as needed) */
  height: 0;
  overflow: hidden;
}
.iframe-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
  touch-action: manipulation;
}
</style>

<div class="iframe-container">
  <iframe
    src="https://towerdefense-296e.onrender.com/"
    allow="fullscreen">
  </iframe>
</div>

I hope you enjoy the game, and please drop feature requests in the comments.