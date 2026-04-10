---
layout: post
title: "Good Dependency Hygiene Practices: Protecting Yourself from Supply Chain Attacks"
categories: [Security, Python, JavaScript]
excerpt: "The number of high-profile supply chain attacks on PyPI and npm has been increasing in frequency. Keeping good 'dependency hygiene' can help you stay protected. This post explores a list of simple actions you can take to achieve good hygiene, and an explainer on what they protect against."
---

TL;DR: A list of steps you can take to protect yourself from supply chain attacks.

- [Consuming Packages](#consuming-packages)
  - [Pin dependencies with hashes](#pin-dependencies-with-hashes)
  - [Use `exclude-newer` to avoid zero-day windows](#use-exclude-newer-to-avoid-zero-day-windows)
  - [Exclusion Window Conflict with CVEs: Override When Necessary](#exclusion-window-conflict-with-cves-override-when-necessary)
  - [Prevent build-time code execution](#prevent-build-time-code-execution)
  - [Run `uv audit` or `pip-audit` in CI](#run-uv-audit-or-pip-audit-in-ci)
  - [Scan GitHub Actions workflows with zizmor](#scan-github-actions-workflows-with-zizmor)
  - [Pin GitHub Actions to commit SHAs](#pin-github-actions-to-commit-shas)
  - [Understand dependency confusion if you use private packages](#understand-dependency-confusion-if-you-use-private-packages)
  - [Do due diligence before adding a dependency](#do-due-diligence-before-adding-a-dependency)
  - [On upgrade cadence](#on-upgrade-cadence)
- [Publishing to PyPI](#publishing-to-pypi)
  - [Switch to Trusted Publishing](#switch-to-trusted-publishing)
  - [Require 2FA for all maintainers](#require-2fa-for-all-maintainers)
- [Conclusion](#conclusion)
- [References](#references)
- [Further Reading](#further-reading)

In early 2026, the popular Axios package was compromised on npm in a supply chain attack [[1]]. This made waves in the JS community, because the popular package has over 100 million weekly downloads. The Axios attack installed a hidden dependency that downloaded a remote access trojan (RAT), giving attackers access to credentials in `.env` files.

Attacks on other popular packages, like Trivy (vulnerability scanner), KICS (IaC scanner), Telnyx (telephony SDK), and liteLLM (LLM proxy server, ~95 million monthly downloads), also made the news. These packages were compromised as part of the TeamPCP campaign: poisoned versions ran a credential harvester on every Python invocation, scanned for Kubernetes secrets, and opened a persistent remote code execution backdoor [[2]].

With these serious attacks happening more and more often, how should we developers protect ourselves? The following are some best practices for "dependency hygiene" to help prevent you from falling victim to these attacks.

## Consuming Packages

### Pin dependencies with hashes

When a maintainer's credentials are compromised, an attacker can push a new artifact under an existing version number without touching the source repo — the compromise is invisible to anyone checking only the version string. Hashes verify the specific artifact. Making sure hashes are in requirement files:

```bash
# pip-tools
pip-compile --generate-hashes requirements.in

# uv
uv pip compile --generate-hashes requirements.in -o requirements.txt
# or generate a full lockfile
uv lock
```

Install with hash verification enforced:

```bash
pip install -r requirements.txt --require-hashes
# or
uv sync
```

**Note**: Lockfiles automatically take care of this best practice.

### Use `exclude-newer` to avoid zero-day windows

Most supply chain attacks are detected within hours of publication. Other attacks take much longer — the [XZ Utils backdoor](https://en.wikipedia.org/wiki/XZ_Utils_backdoor) was active for months before discovery. A rolling time buffer excludes packages published too recently to have been scrutinized. Set it in `pyproject.toml` for a permanent default [[3]]:

```toml
[tool.uv]
exclude-newer = "2 weeks" # or more
```

Or pass it per-command:

```bash
uv pip install -r requirements.txt --exclude-newer 2026-03-28
```

This won't catch attacks on packages already in your lockfile, but it prevents pulling in newly-published malicious versions during fresh installs or CI runs.

### Exclusion Window Conflict with CVEs: Override When Necessary
When a security advisory is released, the fix is almost always the newest version. In this case, upgrading the affected dependency in a timely manner conflicts with the `exclude-newer` policy.

To manage this conflict, you can selectively bypass it for specific packages in uv. Using `cryptography` as an example:
```
uv lock --upgrade-package=cryptography --exclude-newer-package=cryptography="0 days"
```

### Prevent build-time code execution

Typosquatted and name-confused packages commonly deliver their payload via install hooks or `setup.py` — code that runs the moment you `pip install`. When no wheel is available, `pip` will execute these build hooks. Requiring pre-built wheels eliminates that execution path:

```bash
# uv
uv pip install -r requirements.txt --no-build

# pip
pip install -r requirements.txt --only-binary=:all:
```

If a dependency lacks a wheel, installation fails visibly rather than executing arbitrary Python.

### Run `uv audit` or `pip-audit` in CI

These check your dependency tree against the OSV vulnerability database:

```bash
# uv
uv audit

# pip-audit
pip-audit -r requirements.txt
```

Neither catches zero-days, but they surface known CVEs that accumulate in transitive dependencies over time. Both are fast enough to add to a standard CI pipeline without meaningful overhead.

### Scan GitHub Actions workflows with zizmor

CI/CD pipelines are a target in their own right. The December 2024 Ultralytics attack used a crafted PR branch name to trigger template injection in a GitHub Actions workflow, exfiltrating the PyPI token without ever compromising the maintainer's credentials [[4]]. Any workflow using `pull_request_target` with user-controlled inputs is in scope for this class of attack. [zizmor](https://github.com/woodruffw/zizmor) is a static analysis tool that catches these patterns — `pull_request_target` misuse, shell injection, and unpinned external actions [[5]]:

```bash
pip install zizmor
zizmor .github/workflows/
```

### Pin GitHub Actions to commit SHAs

The same CI/CD poisoning vector applies to the Actions you depend on. A compromised action maintainer can move a mutable tag like `@v3` or `@main` to point at malicious code — which is exactly what happened in the March 2025 tj-actions/changed-files attack, retroactively affecting 23,000 repositories [[6]].

LiteLLM's CI pipeline used Trivy without pinning it to a commit SHA. When Trivy was compromised, the attacker gained code execution inside LiteLLM's build environment and exfiltrated its PyPI publishing credentials. From there they uploaded backdoored versions directly [[7]][[8]]. Pinning Trivy to a commit SHA would have stopped the cascade at the first step.

So, pin to the full commit SHA instead of using mutable tags:

```yaml
# Mutable — avoid
- uses: actions/checkout@v4

# Immutable
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

[Dependabot](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically) and [Renovate](https://docs.renovatebot.com/) can keep these SHAs current automatically. For Dependabot, a 14-day cooldown avoids pulling in packages in the window when attacks are most likely to be undetected:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: pip
    directory: "/"
    schedule:
      interval: weekly
    cooldown:
      default-days: 14
```

Enable security alerts separately in your repository's Dependabot settings — these bypass the cooldown and notify you immediately when a CVE is filed against a dependency you're using.

### Understand dependency confusion if you use private packages

If your project depends on packages hosted on a private registry, an attacker can publish a higher-versioned package with the same name to PyPI or npm. Many package managers will resolve to the public registry by default. Either configure your package manager to prefer the private registry, or use namespace prefixes for internal packages.

### Do due diligence before adding a dependency

Typosquatting attacks register packages with names close to popular ones (`colourama` vs. `colorama`). A newer variant, "slopsquatting," targets names LLMs tend to hallucinate when generating code — packages that don't exist but that an AI coding assistant might suggest [[9]]. The cheapest defense is not taking on the dependency in the first place: if the functionality is small and self-contained, consider implementing it directly. If you do need an external package, spend a few minutes on [OpenSSF Scorecard](https://scorecard.dev/) and the package's PyPI release history before adding it. A project with irregular release cadence, a recent maintainer change, or a sudden burst of new versions after months of inactivity is worth a closer look — the last two signals also apply to account takeover and long-term infiltration attacks, where an attacker gains control of a legitimate project. [Socket.dev](https://socket.dev) flags behavioral signals in packages — new network calls, obfuscated code, install hooks that weren't there before — that CVE databases miss entirely.

### On upgrade cadence

Outside of CVEs, you generally don't need to upgrade dependencies on any particular schedule. Staying reasonably current does have one practical benefit: when a security patch does land, applying it is straightforward rather than a multi-version migration. But chasing the latest release of every dependency is itself an attack surface — you're opting into whatever was published most recently. **Let security alerts, not release frequency, drive urgency.**

**Key takeaway**: The minimum viable baseline — hash pinning, `uv audit` in CI, GitHub Actions pinned to commit SHAs — addresses three distinct vectors that have been exploited in production incidents this year.

## Publishing to PyPI

### Switch to Trusted Publishing

Compromised maintainer credentials are the most common path to a poisoned package release. Attackers phish accounts or harvest long-lived API tokens from CI logs and leaked `.env` files; once they have a token, they can publish without touching the source repo. Replace long-lived PyPI API tokens with OIDC-based Trusted Publishing [[10]]. This generates short-lived credentials scoped to a specific GitHub Actions workflow, automatically, per publish. A stolen long-lived token is permanent access; a stolen OIDC token is scoped to a single run. The LiteLLM attack relied on a long-lived token — Trusted Publishing would have eliminated that step.

Configure in PyPI project settings under "Trusted Publishers", then update your publish workflow:

```yaml
jobs:
  publish:
    permissions:
      id-token: write  # Required for OIDC
    steps:
      - uses: pypa/gh-action-pypi-publish@release/v1
        # No API token needed
```

After switching, revoke all legacy API tokens. Audit CI logs for any prior exposure.

### Require 2FA for all maintainers

PyPI allows requiring 2FA at the project level. Enable it. A phished maintainer without 2FA gives an attacker a direct publishing path.

## Conclusion

The recent high-profile hacks all involved supply chain attacks — hackers compromise a dependency somewhere upstream, and the victim unwittingly installs the poisoned version into their environment. Most developers know, with the help of Dependabot, to update dependencies as CVEs become known. What is lesser known is that CI is also an attack surface. Now you know why CI needs to be secured, and how to do it, along with other security best practices. Stay safe out there!

## References

[1]: https://www.sans.org/blog/axios-npm-supply-chain-compromise-malicious-packages-remote-access-trojan "SANS Institute: Axios NPM Supply Chain Compromise"
[2]: https://www.reversinglabs.com/blog/teampcp-supply-chain-attack-spreads "ReversingLabs: Inside the TeamPCP cascading supply chain attack"
[3]: https://docs.astral.sh/uv/reference/settings/#exclude-newer "uv documentation: exclude-newer"
[4]: https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/ "PyPI Blog: Supply-chain attack analysis — Ultralytics"
[5]: https://github.com/woodruffw/zizmor "zizmor: GitHub Actions static analysis"
[6]: https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066 "Wiz: tj-actions/changed-files supply chain attack — CVE-2025-30066"
[7]: https://www.endorlabs.com/learn/teampcp-isnt-done "Endor Labs: TeamPCP Isn't Done — Threat Actor Behind Trivy and KICS Compromises Now Hits LiteLLM"
[8]: https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/ "Datadog Security Labs: LiteLLM and Telnyx compromised on PyPI"
[9]: https://checkmarx.com/zero-post/python-pypi-supply-chain-attack-colorama/ "Checkmarx: PyPI Supply Chain Attack — Colorama and Colorizr Name Confusion"
[10]: https://docs.pypi.org/trusted-publishers/ "PyPI Docs: Trusted Publishing"

1. [SANS Institute: Axios NPM Supply Chain Compromise](https://www.sans.org/blog/axios-npm-supply-chain-compromise-malicious-packages-remote-access-trojan)
2. [ReversingLabs: Inside the TeamPCP cascading supply chain attack](https://www.reversinglabs.com/blog/teampcp-supply-chain-attack-spreads)
3. [uv documentation: exclude-newer](https://docs.astral.sh/uv/reference/settings/#exclude-newer)
4. [PyPI Blog: Supply-chain attack analysis — Ultralytics](https://blog.pypi.org/posts/2024-12-11-ultralytics-attack-analysis/)
5. [zizmor: GitHub Actions static analysis](https://github.com/woodruffw/zizmor)
6. [Wiz: tj-actions/changed-files supply chain attack — CVE-2025-30066](https://www.wiz.io/blog/github-action-tj-actions-changed-files-supply-chain-attack-cve-2025-30066)
7. [Endor Labs: TeamPCP Isn't Done — Threat Actor Behind Trivy and KICS Compromises Now Hits LiteLLM](https://www.endorlabs.com/learn/teampcp-isnt-done)
8. [Datadog Security Labs: LiteLLM and Telnyx compromised on PyPI](https://securitylabs.datadoghq.com/articles/litellm-compromised-pypi-teampcp-supply-chain-campaign/)
9. [Checkmarx: PyPI Supply Chain Attack — Colorama and Colorizr Name Confusion](https://checkmarx.com/zero-post/python-pypi-supply-chain-attack-colorama/)
10. [PyPI Docs: Trusted Publishing](https://docs.pypi.org/trusted-publishers/)

## Further Reading

- [Bernát Gábor: Defense in Depth — A Practical Guide to Python Supply Chain Security](https://bernat.tech/posts/securing-python-supply-chain/) — thorough practical guide by the tox/virtualenv maintainer
- [OpenSSF: Maintainers' Guide — Securing CI/CD Pipelines After tj-actions and reviewdog](https://openssf.org/blog/2025/06/11/maintainers-guide-securing-ci-cd-pipelines-after-the-tj-actions-and-reviewdog-supply-chain-attacks/)
- [Trail of Bits: Supply chain attacks are exploiting our assumptions](https://blog.trailofbits.com/2025/09/24/supply-chain-attacks-are-exploiting-our-assumptions/)
- [Wiz: LiteLLM TeamPCP Supply Chain Attack](https://www.wiz.io/blog/threes-a-crowd-teampcp-trojanizes-litellm-in-continuation-of-campaign)
