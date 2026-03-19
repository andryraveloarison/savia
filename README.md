# Savia — SAV Decision Engine

Savia is a smart decision engine designed to assist service technicians in analyzing and prioritizing maintenance tickets. It evaluates ticket completeness, qualifies the issue type, proposes operational actions, and provides a clear audit trail for every decision.

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)
- (Optional) Python 3.12+

### Running the Application
To start the API in production mode:
```bash
chmod +x run_app.sh
./run_app.sh
```
The API will be available at `http://localhost:8000`.

### Running Tests
To run the full test suite and view the Allure report:
```bash
chmod +x run_tests.sh
./run_tests.sh
```
Tests results can be seen at `http://localhost:5050`.

## 📖 API Documentation
Once the app is running, you can access the interactive documentation at:
- **Scalar API Ref**: [http://localhost:8000/docs](http://localhost:8000/docs)

## ⚙️ Configuration
The application is configured via environment variables (or a `.env` file).

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Name of the application | Savia |
| `APP_VERSION` | Version of the application | 1.0.0 |
| `DEBUG` | Enable debug logs | `false` |
| `ENGINE_VERSION` | Internal engine identifier | `savia-mvp-v1` |
| `CONFIDENCE_THRESHOLD_ESCALATE` | Score below which human is required | `0.50` |
| `CONFIDENCE_THRESHOLD_AUTO` | Score above which auto-resolution is possible | `0.85` |

## 🏗️ Architecture
The project follows **Clean Architecture** principles:
- **Domain**: Pure business rules and entities.
- **Application**: Use cases orchestrating the business logic.
- **Infrastructure**: API routes, schemas, and external integrations.
- **Shared**: Common utilities and constants.

## 📄 License
Internal MVP - Proprietary
# savia
