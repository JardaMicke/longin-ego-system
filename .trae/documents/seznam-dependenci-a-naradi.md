# Seznam dependencí a nářadí pro LONGIN EGO System

## Základní technologický stack

### Python Dependencies (Core)
```toml
[project.dependencies]
# Core systém
redis = ">=5.0.1"           # Hot memory a event streaming
psutil = ">=5.9.8"          # Systémové metriky a monitoring
docker = ">=7.0.0"          # Sibling containers orchestration
pydantic = ">=2.6.0"       # Data validation a settings
fastmcp = ">=0.1.0"         # Model Context Protocol server
httpx = ">=0.27.0"          # HTTP klient pro API volání
psycopg = {extras = ["binary"], version = ">=3.1.18"}  # PostgreSQL driver
fastapi = ">=0.110.0"       # API framework
gunicorn = ">=0.29.0"        # WSGI server
zeroconf = ">=0.132.0"       # mDNS discovery pro Hive
langgraph = ">=0.2.0"        # Orchestrace workflow
langgraph-checkpoint-postgres = ">=0.1.0"  # Persistence workflowů

# AI/ML dependencies
torch = ">=2.0.0"            # PyTorch pro lokální modely
transformers = ">=4.30.0"    # Hugging Face transformers
sentence-transformers = ">=2.2.0"  # Text embeddings
langchain = ">=0.1.0"        # LLM framework
langchain-community = ">=0.0.1"  # Community extensions

# Computer vision (pro Scanner)
opencv-python = ">=4.8.0"    # Computer vision
pytesseract = ">=0.3.10"    # OCR pro text extraction
pillow = ">=10.0.0"         # Image processing
scikit-image = ">=0.21.0"    # Advanced image processing

# Web automation (pro Scanner)
playwright = ">=1.40.0"     # Browser automation
undetected-chromedriver = ">=3.5.0"  # Anti-bot detection
selenium-stealth = ">=1.0.0"  # Stealth mode pro Selenium

# Performance monitoring
prometheus-client = ">=0.17.0"  # Metrics export
psutil = ">=5.9.8"           # System metrics
py-cpuinfo = ">=9.0.0"       # CPU information
gpustat = ">=1.1.0"          # GPU monitoring
nvidia-ml-py = ">=12.535.0"   # NVIDIA GPU monitoring
```

### JavaScript Dependencies (Frontend)
```json
{
  "dependencies": {
    # Core framework
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    
    # UI komponenty
    "@measured/puck": "^0.14.0",     # Visual editor
    "@radix-ui/react-dialog": "^1.0.0",
    "@radix-ui/react-dropdown-menu": "^2.0.0",
    "@radix-ui/react-tabs": "^1.0.0",
    "lucide-react": "^0.300.0",       # Ikony
    
    # 3D vizualizace
    "three": "^0.158.0",
    "@react-three/fiber": "^8.15.0",
    "@react-three/drei": "^9.88.0",
    "@react-three/postprocessing": "^2.15.0",
    
    # Styling
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    
    # State management
    "zustand": "^4.4.0",
    "swr": "^2.2.0",
    
    # API komunikace
    "axios": "^1.6.0",
    "socket.io-client": "^4.7.0",
    
    # Audio/Video
    "wavesurfer.js": "^7.4.0",
    "recordrtc": "^5.6.0",
    
    # Form handling
    "react-hook-form": "^7.47.0",
    "@hookform/resolvers": "^3.3.0",
    "zod": "^3.22.0",
    
    # Code editor
    "@monaco-editor/react": "^4.6.0",
    "monaco-editor": "^0.44.0"
  }
}
```

## Development a Testing nástroje

### Python Development
```toml
[project.optional-dependencies]
dev = [
    # Testing framework
    "pytest >= 8.0.0",
    "pytest-asyncio >= 0.21.0",
    "pytest-cov >= 4.1.0",
    "pytest-mock >= 3.11.0",
    "pytest-xdist >= 3.3.0",      # Parallel test execution
    "pytest-timeout >= 2.1.0",   # Test timeouts
    "hypothesis >= 6.88.0",       # Property-based testing
    "factory-boy >= 3.3.0",       # Test data factories
    
    # Code quality
    "ruff >= 0.6.0",               # Fast Python linter
    "mypy >= 1.10.0",              # Static type checking
    "black >= 23.9.0",             # Code formatting
    "isort >= 5.12.0",             # Import sorting
    "bandit >= 1.7.0",             # Security linter
    "safety >= 2.3.0",             # Dependency vulnerability scanner
    
    # Documentation
    "sphinx >= 7.2.0",             # Documentation generator
    "sphinx-rtd-theme >= 1.3.0",  # Read the Docs theme
    "myst-parser >= 2.0.0",        # Markdown support
    
    # Development tools
    "ipython >= 8.16.0",           # Enhanced REPL
    "ipdb >= 0.13.0",              # Debugger
    "pre-commit >= 3.5.0",         # Git hooks
    "commitizen >= 3.12.0",        # Conventional commits
    
    # Type stubs
    "types-redis >= 4.6.0",
    "types-psutil >= 5.9.5",
    "types-requests >= 2.31.0",
    "types-setuptools >= 68.2.0"
]
```

