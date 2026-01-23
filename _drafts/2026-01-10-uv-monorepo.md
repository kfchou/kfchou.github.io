## Building Python Monorepos: uv Workspaces

Managing a complex Python repository with a shared core, various plugins, and multiple applications used to be a headache involving brittle path dependencies or complex scripts. In 2026, the uv workspace has emerged as the definitive solution for these "monorepo" architectures.

## What is a Workspace?
UV's Workspace concept is heavily inspired by Rust's Cargo -- a high performance tool for managing large codebases with multiple related packages.
* A workspace consists of many **workspace members**. Members are the individual local packages (applications or libraries) that make up the workspace. Each member has its own pyproject.toml to define its specific dependencies and configuration.
* The entire workspace shares a **single uv.lock file** located at the workspace root. This ensures that all members use consistent versions of shared dependencies, preventing version conflicts between different parts of your project.
* Workspace Root: Every workspace must have a root directory that contains a pyproject.toml file with a `[tool.uv.workspace]` table. This root is also considered a workspace member.
* Unified Environment: By default, uv creates a single virtual environment (.venv) for the entire workspace, which includes all members and their dependencies. Members are installed into this environment as editable packages, meaning changes to one member are immediately reflected when used by another.

Workspace members are treated as local editable packages. They can reference each other without being published. The workspace root serves as a wrapper, or a "dev" environment, for its members. It is an orchestration layer to define shared context across the workspace members.

An example directory tree for a uv-monorepo below:
```
uv-monorepo-python/
├── pyproject.toml          # Monorepo-level configuration (define unified tools settings common to all workspace members)
├── uv.lock                 # The sole uv lock file for dependency resolution
├── packages/               # All Python packages/libraries
│   ├── package_a/          # package_a is a workspace member
│   │   ├── pyproject.toml
│   │   └── package_a/
│   │       ├── __init__.py
│   │       └── ... 
│   ├── package_b/          # package_b is a workspace member
│   │   ├── pyproject.toml
│   │   └── package_b/
│   │       ├── __init__.py
│   │       └── ...
│   └── ...
├── services_or_apps/       # Applications/microservices
│   ├── service_x/
│   │   ├── pyproject.toml
│   │   └── service_x/
│   │       ├── __init__.py
│   │       └── ...
│   └── ...
│
├── scripts/                # Monorepo-level utility scripts
│   └── some_script.py
│
└──  tests/                  # Global or integration tests
    └── test_monorepo.py
```


## How to configure pyproject.toml?
Here is how to configure a repo with a shared core library and an application.

### 1. The Workspace Root (/pyproject.toml)

The root file defines the boundaries of your workspace and hosts shared dev tools.

```toml
[project]
name = "my-monorepo"
version = "0.1.0"
requires-python = ">=3.12"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "ruff>=0.3.0",
]

[tool.uv.workspace]
# Include all subdirectories in packages/ and apps/ as members
members = ["packages/*", "apps/*"]

[tool.uv.sources]
# You may add workspace dependencies here if needed
core-lib = { workspace = true } # core-lib is a workspace member

[tool.uv]
package = false # Don't build the root directory as a package
```

The key root-level config is the `[tool.uv.workspace]` table. Here, you define where your workspace members are located. Note that starting the path with `./` e.g., `./packages/*` is invalid.

Workspace members will appears in your `uv.lock`'s `[manifest]` table:
```
[manifest]
members = [
    "core-lib",
    ...
]
```

### 2. The Core Package (/packages/core-lib/pyproject.toml)

For a library, ensure it is marked as a "package" so others can import it. uv will build the package when you run the `sync` command.

```toml
[project]
name = "core-lib" # This package name gets registered as a workspace member
version = "0.1.0"
dependencies = ["requests>=2.31"]

[tool.uv]
package = true # This makes core-lib importable by other members
```

### 3. The Application (/apps/main-app/pyproject.toml)


The application links to other workspace members (e.g. the core library) by using the `[tool.uv.sources]` table and setting `workspace = true`. 

```toml
[project]
name = "main-app"
version = "0.1.0"
dependencies = [
    "core-lib",
    "external-lib",
    "fastapi>=0.110",
]

[tool.uv]
package = false # Optimizes sync; in this example, this app isn't meant to be imported

[tool.uv.sources]
core-lib = { workspace = true } # core-lib is a workspace member
external-lib { git = "https://github.com/code-owner/code-repo"} # declare private external dependencies explicitly

[tool.uv]
package = false # If the app is a standalone script/service, you can skip the package build.
```

