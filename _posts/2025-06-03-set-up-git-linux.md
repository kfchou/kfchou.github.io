---
layout: post
title:  GH CLI tool - the best git credential manager for Linux
categories: [git, tutorials]
excerpt: Set up git credentials on a Linux machine in ~2 minutes
---

Are you setting up a new Linux machine and need to set up Git? This is by far the fastest and easiest way to set up your Git credentials, assuming you're using GitHub and not another version control service.

# TL;DR
Do the following: 

1. Get [GitHub CLI tools](https://cli.github.com/manual/). Follow instructions here: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
2. Authenticate: run `gh auth login` and follow the prompts to log into GitHub
3. Use `gh` as the Git credential helper: run `gh auth setup-git`
4. Set up the username and email associated with your commits:
    ```
    git config --global user.name "first.last"
    git config --global user.email "<first.last@email.com>"
    ```
Done! Try cloning a repository to make sure everything worked with `git clone ...`

# Motivation
The first time you log into GitHub on Windows PowerShell, a browser pops up and you're instructed to log into GitHub via the web UI. The Windows Git Credential Manager then saves your credentials behind the scenes, and you never have to worry about entering your password again.

Similarly, WSL utilizes Windows' Git Credential Manager to handle storing your credentials.

On Linux, it is not so easy. Both Git and the official GitHub docs point to the [Git Credential Manager](https://github.com/git-ecosystem/git-credential-manager), and after installing it, you need to take additional non-trivial steps to finish setting it up. All credential store options available to Linux distributions (in `git config --global credential.credentialStore <store_option>`) involve additional third-party tools. Why isn't there a simple UI pop-up like Windows? This is where the GitHub CLI tool comes to the rescue.

In addition to managing your credentials, the GitHub CLI tool lets you interact with GitHub itself in the command line, such as opening PRs, issues, interacting with projects, and so much more!