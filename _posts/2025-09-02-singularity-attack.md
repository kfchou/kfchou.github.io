---
layout: post
title:  s1ngularity - AI-assisted supply-chain attack
categories: [LLMs, Security, Nx]
---

I don't usually write about security, but as a frequent user of Claude Code, I felt the recent news of the s1ngularity attack warrants special attention. Just as we all started to rely on AI CLI tools like Claude and Gemini to enhance our work, hackers just exploited them in a real supply-chain attack. It's the first time we've seen this in the wild.

## What happened?

On August 26–27, 2025, attackers briefly took over popular Nx npm packages and shipped a post-install stealer that harvested developer secrets (GitHub and npm tokens, SSH keys, `.env` API keys, and even crypto wallets). Stolen data was pushed to *public repos created in the victim's own GitHub account* named `s1ngularity-repository` (containing `results.b64`). Nx has since removed the bad versions, but a second wave of attack used leaked tokens to flip victims' private repos to public [[1][1]][[2][2]].


## How LLMs were part of the attack

The malware didn't just comb files—it **abused locally installed AI CLI tools** (e.g., Claude, Gemini, Amazon Q “q”) to help with reconnaissance and exfiltration, invoking them with unsafe flags like `--dangerously-skip-permissions`, `--yolo`, and `--trust-all-tools`. This is one of the first documented cases of **weaponizing developer AI assistants** to widen a supply-chain breach. Some tools refused harmful prompts, but many executed, aiding enumeration of secrets [[2][2]][[3][3]][[4][4]][[5][5]].


## What actually let this happen

Investigators and Nx's own advisory tie the compromise to a **vulnerable GitHub Actions workflow**: a PR-title injection combined with `pull_request_target` (elevated permissions) allowed triggering the publish pipeline and **exfiltrating an npm publishing token**. Attackers then pushed malicious Nx builds for a few hours until takedown [[1][1]][[2][2]].


## Are you affected? Quick checks

- **Search your GitHub** for `s1ngularity-repository` (GitHub hid many, but artifacts may remain). Also check your audit log for repo creations [[1][1]].  
- Look for `/tmp/inventory.txt` (and `.bak`) and for `sudo shutdown -h 0` lines added to `~/.bashrc` or `~/.zshrc` [[1][1]][[2][2]].  
- See if you installed **affected Nx versions**: `nx` `20.9.0–20.12.0` and `21.5.0–21.8.0`, plus listed `@nx/*` versions [[1][1]][[2][2]].  
- Note: Many compromises occurred via the **Nx VS Code extension** (version check ran `npx nx@latest` during the window). Update Nx Console to `18.66.0+` [[3][3]].  


## If exposed: immediate mitigation (priority order)

1. **Rotate credentials**  
   Revoke/regenerate: GitHub PATs and gh CLI OAuth token, npm tokens, SSH keys, cloud/API keys in `.env`, and **AI provider keys** (Anthropic, Google, OpenAI, Amazon Q, etc.). Treat any crypto wallets as compromised and move funds [[1][1]][[2][2]][[6][6]].  

2. **Purge malicious code paths**  
   Delete `node_modules`, clear package manager caches, remove `sudo shutdown` lines from shells, delete `/tmp/inventory.txt*`, reinstall only safe Nx versions [[1][1]][[2][2]].  

3. **Hunt for exposure evidence**  
   Review org/user audit logs for odd `gh` API use; search for `s1ngularity-repository*`. Consider scanning leaked `results.b64` to enumerate which secrets need rotation (GitGuardian published indicators and a scanner) [[2][2]][[5][5]].  


## Hardening for the AI era (what to change going forward)

- **Treat AI CLIs/agents like privileged automation**: run in sandboxes/containers with minimal filesystem scope and no default network egress; disable or forbid “yolo/skip-permissions/trust-all-tools” modes; avoid granting them blanket access to SSH keys, cloud creds, or wallet paths [[4][4]].  
- **Lock down CI workflows**: avoid `pull_request_target` unless absolutely necessary; sanitize any user-controlled inputs (titles, labels); restrict `GITHUB_TOKEN` scopes; require approvals before publish steps [[1][1]].  
- **Dependency hygiene**: pin versions; **cool-down** new releases for 24–48h before adoption; block post-install scripts org-wide unless required; consider SBOM/allow-lists and registries that quarantine fresh versions [[3][3]].  
- **Secrets posture**: centralize secret inventory and automate rotation; monitor for public repo creation or anomalous `gh` activity; deploy honeytokens to detect leakage quickly [[5][5]].  


## Sources & further reading
1. [Malicious versions of Nx and some supporting plugins were published][1]  
2. [Wiz Research – Nx supply-chain attack technical write-up][2]  
3. [Kaspersky – Nx supply chain attack overview][3]  
4. [The Hacker News – Hackers abused AI tools in Nx npm supply-chain attack][4]  
5. [GitGuardian – Analysis of leaked secrets & LLM tool prevalence][5]
6. [Kaspersky – Nx supply chain attack overview][6]

[1]: https://github.com/nrwl/nx/security/advisories/GHSA-cxm3-wv7p-598c "Malicious versions of Nx and some supporting plugins were published"
[2]: https://www.wiz.io/blog/s1ngularity-supply-chain-attack "Wiz Research – Nx supply-chain attack technical write-up"
[3]: https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware "Supply Chain Security Alert: Popular Nx Build System Package Compromised with Data-Stealing Malware"
[4]: https://thehackernews.com/2025/08/malicious-nx-packages-in-s1ngularity.html "The Hacker News – Hackers abused AI tools in Nx npm supply-chain attack"
[5]: https://blog.gitguardian.com/the-nx-s1ngularity-attack-inside-the-credential-leak/ "GitGuardian – Analysis of leaked secrets & LLM tool prevalence"
[6]: https://www.kaspersky.com/blog/nx-build-s1ngularity-supply-chain-attack/54223/ "Kaspersky – Nx supply chain attack overview"
