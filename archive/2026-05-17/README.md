# Doompile

Doompile is a CLI-first learning planner built from saved resources, starting with Twitter bookmarks.

The system is designed to turn noisy saved artifacts into a curated resource graph that can answer:
- what is this resource actually about?
- where is the original source?
- what should I learn first?
- what should I learn next?

## Status

This repository is in phase 1 scaffolding.

Current focus:
- establish the project structure
- document the product and architecture
- prepare the codebase for Twitter import, source resolution, review, and path generation

CLI convention:
- primary command name: `pile`

## Product Direction

This is not primarily a bookmark archive.

It is a source-first, goal-first system for:
- recovering high-signal learning resources
- organizing them into concepts and topics
- generating opinionated learning paths
- tracking progress through those paths

## Core Principles

- CLI-first user experience
- high-quality curation with manual review
- Twitter-first distribution, connector-generic architecture
- strong typing and explicit interfaces
- observability and LLM tracing as first-class features

## Planning Profile

Default profile: `Veteran Builder`

Biases:
- fundamentals before novelty
- practical understanding over shallow coverage
- real-world tradeoffs and implementation detail
- small number of high-signal resources
- early exercises and toy projects

## Documentation

- `docs/project-spec.md` contains the current project specification.
- `AGENTS.md` contains engineering and contributor guidance.
- `MEMORY.md` tracks current decisions, open work, and important references.