You can find a template for a uv-monorepo [here](https://github.com/JasperHG90/uv-monorepo)

### Key Configurations
* `[tool.uv.workspace]`: Defines workspace members
* `tool.uv.package = true`: Essential for any member you want to import elsewhere.
* `tool.uv.sources`: Every member that depends on another must explicitly declare `{ workspace = true }` i.e., "this dependency is another workspace member".
* Root Constraints: If you need to force a specific version of a sub-dependency (like a security patch), it must be defined in the root pyproject.toml, as uv ignores member-level constraints.

## Essential Workflow (2026)
Once your structure is set, use these commands keep your monorepo healthy:

* `uv lock` from the root: generates manifest for your entire workspace.
* `uv sync` from the root: creates a virtual environment, install dependencies, build and install workspace packages.

  Note: You can run `uv sync --all-packages` from a workspace member directory to achieve the same affect as running `uv sync` from the workspace root.

* Isolated Testing: To run tests for just one plugin without other workspace noise:
  ```bash
  uv sync --package my-plugin
  uv run pytest packages/my-plugin/tests
  ```

  Note: make sure pytest is installed when you run `uv run pytest`. If pytest is not installed as a direct dependency of the package you are in, uv falls back to a system-wide pytest or one from a different environment that doesn't "know" about your local workspace members (details below)[uv appears to...]

* Add a new dependency from root: e.g., to add httpx to only the core library:
  ```bash
  uv add --package core-lib httpx
  ```


## Limitations
### Use Path Deps if Requirements Cannot Be Resolved 
use Workspaces if your packages are part of the same project lifecycle. Use Path Dependencies only if you have strictly conflicting version requirements (e.g., App A needs numpy 1.x and App B needs numpy 2.x) that cannot coexist in the same virtual environment.

Workspace Setup vs Relative Paths:

Feature 	Workspace	Relative Path Dependencies
Lockfile	Single uv.lock at root	Individual uv.lock per project
Virtual Env	Shared .venv at root	Separate .venv per project
Conflicts	Not allowed (fails to lock)	Allowed (isolated)
Best For	Tightly coupled apps/libs	Microservices or standalone libs
IDE Sync	Easiest (one project root)	Harder (multiple project roots)

## 3rd Party Development
A workspace setup is highly optimized for internal developers. What should we do if a 3rd party wants to contribute to a plugin? In this scenario, you'll want to share the core library, but keep other components or apps hidden.

In this case, you have a few options:
1. Publish your core library to a private packaging index
2. Use `uv build` inside your core library. Any dependency you listed in core/pyproject.toml (like pydantic) will be listed as a requirement for the 3rd party automatically.
3. Plugin Templates: It is common practice in 2026 to provide 3rd parties with a template repository (`uv` does this with `uv init --type lib`) that already has my-core-library added as a dependency.

## Testing and CI
* Define Shared Tools at the Root: Avoid installing pytest in every member's pyproject.toml. Instead, define a shared dev or test group in the root pyproject.toml.
```
# root/pyproject.toml
[dependency-groups]
test = ["pytest", "pytest-cov"]
```

### Local Testing
* Test Individual Packages (Isolated): To ensure a package isn't accidentally relying on "ghost dependencies" from its siblings, sync specifically to that package before testing.
```bash
# Syncs ONLY my_pkg's deps + the root's test tools
uv sync --package my_pkg --group test
# Run tests for that specific package
uv run --package my_pkg pytest packages/my_pkg/tests
```

* Testing across packages (Integration): For tests defined at the root that exercise multiple members, perform a full workspace sync. 
```bash
uv sync --all-packages --group test
uv run pytest tests/root_integration_tests
```

### Github Actions
* Use a Matrix for Individual Packages: Run tests for each member in parallel jobs to speed up CI and isolate failures.
```yaml
jobs:
  test-members:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        package: [core-lib, app-a, plugin-b]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --package ${{ matrix.package }} --group test
      - run: uv run --package ${{ matrix.package }} pytest packages/${{ matrix.package }}

```

* Dedicated Job for Integration Tests: Run root-level tests in a separate job that syncs the entire workspace.
```yaml
test-integration:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - uses: astral-sh/setup-uv@v5
    - run: uv sync --all-packages --group test
    - run: uv run pytest tests/root_integration_tests
```

## Appendix
### uv appears to use a different, unexpected virtual environment
Expected behavior:
```bash
$ uv run --package my_pkg which pytest
/monorepo-root/.venv/bin/python3: No module named pytest
```

Observed behavior:
```bash
$ uv run --package my_pkg which pytest
/opt/anaconda/bin/pytest # or some other unexpected path
```

Why does this happen?

When you run a command like pytest, your shell looks for the executable in the directories listed in your PATH environment variable. `uv run` puts the virtual environment's bin (or Scripts on Windows) directory earlier in the PATH. However, it does not fully replace the system PATH. This means if pytest is not installed in the current virtual environment, the command may fall back to a system or global Python environment where pytest is installed. In the case of `uv run pytest`, this can lead to unexpected behavior and environment inconsistencies. 

i.e., if pytest is not in your current environment, `uv run pytest` looks for pytest in the following order:
1. The Active Project Environment: The .venv associated with your current workspace member.
2. The Parent Workspace Environment: The shared .venv at the monorepo root.
3. The "Tool" Cache: If you've ever run uvx pytest (or uv tool run pytest), uv caches an isolated version of pytest in its global tool directory.
4. The System PATH: Any pytest executable found in your global system path
 
To prevent this behavior, you could run pytest specifically as a module:
```bash
$ uv run --package my_pkg python -m pytest
/monorepo-root/.venv/bin/python3: No module named pytest
```