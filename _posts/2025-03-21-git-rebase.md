---
layout: post
title:  Maintain a tidy commit history with git rebase
categories: [git, tutorial]
excerpt: A closer look into `git rebase`
---
- [The basic rebase](#the-basic-rebase)
- [Rebasing with 2 arguments](#rebasing-with-2-arguments)
  - [Use case: Dealing with squashed parent branches](#use-case-dealing-with-squashed-parent-branches)
  - [Use case: Squashed parent brahcnes with additional commits](#use-case-squashed-parent-brahcnes-with-additional-commits)
  - [Use case: Removing a commit from history](#use-case-removing-a-commit-from-history)
- [Rebasing with 3 arguments](#rebasing-with-3-arguments)
- [Further reading](#further-reading)

What does a clean commit history look like? Let's take a look at a the commit history of the main branch of a repository like [Poetry](https://github.com/python-poetry/poetry/commits/main/). Two things stand out to me -- 1. Each commit is bite-sized (atomic commits); changes are limited to a few files and functionalities, and 2. each commit message succinctly describes the change made, so if anything goes wrong, devs know exactly where to look. This is not only helpful for debugging, but it also helps with automated generation of [release notes](https://github.com/python-poetry/poetry/releases/tag/2.1.1).

A key tool in keeping a clean commit history is `git rebase`. But most people I've talked to aren't familiar withit. So I hope these notes will help you learn to use `git rebase` like a pro. 



# The basic rebase
You're working on the `feature` branch, and need to merge it back into `main`. Rebase is used to keep the git history linear and synchronize your branch with the additional commits made in `F` and `G`.

The syntax for rebase is `git rebase <target branch>`

```bash
git pull origin main # update your target branch
git checkout feature # switch to your branch
git rebase main # initiate the rebase
```

This would have the following effect:
```
          Before                           After
    A---B---C---F---G (main)        A---B---C---F---G (main)
             \                                       \
              D---E (feature)                         D'---E' (feature)
```
In git jargon, we call this "__rebase onto main__".

> ⚠️ After rebasing, you must force push your changes:
```bash
git push --force
```

Why do you need to force push after a rebase? Because the commits in the feature branch has changed (`D -> D'`,`E -> E'`). You can read the [long answer here](https://stackoverflow.com/questions/77029078/why-do-i-need-a-force-push-after-a-rebase).

I recommand reading [Git rebase illustrated](https://dev.to/joemsak/git-rebase-explained-and-eventually-illustrated-5hlb) to see what's happening under the hood. Specifically, having an understanding of what happens when git "rewinds" then "replays" your commits is very helpful in branch management.

# Rebasing with 2 arguments
`git rebase --onto` allows you to rebase starting from a specific commit. It grants you exact control over what is being rebased and where. This is for scenarios where you need to be precise [1].


Let's say you need to rebase `feature` directly on top of `F` starting from `E`, dropping `D`
```
          Before                                   After
    A---B---C---F---G (main)                A---B---C---F---G (main)
             \                                           \
              D---E---H---I (HEAD, feature)               E'---H'---I' (HEAD, feature)
```
In this case, we would use the command `git rebase --onto F D`. i.e., "rebase onto `F`, starting from the child of `D`".

You can think of it like we are changing the parent of `E` from `D` to `F`. The general syntax here is
```bash
git rebase --onto <new_base> <old_base>
```

## Use case: Dealing with squashed parent branches
This syntax is very useful when you have branched off of `feature-1`, but `feature-1` has been squash-merged into `main`:

```
   feature-1 has been squash-merged to main            This is equivalent to the previous picture
     A---BC   <-- main                                     A---BC   <-- main
      \                                                     \
        B---C   <-- feature-1                                B---C---D---E <-- feature-2
            \                                     
             D---E   <-- feature-2                                     
```

Now you might want to merge `feature-2` to `main` as well, but because `B` and `C` are technically different from `BC`, you _might_ run into issues.

To maintain a clean commit history, you can drop `B` and `C`, and rebase onto `BC`:
```bash
# main points to BC and feature-1 points to C
git switch feature-2 && git rebase --onto main feature-1
```
Which would look like
```
          D'---E'  <-- feature-2 (HEAD)
         /
    A---BC   <-- main
     \
      B---C   <-- feature-1
          \
           D---E   [abandoned]
```

## Use case: Squashed parent brahcnes with additional commits
Let's complicate the situation a bit. Someone has made additional commits to `feature-1` after you've branched off it, then squash-merged `feature-1` into `main`. To keep your own commit history clean in this case, do the same as above:
```bash
git switch feature-2 && git rebase --onto main feature-1
```
Which looks like
```
            Before                                            After

                                                        D'-E'  <-- feature-2 (HEAD)
                                                       /
      A---BCFG   <-- main                       A--BCFG   <-- master
       \                                         \
        B---C---F---G   <-- feature-1             B--C--F--G   <-- feature-1
            \                                        \
             D--E   <-- feature-2 (HEAD)              D--E   [abandoned]
```

See detailed discussion [here](https://stackoverflow.com/questions/63218716/branching-off-of-squashed-branches).

## Use case: Removing a commit from history
Have you ever committed a secret by accident? It's ok, we all have. I'll show you how to remove that commit from your git history.

Let's say you've made the commit `A`, `B`, `C`, ... `G`. If you need to remove `C` from your history, do the following:
```
# Assuming you're on the correct branch
git rebase --onto <commit-B> <commit-C>
```
You'll get
```
            Before                                   After
                                                       
      A---B---C---D---E                         A---B---D---E 
```

Unlike `git revert`, `rebase` will remove the "oopsie" commit without leaving a trace (remember to --force push). Use with caution...

# Rebasing with 3 arguments
We can be even more precise while rebasing. In the examples above, you can specify which branch you're referring to with
```bash
git rebase --onto <new_base> <old_base> HEAD
```
Doing so would have the same effects illustrated above, where `HEAD` points to `feature-2`.

The general syntax for 3-argument rebase is
```bash
git rebase --onto <new_base> <old_base> <until>
```

What happens if we change `HEAD` to another commit? In the basic example, `git rebase --onto F D H` would have the following effect:
```
        Before                                    After
    A---B---C---F---G (branch)                A---B---C---F---G (branch)
             \                                        |    \
              D---E---H---I (HEAD my-branch)          |     E'---H' (HEAD)
                                                       \
                                                        D---E---H---I (my-branch)
```
Here, we've not only rebased `my-branch`, we've also removed a commit. The same effect is achieved if we do `git rebase --onto F D HEAD~1`.

Neat! But you probably won't need to use this day to day.


# Further reading
These notes are distilled from numerous blogs and stack overflow answers. Select posts worth reading in detail include:

[1 - a tutorial on the rebase --onto command](https://stackoverflow.com/questions/29914052/how-to-git-rebase-a-branch-with-the-onto-command#:~:text=The%20Precise:%20git%20rebase%20%2D%2D,it%20contains%20some%20incompatible%20changes.&text=In%20this%20case%2C%20we%20would,.&text=In%20this%20example%2C%20in%20order,the%20old%20parent%20was%20E%20.)

[2 - more examples of the --onto command](https://womanonrails.com/git-rebase-onto#:~:text=In%20case%20of%20git%20rebase,(all%20valid%20commits)%20too).

[Simon Dosda](https://simondosda.github.io/posts/2022-01-03-git-rebase-workflow.html) thinks one step ahead and organizes his commits locally even before pushing. Specifically, you can __amend__ local commits.