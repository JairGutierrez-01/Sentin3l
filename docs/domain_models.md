# Domain Model v0.1
## 1. Purpose

This document defines the conceptual entities of the Sentin3l system.

Its goal is to provide a clear map of the domain objects that exist within the project, distinguishing between:

Core MVP entities

Temporary processing objects

Future entities outside the MVP

The document does not lock the implementation to a specific database schema.
Instead, it serves as a conceptual guide for me and the system design and future expansion.

## 2. Entity Categories

Entities in Sentin3l fall into three main categories:

### Persistent Entities

Objects that should be stored in the database.

### Temporary Processing Objects

Objects that exist during analysis but do not need to be persisted.

### Future Entities

Concepts planned for later stages of the project but intentionally excluded from the MVP.

## 3. Core MVP entities
These entities represent the core persistent model required for the first functional version of Sentin3l.

### 1.ObservedResource
Description:

> Represents a normalized technical representation of a URL or domain that has been analyzed by the system.

> The purpose of this entity is to allow minimal tracking of repeated observations without storing sensitive input data.

Possible attributes

- id

- normalized_url or normalized_url_hash

- hostname

- registrable_domain

- path_hash (optional)

- first_seen_at

- last_seen_at

- occurrence_count

Notes
This entity allows Sentin3l to track how often a resource has appeared without storing full user input history.
--- 

### 2.Analysis
Description:

>Represents a single execution of the Sentin3l analysis pipeline.

>Each analysis corresponds to one evaluation of a submitted URL and stores the final result of the detection process.

Possible attributes:

- id

- observed_resource_id

- analyzed_at

- suspicion_score

- risk_level

- explanation_text

- recommendation_text

- detector_version (optional)

Notes

This is the central entity of the analysis system, connecting the analyzed resource with the detection results.

---
### 3. Analysis Description

> Represents a single execution of the Sentin3l analysis pipeline.

> Each analysis corresponds to one evaluation of a submitted URL and stores the final result of the detection process.

Possible attributes:

- id

- observed_resource_id

- analyzed_at

- suspicion_score

- risk_level

- explanation_text

- recommendation_text

- detector_version (optional)

Notes

This is the central entity of the analysis system, connecting the analyzed resource with the detection results.

---


### 4.AnalysisFlag
Description:

>Represents a flag or indicator detected during a specific analysis.

>Multiple flags may be associated with a single analysis.

Possible attributes:

- id

- analysis_id

- flag_definition_id

- weight_applied

- evidence_summary (optional)

Notes

This entity links the detection signals to the specific analysis in which they were triggered.

### 5.FlagDefinition
Description

>Represents a catalog of all possible detection flags used by the system.

>Using a centralized flag catalog helps maintain consistency and avoids hardcoded detection labels.

Possible attributes:

- id

- code

- name

- description

- default_weight

- is_active

Example flags:

    IP_IN_HOST
    LONG_URL
    SUSPICIOUS_KEYWORD
    EXCESSIVE_SUBDOMAINS
    UNUSUAL_CHARACTER_PATTERN

## 4. Embedded Result Components

These concepts are part of the analysis output but do not necessarily require separate database tables.

### 1.Explanation

Human-readable explanation describing why the analyzed URL may be suspicious.

This explanation translates technical indicators into language understandable by non-experts.

Example:

    "The URL contains an IP address instead of a domain name and has an unusually long path structure."

### 2.Recommendation

Basic guidance provided to the user after analysis.

Examples:

- Exercise caution before opening the link

- Verify the sender of the message

- Avoid visiting the URL

- nspect the domain manually

In the MVP, both explanation and recommendation are stored as fields within the Analysis entity.

## 5. Temporary Processing Objects

These objects exist during the analysis process but are not intended to be persisted in the database.

### 1. URLSubmission
Description:

> Represents the raw URL input received from the user.

Possible attributes:

- raw_url

- submitted_at

- request_id (optional)

Notes

This object exists only during request processing and should not necessarily be stored.

### 2.ParsedURL
Description

>Represents the structural decomposition of a URL used for analysis.

Possible attributes:

- scheme

- hostname

- registrable_domain

- subdomains

- port

- path

- query

- fragment

- length

- uses_ip_host

Notes

This object enables detection rules to operate on structured URL components rather than raw strings.

### 3. NormalizationResult
Description:

> Represents the result of URL normalization.

Possible attributes:

- normalized_url

- normalization_notes

- normalization_warnings

### 4. FeatureSet
Description:

> Represents features extracted from the parsed URL used for detection rules.

Possible attributes:

- url_length

- subdomain_count

- contains_ip

- suspicious_keyword_hits

- has_punycode

- query_param_count

### 5. ScoreBreakdown
Description:

>Internal representation of how the final suspicion score was calculated.

Example contributions:

    LONG_URL → +15

    IP_IN_HOST → +25

    SUSPICIOUS_KEYWORD → +20

This object helps explain scoring logic but does not need to be stored in the database.

## 6. Core Relationships

The core relationships of the MVP model can be summarized as follows.

### ObservedResource → Analysis
One resource may be analyzed multiple times.

### Analysis → AnalysisFlag
One analysis may produce multiple flags.

### FlagDefinition → AnalysisFlag
A flag type may appear in many analyses.

## 7. MVP Minimal Persistent Model

> The minimal persistent schema required for the MVP can be summarized as:

ObservedResource

Analysis

AnalysisFlag

FlagDefinition

All other entities operate as internal domain objects or future architectural extensions.

## 8. Version Note

This document represents Domain Model v0.1.

The model may evolve as Sentin3l expands its detection capabilities and introduces additional analysis modules.