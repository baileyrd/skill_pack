# Source-extraction playbook

Step 1 needs to be exhaustive regardless of what the source repo is written
in. The categories (`interface` / `config` / `behavior`, plus `test`/`docs`
as sources) are language-agnostic; the *tooling* to surface candidates
under each category is not. This is a starting-point checklist per common
source stack, not a substitute for reading the code — every language
section ends the same way on purpose: grep/tool output is a candidate list,
confirm by reading.

## Python
- **Interface**: `__all__` in `__init__.py` files; `click`/`argparse`/
  `typer` command/option definitions (grep for `add_argument`,
  `@click.command`, `@click.option`); Flask/FastAPI/Django route decorators
  (`@app.route`, `@router.get`, `urls.py`); public (non-`_`-prefixed)
  functions/classes/methods.
- **Config**: `os.environ`/`os.getenv` call sites; `pydantic`
  `BaseSettings`/`dataclass` config models; `.env.example`,
  `settings.py`/`config.py` defaults; `argparse` defaults.
- **Behavior**: `celery`/`apscheduler`/cron entries for background jobs;
  `try`/`except` blocks (what error paths exist and what they do);
  `signal.signal` handlers; anything writing files (`open(..., 'w')`) or
  making network calls.
- **Tests**: `pytest`/`unittest` test files — read assertions, not just test
  names; fixtures often encode setup/teardown behavior worth preserving too.

## Node/TypeScript
- **Interface**: `exports`/`module.exports`/named `export`; Express/Fastify/
  Koa route registrations (`.get(`, `.post(`, `router.`); `commander`/
  `yargs` CLI definitions; `package.json` `"bin"` entries.
- **Config**: `process.env` call sites; `.env.example`; config files
  (`config/*.json`, `cosmiconfig`-style loaders); CLI option defaults.
- **Behavior**: `setInterval`/`node-cron`/queue consumers for background
  work; `try`/`catch` and `.catch(` (error paths); `process.on('SIGTERM', ...)`
  and similar; file/network I/O call sites.
- **Tests**: Jest/Mocha/Vitest specs — same rule, read assertions.

## Go
- **Interface**: exported (capitalized) identifiers; `cobra`/`flag`/
  `urfave/cli` command definitions; `net/http`/`gin`/`echo` route
  registrations.
- **Config**: `os.Getenv`/`os.LookupEnv` call sites; `viper`/config-struct
  defaults; flag defaults.
- **Behavior**: goroutines with tickers/cron for background work; `defer`
  and error-wrapping patterns (what's cleaned up, what's the error
  contract); `signal.Notify` handlers.
- **Tests**: `_test.go` files, table-driven tests especially — the table
  itself is often close to a capability list already.

## JVM (Java/Kotlin)
- **Interface**: `public` classes/methods; Spring `@RestController`/
  `@RequestMapping` routes; `picocli`/`args4j` CLI definitions; module
  `exports` in `module-info.java`.
- **Config**: `application.properties`/`application.yml`, `@Value`/
  `@ConfigurationProperties` bindings, `System.getenv`.
- **Behavior**: `@Scheduled` jobs, message-queue consumers, exception
  hierarchies and `@ExceptionHandler`s, shutdown hooks
  (`Runtime.addShutdownHook`).
- **Tests**: JUnit/TestNG test classes.

## Ruby
- **Interface**: `Rails` routes (`config/routes.rb`), Rake tasks, public
  methods on classes not under `private`/`protected`.
- **Config**: `ENV[...]` call sites, `Rails.application.config`, credentials/
  secrets files.
- **Behavior**: `ActiveJob`/Sidekiq workers, `rescue` blocks, `at_exit`/
  signal traps.
- **Tests**: RSpec/Minitest specs.

## Anything not listed here
The categories still apply. Find the language's equivalent of "what's
exported," "what reads environment/config," "what runs on a schedule or in
response to a signal," and "what does the test suite assert" — those four
questions cover interface, config, behavior, and test-as-spec regardless of
ecosystem. If genuinely stuck on tooling for an unusual stack, that's a
step-0-adjacent question to raise rather than a reason to extract less
thoroughly than the languages above.

## Cross-cutting, regardless of source language
- **CI/build config** (`.github/workflows/`, `Makefile`, `Jenkinsfile`) often
  encodes real behavior — a lint rule that's actually load-bearing, a build
  step that generates something, a deploy step with side effects. Skim it.
- **Infra-as-code** (Dockerfile, k8s manifests, Terraform) can imply runtime
  behavior (health-check endpoints, expected ports, volume mounts) that
  isn't visible in application code alone.
- **Version history / CHANGELOG** can surface a capability that shipped and
  is still present but under-documented in current-state docs.

None of this replaces reading the actual code before trusting a grep hit or
a tool's output — same caveat as every other search step across this
skill family.