### JavaScript Development
```json
{
  "devDependencies": {
    # Testing
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.1.0",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "cypress": "^13.4.0",
    
    # Code quality
    "eslint": "^8.52.0",
    "eslint-config-next": "^14.0.0",
    "eslint-config-prettier": "^9.0.0",
    "prettier": "^3.0.0",
    
    # TypeScript
    "typescript": "^5.2.0",
    "@types/node": "^20.8.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    
    # Development tools
    "husky": "^8.0.0",
    "lint-staged": "^15.0.0",
    "concurrently": "^8.2.0",
    "nodemon": "^3.0.0"
  }
}
```

## Infrastructure a Deployment

### Container technologie
```dockerfile
# Dockerfile pro Python services
FROM python:3.12-slim-bookworm

# Security hardening
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd --create-home --shell /bin/bash longin
USER longin
WORKDIR /home/longin

# Python dependencies
COPY --chown=longin:longin requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application
COPY --chown=longin:longin . .

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Security options
USER longin
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "ganglion.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Orchestration
```yaml
# docker-compose.yml pro development
version: '3.8'

services:
  redis:
    image: redis:7.2-alpine
    command: redis-server --appendonly yes --maxmemory 2gb --maxmemory-policy allkeys-lru
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: longin
      POSTGRES_PASSWORD: longin
      POSTGRES_DB: longin_ego
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./migrations:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U longin"]
      interval: 10s
      timeout: 5s
      retries: 5

  ganglion:
    build:
      context: .
      dockerfile: docker/Dockerfile.ganglion
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    environment:
      - LONGIN_ENV=dev
      - REDIS_URL=redis://redis:6379/0
      - POSTGRES_DSN=postgresql://longin:longin@postgres:5432/longin_ego
    volumes:
      - ./ego:/app/ego:ro  # Read-only soul.md mount
      - /var/run/docker.sock:/var/run/docker.sock  # Docker in Docker
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

### Monitoring a Observability
```yaml
# prometheus.yml pro monitoring
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'longin-ganglion'
    static_configs:
      - targets: ['ganglion:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'longin-system'
    static_configs:
      - targets: ['localhost:9100']  # Node exporter
    scrape_interval: 10s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']  # Redis exporter
    scrape_interval: 10s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']  # Postgres exporter
    scrape_interval: 10s
```

## Security nástroje

### Container Security
```bash
# Trivy pro scanning image vulnerabilities
trivy image longin-ego/ganglion:latest

# Clair pro container vulnerability scanning
clair-scanner --ip="$(hostname -I | awk '{print $1}')" longin-ego/ganglion:latest

# Falco pro runtime security monitoring
falco -r /etc/falco/rules.d/
```

### Code Security
```bash
# Bandit pro Python security linting
bandit -r kernel/ ganglion/ workers/ -f json -o security-report.json

# Safety pro dependency vulnerabilities
safety check --json --output safety-report.json

# Semgrep pro static analysis
semgrep --config=auto --json --output=semgrep-report.json .
```

### Network Security
```bash
# Nmap pro network scanning
nmap -sV -O localhost

# Wireshark pro traffic analysis
wireshark -i any -f "port 8000 or port 3000 or port 6379 or port 5432"

# Fail2ban pro intrusion prevention
fail2ban-client status longin-ego
```

## Performance nástroje

### Profiling
```python
# Memory profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Funkce pro memory profiling
    pass

# CPU profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Kód k profilování
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats()
```

### Load Testing
```python
# Locust pro load testing
from locust import HttpUser, task, between

class LonginEGOUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(10)
    def test_api_endpoint(self):
        self.client.get("/api/health")
    
    @task(5)
    def test_memory_endpoint(self):
        self.client.post("/api/memory/recall", json={"query": "test"})
```

### GPU Monitoring
```python
# NVIDIA GPU monitoring
import pynvml

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

gpu_temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
gpu_mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
```

## Backup a Disaster Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump -h postgres -U longin -d longin_ego -F c -b -v -f backup.dump

# Redis backup
redis-cli SAVE
cp /data/dump.rdb /backups/redis-$(date +%Y%m%d-%H%M%S).rdb

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d-%H%M%S)
docker exec postgres pg_dump -U longin longin_ego > backup-$DATE.sql
docker exec redis redis-cli SAVE
docker cp redis:/data/dump.rdb redis-backup-$DATE.rdb
```

## Závěr

Tento komplexní seznam dependencí a nářadí pokrývá všechny aspekty LONGIN EGO System:

1. **Core dependencies** - základní technologický stack
2. **Development tools** - vývojové a testovací nástroje
3. **Infrastructure** - containerizace a orchestrace
4. **Security tools** - bezpečnostní scanning a monitoring
5. **Performance tools** - profilování a optimalizace
6. **Backup solutions** - disaster recovery

Všechny nástroje jsou open-source nebo mají free tier, což odpovídá požadavku na opensource řešení. Pro produkční nasazení doporučuji:
- Pravidelné aktualizace dependencí
- Automatizovaný security scanning
- Komplexní monitoring a alerting
- Pravidelné zálohování a test obnovy