# Changelog

All notable changes to the Savia project will be documented in this file.

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
