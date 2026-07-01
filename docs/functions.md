# Sentin3l – Technical Function & Utilities Reference (v1.0)

## 1. Overview
This document serves as a technical reference manual for the core codebase of **Sentin3l**. It maps out the inner workings of the system's utilities (`utils/`) and orchestration business logic (`services/`) required for modular URL analysis and privacy-conscious phishing detection.

---

## 2. Utility Layer (`utils/`)
The utility layer contains pure, stateless functions designed to transform data structures and evaluate static heuristic parameters without inducing database side-effects.

### 2.1. URL Tools (`url_tools.py`)
Responsible for data normalization, metadata decomposition, and ensuring user privacy before storage or pipeline processing.

| Function Name | Description | Inputs | Outputs |
| :--- | :--- | :--- | :--- |
| `normalize_and_redact_url` | Sanitizes raw inputs. Lowers domains, censors all query parameter values into `[REDACTED]`, and drops client-side browser fragments. | `raw_url: str` | `str` (Sanitized URL) |
| `extract_domain_info` | Safely extracts full network hostnames and public registrable root domains leveraging `tldextract`. | `raw_url: str` | `Tuple[str, str]` (Host, Root Domain) |
| `generate_url_hash` | Generates a secure cryptographic SHA-256 string from a redacted URL to act as a unique system key. | `redacted_url: str` | `str` (64-char Hex Hash) |
| `process_url_for_storage` | Orchestrates the translation of an input string into a dictionary schema ready for model parsing. | `raw_url: str` | `Dict[str, str]` (Payload schema) |

### 2.2. Threat Heuristics & Rules (`detectors.py`)
Independent assessment algorithms returning concrete suspicion dictionaries (`{"code": str, "evidence": str}`) when an indicator flags positive, otherwise returning `None`.

* **`detect_ip_host(hostname: str)`**: Tests whether the targeted host location bypasses domains to use a raw IP address representation directly.
* **`detect_long_url(url: str, limit: int = 100)`**: Evaluates whether structural lengths cross baseline parameters (Defaults to 100 characters).
* **`detect_suspicious_tld(registrable_domain: str, suspicious_tlds: list[str])`**: Flags top-level extensions strongly correlated with disposable campaign patterns.
* **`detect_sensitive_keywords(url: str, sensitive_keywords: list[str])`**: Scans structural elements looking for critical social engineering triggers (e.g., 'login', 'secure').
* **`detect_punycode(hostname: str)`**: Flags suspicious `xn--` markers indicative of internationalized homograph character spoofing attempts.
* **`detect_excessive_subdomains(hostname: str)`**: Evaluates host point structures to discover multi-level tunneling tactics (Flags if levels > 4).
* **`detect_typosquatting(registrable_domain: str, target_brands: list[str])`**: Compares string distances against protected profiles using `SequenceMatcher` to catch lookalike brand names.
* **`detect_url_shortener(hostname: str, url_shorteners: list[str])`**: Determines whether redirection mechanisms mask explicit destinations.
* **`detect_brand_impersonation(hostname: str, registrable_domain: str, target_brands: list[str])`**: Catches instances where trusted brand assets populate subdomains outside their rightful root context.
* **`detect_at_symbol(url: str)`**: Flags `@` characters utilized to distort browser parsing destinations.
* **`detect_double_extension(url_path: str, dangerous_extensions: list[str])`**: Counts trailing extensions to discover spoofed executable formats inside paths.
* **`detect_insecure_protocol(url: str)`**: Evaluates transport vulnerabilities by checking for legacy, unencrypted `http://` prefixes.

---

## 3. Service Layer (`services/`)
The transactional engine of Sentin3l. These modules connect utility inputs, handle operational dependencies, manage state, and interact with the SQLAlchemy database context.

### 3.1. Analysis Engine (`analysis_service.py`)
The pipeline coordinator responsible for assembling dynamic heuristic inputs and determining severe threat categories.

* **`load_threat_intel()`**: Loads critical tracking matrices from local storage files. Cached efficiently using Python's `@lru_cache` to minimize disk read bottlenecks.
* **`run_security_detectors(...)`**: Bundles heuristic signatures sequentially into an executable list context to efficiently filter out clean indicators.
* **`calculate_risk_level(suspicion_score: int, total_flags: int)`**: Evaluates absolute weights against mathematical categories to yield uniform evaluation status labels (`Safe`, `Low`, `Medium`, `High`).
* **`create_analysis_for_resource(db: Session, resource: ObservedResource, raw_url: str)`**: Runs the complete analysis suite, maps weights to central DB structures, cascades transactional flags, and commits the final execution records.
* **`get_recent_analyses(db: Session, limit: int = 10)`**: Queries chronological history logs. Performance optimized with SQLAlchemy `joinedload` techniques to bypass classical N+1 overheads.

### 3.2. Observed Resource Ledger (`observed_resource_service.py`)
Ensures historical compliance with minimal metadata tracking parameters.

* **`get_resource_by_hash(db, normalized_url_hash)`**: Performs index lookups by unique cryptographic hashes to quickly find previously assessed links.
* **`create_resource(db, ...)`**: Records structural metadata contexts for a brand-new, unique target destination.
* **`update_occurrence(db, resource)`**: Increments tracking statistics and updates chronological timestamps when matching hashes resurface.
* **`get_or_create_resource(db, raw_url)`**: Primary orchestration gate. Transforms strings into secure schemas and transparently branches executions into update or creation workflows.

### 3.3. Flag Definitions & Catalogue (`flag_definition_service.py`)
Provides stability across data environments by keeping labels out of runtime code strings.

* **`get_flag_by_code(db, code)`**: Looks up static structural rules to determine target score increments during analysis tasks.
* **`get_all_active_flags(db)`**: Returns comprehensive active indices, ideal for populating dashboards or caching mechanisms.
* **`seed_default_flags(db)`**: Safe configuration seeder. Parses local rule configuration arrays and inserts new rules while safely ensuring idempotency.

### 3.4. Monitored Brand Assets (`brand_service.py`)
Supplies brand reference objects to combat lookalike squatting and impersonation mechanics.

* **`seed_brands_from_file(db, filename)`**: High-performance synchronize algorithm. Performs set differences (`file_brands - existing_brands`) to execute optimized batch inserts on missing definitions.
* **`get_active_brands(db)`**: Delivers flat lists of active protected strings required by matching evaluation logic blocks.