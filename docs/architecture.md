# Sentin3l – Architecture Sketch v0.2

## 1. Project Goal

The project does not aim to be a full threat intelligence platform. Its goal is to provide a simple, explainable, and privacy-conscious URL analysis experience.

## 2. Input

Current primary input:

- one URL submitted by the user

Future inputs may be added later, but they are outside the current MVP scope.

## 3. Output

The system should return:

- a suspicion score
- detected indicators or flags
- a human-readable explanation of why the URL may be suspicious
- basic guidance or recommendations for the user

## 4. Internal Processing

The exact internal detection logic is intentionally left open at this stage.

This is a learning-focused part of the project and will evolve during development as detection strategies are researched, tested, and improved.

The system is expected to include some form of:

- URL parsing
- indicator detection
- scoring
- explanation generation

However, implementation details are not fixed in this early version of the document.

## 6. Data Storage Principles

Sentin3l follows minimal data retention principles.

The system may store limited technical metadata for analysis improvement and statistics, such as:

- URL domains
- hashed URL fragments or partitions
- detection flags
- counts and frequency statistics

The system must not store:

- user passwords
- credential inputs
- raw sensitive secrets

## 7. Privacy Principles

Sentin3l is designed with a privacy-conscious approach.

Core privacy principles include:

- minimal retention
- no password storage
- no unnecessary collection of personal data
- storage of technical indicators instead of raw sensitive input where possible

## 8. MVP Scope

Included in the MVP:

- URL submission
- suspicion scoring
- explanation in plain language
- minimal technical metadata storage
- basic statistics or repeated occurrence tracking

Not included in the MVP:

- user authentication
- account creation
- credential storage
- full breach intelligence platform behavior
- large-scale OSINT capabilities

## 9. Design Philosophy

The project architecture should remain modular and scalable, but not overdesigned.

This document defines the current direction of the project without locking all internal functions too early.

The goal is to support learning, experimentation, and gradual refinement.

##