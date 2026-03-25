# Savia — SAV Decision Engine

Savia is a smart decision engine designed to assist service technicians in analyzing and prioritizing maintenance tickets. It evaluates ticket completeness, qualifies the issue type, proposes operational actions, and provides a clear audit trail for every decision.

## Quick Start

### Prerequisites
- **Docker Desktop** (includes Docker & Docker Compose)
  - [Download for Windows](https://www.docker.com/products/docker-desktop)
  - [Download for macOS](https://www.docker.com/products/docker-desktop)
  - [Installation for Linux](https://docs.docker.com/engine/install/)
- *(Optional)* Python 3.12+ (for running locally without Docker)
- *(Optional)* GNU Make
  - **Linux**: Usually pre-installed with build-essential (`sudo apt install build-essential`)
  - **macOS**: Install Xcode Command Line Tools (`xcode-select --install`)
  - **Windows**: Install via WSL, Chocolatey (`choco install make`), or Git Bash (comes with GNU Make)

### Initial Setup
```bash
# Optional: Copy example config (app uses sensible defaults without it)
cp .env.example .env

# Optional: For SonarCloud analysis, add your token to .env
# SONAR_TOKEN=your_token_here  (get from https://sonarcloud.io/account/security/)

# 1. Verify Docker is running
# 2. Start the application (first time - with build)
make start
# Or without Make: docker compose up --build -d
```

## Running the Application

### Using Makefile (Recommended - All Platforms)
```bash
# First time setup - Build and start
make start

# Subsequent runs - Just start (no rebuild)
make run

# View logs
make logs

# Stop application
make stop

# View all available commands
make help
```

### Using Docker Compose directly
```bash
# Start with build
docker compose up --build

# Stop
docker compose down

# View logs
docker compose logs -f savia-api
```

The API will be available at `http://localhost:8000`.

## Running Tests

### Using Makefile (Recommended)
```bash
# Run tests + Allure report server
make test

# View test logs
make test-logs

# Stop test services
make test-stop
```

### Using Docker Compose directly
```bash
# Run tests
docker compose -f docker-compose.test.yml down --remove-orphans
docker compose -f docker-compose.test.yml run --rm tests

# Start Allure report server
docker compose -f docker-compose.test.yml up -d allure
```

**Test results** can be viewed at `http://localhost:5050` (Allure Report).

## Code Quality Analysis (SonarCloud) — Optional

If you want code quality analysis, setup SonarCloud:

```bash
# Get token from: https://sonarcloud.io/account/security/
# Add to .env:
SONAR_TOKEN=your_token_here

# Run analysis
make sonar
```

**Results**: [SonarCloud - Savia Project](https://sonarcloud.io/project/overview?id=andryraveloarison_savia)

## API Documentation
Once the app is running, you can access the interactive documentation at:
- **Scalar API Ref**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

## ⚙️ Configuration

The app works **out-of-the-box** with sensible defaults. `.env` is **completely optional**.

### When You Need `.env`
- To **change default settings** (thresholds, debug mode, etc.)
- To **enable SonarCloud analysis** (add `SONAR_TOKEN`)

### Available Variables
```env
# Core Application (optional)
DEBUG=false                        # Enable debug logs
ENGINE_VERSION=savia-mvp-v1        # Engine identifier

# Confidence Thresholds (optional)
CONFIDENCE_THRESHOLD_ESCALATE=0.40 # Below: require human review (0-1)
CONFIDENCE_THRESHOLD_AI=0.90       # Above: fully trust AI (0-1)

# AI Features (optional)
AI_ENABLED=true                    # Enable/disable AI analysis
AI_PROVIDER=openai                 # AI provider: openai or mock

# SonarCloud (optional, only for code quality analysis)
SONAR_TOKEN=                       # Get from https://sonarcloud.io/account/security/
```

**No .env file needed?** Just run `make run` — everything works with defaults!

## Project Structure & Architecture

```
app/
├── core/                # 🔧 Technical foundation
│   ├── config.py        # Environment & settings
│   ├── logging.py       # Logging setup
│   ├── middleware.py    # HTTP middleware
│   └── exceptions.py    # Global exception handlers
│
├── domain/              # Business Core (Pure Logic)
│   ├── entities/        # Domain models
│   ├── services/        # Business logic
│   ├── rules_engine/    # Decision rules
│   └── types/           # Domain types
│
├── application/         # Use Cases
│   └── use_cases/       # Business workflows
│
├── infrastructure/      # External Adapters
│   ├── api/             # HTTP routes
│   ├── schemas/         # Request/response validation
│   └── ai/              # AI integrations
│
└── shared/              # Common Utilities
    ├── constants/       # Global constants
    ├── types/           # Shared types
    └── utils/           # Helper functions

tests/                   # Test suite (unit + integration)
coverage/                # Test reports
docker-compose.yml       # Production config
docker-compose.test.yml  # Test config
Dockerfile              # Container definition
Makefile                # Commands (recommended)
```

### Clean Architecture Principles

The code follows **Clean Architecture** with dependencies pointing inward only:

```
HTTP Request
    ↓
Infrastructure (API) → Application (Use Cases) → Domain (Business Rules)
```

- **Domain**: Pure business logic, no external dependencies
- **Application**: Orchestrates domain logic for use cases
- **Infrastructure**: Technical adapters (API, databases, AI services)
- **Core**: Cross-cutting concerns (config, logging, middleware)
- **Shared**: Common utilities used by multiple layers

**Key**: Domain layer has zero knowledge of API, databases, or frameworks.

## Development

### Local Setup (without Docker)
```bash
# Using Makefile
make install
make dev

# Or manually:
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### All Makefile Commands
```bash
make run               # Start with Docker
make test              # Run tests + Allure report
make sonar             # SonarCloud analysis (optional)
make stop              # Stop all services
make logs              # View logs
make dev               # Run locally
make clean             # Remove containers
make help              # Show all commands
```

### 🚀 Without Make? (Windows Users)
If you don't have Make installed, use Docker Compose directly:
```bash
# Start application
docker compose up --build

# Run tests  
docker compose -f docker-compose.test.yml down --remove-orphans
docker compose -f docker-compose.test.yml run --rm tests
docker compose -f docker-compose.test.yml up -d allure

# Stop
docker compose down
```

## Stopping Services

```bash
make stop               # Stop all
make test-stop          # Stop tests only
# Or: docker compose down
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port already in use** (8000 or 5050) | Linux: `lsof -i :8000 && kill -9 <PID>` \| Windows: `netstat -ano \| findstr :8000 && taskkill /PID <PID> /F` |
| **Docker daemon not running** | Start Docker Desktop or `sudo systemctl start docker` on Linux |
| **`make` command not found** | **Linux**: Install: `sudo apt install build-essential` \| **macOS**: Install Xcode tools: `xcode-select --install` \| **Windows**: Install via WSL, Chocolatey, or use `docker compose` directly (no Make needed) |
| **Allure report not loading** | Check container: `make ps` or restart: `docker compose -f docker-compose.test.yml up -d allure` |
| **SONAR_TOKEN not found** | Add to `.env`: `SONAR_TOKEN=your_token_here` (get from https://sonarcloud.io/account/security/) or skip `make sonar` |
| **No `.env` file** | Not needed! App uses defaults. Only required for SonarCloud or custom settings. |

## Test Coverage
After running tests, coverage report is available at:
- `coverage/coverage.xml` - XML report
- Allure HTML report at `http://localhost:5050`

## License
Internal MVP - Proprietary
