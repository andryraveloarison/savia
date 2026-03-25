# Changelog

All notable changes to the Savia project will be documented in this file.

## [1.4.0] - 2026-03-25

### Added
- **Rate Limiting**: Protection against abuse by limiting the number of requests per client.
- **Payload Size Limit**: Maximum request body size to prevent large payload attacks and memory issues.
- **AI Timeout Handling**: Timeout added to AI calls to prevent blocking requests when the AI service is slow or unavailable.
- **Constraints Service**: Centralized validation for request constraints (payload size, attachments count, etc.).
- **Constraints Constants**: Added shared constants for system limits and validation rules.
- **Unit Tests**: Added tests for ConstraintsService to ensure validation logic reliability.

### Changed
- **Analyze Ticket Use Case**: Integrated constraints validation and timeout handling into the analysis workflow.
- **Exception Handling**: Improved custom exceptions for constraint violations and timeout errors.

### Security
- Added protections against DoS via large payloads.
- Prevented long blocking calls to external AI services.
- Improved API robustness and input validation.


## [1.3.0] - 2026-03-24

### Added
- **Makefile**: Unified command interface for all operations (run, test, sonar, etc.) - works on Linux, macOS, and Windows.
- **.env.example**: Configuration template with well-documented variables and setup instructions.
- **Enhanced Architecture Documentation**: Clarified Clean Architecture layers with clear separation between Domain, Application, Infrastructure, Core, and Shared layers.
- **SonarCloud Integration**: Added `make sonar` and `make sonar-token` commands for code quality analysis (optional feature).

### Changed
- **README Restructure**: 
  - Merged Project Structure and Architecture sections for clarity
  - Simplified setup instructions with initial setup steps
  - Marked SonarCloud as optional
  - Consolidated troubleshooting into a concise table format
  - Reduced README size by ~30% while improving clarity
- **Environment Configuration**: Improved .env file loading in Makefile to properly export variables.
- **Help Command**: Enhanced `make help` to display all available commands with descriptions.

### Removed
- **Deprecated Scripts**: Removed `run_app.sh`, `run_tests.sh`, `run_sonar.sh` and their Windows equivalents (`*.bat`, `*.ps1`) - all functionality now integrated into Makefile.
- **Redundant Code**: Eliminated script duplication across operating systems.

### Fixed
- **SONAR_TOKEN Loading**: Fixed .env variable export in Makefile so tokens are properly loaded on all platforms.
- **Cross-Platform Compatibility**: All commands now work identically on Windows, macOS, and Linux.

## [1.2.0] - 2026-03-24

### Added
- **Extended Test Suite**: Added targeted unit tests to cover previously untested branches across `AIAdapter`, `AIAnalysisService`, `JustificationService`, `OrientationService`, `CompletenessService`, `TicketEntity`, and `CustomJsonFormatter`.

### Fixed
- **SonarCloud Coverage Alignment**: Fixed coverage report path mismatch between Docker test container and SonarCloud by enabling `relative_files = true` in `.coveragerc`.
- **Coverage Scope**: Excluded test files from coverage measurement to align local and SonarCloud metrics.

## [1.1.0] - 2026-03-23

### Added
- **AI Layer Orchestration**: Added `AIAnalysisService` to manage AI analysis and deterministic fallbacks.
- **AIAdapter**: Introduced a mockable `AIAdapter` for flexible AI integration.
- **Enhanced Payload Validation**: Made `attachments` and `history` mandatory in the `TicketInput` schema to ensure data completeness.

### Changed
- **Audit logic Refactoring**: Simplified `AuditService` to focus on decision provider transparency.
- **Modernized Codebase**: Resolved multiple deprecation warnings related to Pydantic V2, Starlette status codes, and JSON logging.

### Fixed
- **Pydantic Validation errors**: Fixed various validation issues in API responses and audit logs.
- **Test Payloads**: Updated all tests to work with the new mandatory fields.

## [1.0.0] - 2026-03-19

### Added
- **Core Engine**: Initial release of the decision engine for SAV ticket analysis.
- **Completeness Check**: Validation of mandatory fields and message content.
- **Qualification**: Automatic categorization (Heating, Ventilation, Plumbing) with inconsistency detection.
- **Orientation**: Recommendation of operational actions (Intervention vs. Human Escalation) based on urgency and equipment knowledge.
- **Confidence Scoring**: Multi-weighted scoring system to justify automated decisions.
- **Structured Logging**: JSON-formatted logs with `correlation_id`, `ticket_id`, and processing duration.
- **API Reference**: Scalar integration for interactive documentation.
- **Testing Suite**: 25+ integration and unit tests with coverage reporting (97%+).
- **Docker Integration**: Production and Test environments containerized.
- **Environment Configuration**: Robust setting management using Pydantic.

### Changed
- Refactored rules engine to separate domain logic from infrastructure details.
- Standardized HTTP status codes (200, 400, 422, 500).