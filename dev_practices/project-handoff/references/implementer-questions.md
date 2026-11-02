# Implementer questions

Prompts for the step-3 implementer pass. They are prompts, not a form. Skip any
area that doesn't apply, and add questions this specific project raises. The
point is to ask what Claude Code will ask halfway through the build, before it
gets there.

## Contents
- Intent and scope
- Shape and boundaries
- Data
- Behavior and errors
- Interfaces
- Stack and dependencies
- Environment and delivery
- Quality bar
- Sequencing

## Intent and scope
- Who uses this, and what's the one job it must do well?
- What's explicitly out of scope, including the things that look in scope but aren't?
- What does "done" look like for the first usable slice?
- Is this a spike/prototype or something meant to last? (This sets the test and docs bar.)

## Shape and boundaries
- Is it a library, CLI, service, UI, or agent tool? One binary or several?
- What are the domain core and the adapters, and which side does each piece of I/O sit on?
- Which existing repos/crates does it reuse or must it match (naming, layout, conventions)?
- Where does it live: a new repo, a monorepo path, or a subfolder of something existing?

## Data
- What are the core types, and which states must be impossible to represent?
- Where is state stored, in what format, and who else reads it?
- Identity: what's the key, is it stable, and are there collisions?
- Size and growth: rows, bytes, how often it changes?

## Behavior and errors
- For each main operation, what happens on bad input, a missing resource, or a partial failure?
- What's retried, what fails loudly, and what's logged?
- Is concurrency real (concurrent I/O, multiple writers) or not?
- Idempotency: what happens if it runs twice?

## Interfaces
- Exact CLI flags, API routes, or tool names and their arguments? Output format (human vs JSON)?
- Exit codes / error shape?
- Config: which knobs exist, where they're set, and their defaults?

## Stack and dependencies
- Language and version, and the framework, if any?
- Which third-party dependencies were agreed on, and which were rejected and why?
- Anything off-limits (cloud services, network calls, licenses)?

## Environment and delivery
- Where does it run: the user's Windows/PowerShell machine, a home server, the cloud, or an air-gapped/NIPR-style environment?
- How is it built, installed, and released? CI?
- Secrets: what's needed, and where do they come from? (Never put them in the pack.)

## Quality bar
- Which tests are required (unit, integration, parity against a reference)?
- What's the performance target, if any, and how will it be measured?
- Docs expected at this stage?

## Sequencing
- What's the first slice to build, and what comes after it?
- What should be stubbed or faked at first?
- Which decisions can wait until the first slice exists?
