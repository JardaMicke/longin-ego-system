# Technická architektura hostingu Longin EGO System

## 1. Architektonické schéma hostingové infrastruktury

```mermaid
graph TB
    subgraph "Internet & DNS"
        DNS[Webglobe DNS]
        SSL[Let's Encrypt SSL]
        MON[Monitoring: Netdata]
    end
    
    subgraph "Produkční server: longinegosystem.eu"
        subgraph "Reverse Proxy Layer"
            CAD[Caddy 2.9.1
                 Automatic HTTPS
                 HTTP/2 + QUIC]
        end
        
        subgraph "Application Layer - Docker Stack"
            subgraph "Frontend Services"
                CUI[Cortex UI
                     Next.js 14
                     Port: 3000
                     Puck Editor]
            end
            
            subgraph "Backend Services"
                GA[Ganglion API
                    FastAPI/Uvicorn
                    Port: 8000
                    Python 3.12]
            end
            
            subgraph "Data Layer"
                RD[Redis 7.2
                   Hot Memory
                   Streams
                   Port: 6379]
                
                PG[PostgreSQL 16
                   pgvector extension
                   Cold Memory
                   Port: 5432]
            end
        end
        
        subgraph "System Layer"
            BK[Backup System
                Daily Cron
                7-day retention]
            
            LG[Log Aggregation
                Docker Logs
                System Logs]
        end
    end
    
    subgraph "Local Network Integration"
        GN1[Ganglion Node 1
             RTX 3060
             32GB RAM]
        
        GN2[Ganglion Node 2
             Laptop/HTPC
             Local LLM]
        
        GN3[Ganglion Node 3
             Development PC
             Browser Testing]
    end
    
    DNS -->|A record| CAD
    CAD -->|/| CUI
    CAD -->|/v1/*| GA
    GA -->|Redis Streams| RD
    GA -->|Persistent| PG
    CUI -->|Layout Data| PG
    GA -->|mDNS Discovery| GN1
    GA -->|RPC Calls| GN2
    GA -->|Sandbox| GN3
    
    MON -.->|Metrics| CAD
    MON -.->|Metrics| GA
    MON -.->|Metrics| RD
    MON -.->|Metrics| PG
```

## 2. Technologický stack

### 2.1 Core Technologies
- **Container Runtime**: Docker 24.0+ with Docker Compose v2
- **Orchestration**: Docker Compose (single-node)
- **Reverse Proxy**: Caddy 2.9.1 (automatic HTTPS)
- **Load Balancing**: Caddy's built-in (round-robin, health checks)

### 2.2 Backend Stack
- **Runtime**: Python 3.12 slim
- **Framework**: FastAPI 0.110+ with Uvicorn
- **Message Broker**: Redis Streams 7.2
- **Database**: PostgreSQL 16 with pgvector extension
- **Memory Management**: Redis (hot) + PostgreSQL (cold)
- **Orchestration**: LangGraph for ERTDSD workflows

### 2.3 Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Build Tool**: Vite (via Next.js)
- **UI Editor**: Puck 0.15.0 (visual editor)
- **Styling**: Tailwind CSS (implied)
- **State**: Server components + client hydration

### 2.4 Network & Discovery
- **Service Discovery**: mDNS (Zeroconf) via python-zeroconf
- **Inter-service**: Docker networking (longin-net)
- **External**: Caddy reverse proxy with automatic SSL

## 3. Infrastrukturní komponenty

### 3.1 Server specifikace (Doporučeno)
```yaml
CPU: AMD Ryzen 7 5800X / Intel i7-12700K (8+ cores)
RAM: 64GB DDR4-3200 (32GB minimum)
GPU: NVIDIA RTX 3060 12GB / RTX 4070 12GB
Storage: 1TB NVMe SSD (500GB minimum)
Network: 1Gbps symmetric (100Mbps minimum)
OS: Ubuntu 22.04 LTS / Debian 12
```

### 3.2 Docker Services Configuration

**Redis Service:**
```yaml
redis:
  image: redis:7.2-alpine
  command: ["redis-server", "--appendonly", "yes"]
  ports: ["6379:6379"]
  volumes: ["redis-data:/data"]
  networks: ["longin-net"]
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "redis-cli", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
```

**PostgreSQL Service:**
```yaml
postgres:
  image: pgvector/pgvector:pg16
  environment:
    POSTGRES_USER: longin
    POSTGRES_PASSWORD: [SECURE_PASSWORD]
    POSTGRES_DB: longin_ego
  ports: ["5432:5432"]
  volumes: ["postgres-data:/var/lib/postgresql/data"]
  networks: ["longin-net"]
  restart: unless-stopped
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U longin"]
    interval: 30s
    timeout: 10s
    retries: 3
```

**Ganglion API Service:**
```yaml
ganglion-api:
  image: longin-ego/ganglion:latest
  build:
    context: .
    dockerfile: docker/Dockerfile.ganglion
  environment:
    LONGIN_ENV: prod
    REDIS_URL: redis://redis:6379/0
    POSTGRES_DSN: postgresql://longin:[PASSWORD]@postgres:5432/longin_ego
  ports: ["8000:8000"]
  depends_on:
    redis:
      condition: service_healthy
    postgres:
      condition: service_healthy
  networks: ["longin-net"]
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/v1/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

**Cortex UI Service:**
```yaml
cortex-ui:
  image: longin-ego/cortex:latest
  build:
    context: .
    dockerfile: docker/Dockerfile.cortex
  environment:
    NODE_ENV: production
    LONGIN_ENV: prod
    POSTGRES_DSN: postgresql://longin:[PASSWORD]@postgres:5432/longin_ego
  ports: ["3000:3000"]
  depends_on:
    postgres:
      condition: service_healthy
  networks: ["longin-net"]
  restart: unless-stopped
```

### 3.3 Caddy Reverse Proxy Configuration

**Primary Caddyfile:**
```
longinegosystem.eu {
    redir https://www.longinegosystem.eu{uri}
}

www.longinegosystem.eu {
    # API routing
    reverse_proxy /v1/* ganglion-api:8000 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
        
        # Health checks
        health_uri /v1/health
        health_interval 30s
        health_timeout 10s
    }
    
    # UI routing
    reverse_proxy cortex-ui:3000 {
        header_up Host {host}
        header_up X-Real-IP {remote}
        header_up X-Forwarded-For {remote}
        header_up X-Forwarded-Proto {scheme}
    }
    
    # Security headers
    header {
        X-Frame-Options DENY
        X-Content-Type-Options nosniff
        X-XSS-Protection "1; mode=block"
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
    }
    
    # Compression
    encode gzip zstd
    
    # Logging
    log {
        output file /var/log/caddy/access.log
        format json
    }
}
```

## 4. Security Architecture

### 4.1 Network Security
- **Firewall**: UFW with minimal open ports (22, 80, 443)
- **Docker Isolation**: Custom bridge network (longin-net)
- **Service Communication**: Internal Docker networking only
- **External Access**: Only through Caddy reverse proxy

### 4.2 Application Security
- **SSL/TLS**: Automatic Let's Encrypt certificates
- **HTTP Security Headers**: HSTS, CSP, XSS protection
- **Rate Limiting**: Caddy's built-in rate limiting
- **Input Validation**: FastAPI automatic validation
- **SQL Injection**: Parameterized queries via psycopg

### 4.3 Container Security
- **Base Images**: Official slim images (python:3.12-slim, node:20-alpine)
- **Non-root User**: Services run as non-privileged users
- **Read-only Filesystems**: Where possible
- **Resource Limits**: Memory and CPU constraints
- **Security Scanning**: Regular vulnerability scanning with Trivy

### 4.4 Data Security
- **Encryption at Rest**: PostgreSQL TDE, Redis password protection
- **Encryption in Transit**: TLS 1.3 for all external connections
- **Backup Encryption**: Encrypted backups with GPG
- **Secret Management**: Environment variables, Docker secrets

## 5. Performance Optimization

### 5.1 Caching Strategy
- **Redis**: Hot memory for active conversations and streams
- **PostgreSQL**: Query result caching, prepared statements
- **HTTP**: Caddy caching for static assets
- **Next.js**: Static generation, ISR where applicable

### 5.2 Database Optimization
- **Indexes**: pgvector HNSW for embeddings, B-tree for lookups
- **Partitioning**: Time-based partitioning for audit logs
- **Connection Pooling**: PgBouncer for PostgreSQL
- **Query Optimization**: Explain analyze, query planning

### 5.3 Resource Management
- **Memory Limits**: Container-level memory constraints
- **CPU Throttling**: CPU quota management
- **GPU Scheduling**: Single-GPU lock mechanism
- **Pruning**: Aggressive memory cleanup post-execution

### 5.4 Load Balancing & Scaling
- **Horizontal**: Multiple Ganglion nodes (distributed)
- **Vertical**: Container resource scaling
- **Health Checks**: Circuit breaker pattern
- **Auto-scaling**: Manual scaling based on metrics

## 6. Monitoring & Observability

### 6.1 Metrics Collection
- **System Metrics**: CPU, Memory, Disk, Network (Netdata)
- **Application Metrics**: Custom metrics via Prometheus
- **Business Metrics**: Task completion rates, error rates
- **SLI/SLO**: Availability, latency, throughput

### 6.2 Logging Architecture
- **Structured Logging**: JSON format for all logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Correlation IDs**: Request tracing across services
- **Log Aggregation**: Centralized logging (ELK stack optional)

### 6.3 Alerting
- **Health Checks**: Endpoint monitoring every 30s
- **Resource Alerts**: CPU > 80%, Memory > 85%, Disk > 90%
- **Application Alerts**: Error rate > 5%, Response time > 2s
- **Security Alerts**: Failed auth, suspicious activity

### 6.4 Dashboards
- **System Dashboard**: Server resource utilization
- **Application Dashboard**: Service health, request metrics
- **Business Dashboard**: Task processing, user activity
- **Security Dashboard**: Failed requests, blocked attempts

## 7. Backup & Disaster Recovery

### 7.1 Backup Strategy
- **Frequency**: Daily full backups, hourly incremental
- **Retention**: 7 days full, 30 days incremental
- **Encryption**: GPG encryption for all backups
- **Storage**: Local + Cloud (S3-compatible)
- **Testing**: Weekly restore testing

### 7.2 Database Backups
```bash
# PostgreSQL backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec postgres pg_dump -U longin -d longin_ego | \
  gzip | \
  gpg --cipher-algo AES256 --compress-algo 2 --symmetric --output "/backup/postgres_$DATE.sql.gz.gpg"
```

### 7.3 Redis Backups
```bash
# Redis backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec redis redis-cli BGSAVE
docker cp redis:/data/dump.rdb "/backup/redis_$DATE.rdb"
gpg --cipher-algo AES256 --compress-algo 2 --symmetric --output "/backup/redis_$DATE.rdb.gpg" "/backup/redis_$DATE.rdb"
```

### 7.4 Disaster Recovery
- **RTO**: 1 hour (maximum acceptable downtime)
- **RPO**: 1 hour (maximum acceptable data loss)
- **Failover**: Manual process with automated scripts
- **Documentation**: Step-by-step recovery procedures

## 8. Deployment Pipeline

### 8.1 CI/CD Architecture
```mermaid
graph LR
    DEV[Developer] -->|Push| GIT[Git Repository]
    GIT -->|Trigger| CI[GitHub Actions]
    CI -->|Build| TEST[Unit Tests]
    CI -->|Security| SCAN[Security Scan]
    CI -->|Build| IMAGE[Docker Images]
    IMAGE -->|Push| REG[Container Registry]
    REG -->|Deploy| PROD[Production Server]
    PROD -->|Verify| HEALTH[Health Checks]
```

### 8.2 Deployment Process
1. **Build**: Multi-stage Docker builds
2. **Test**: Unit tests, integration tests, security scans
3. **Package**: Docker images with semantic versioning
4. **Deploy**: Blue-green deployment with rollback capability
5. **Verify**: Health checks and smoke tests
6. **Monitor**: Metrics and alerting activation

### 8.3 Rollback Strategy
- **Immediate**: Docker service rollback
- **Database**: Migration rollback scripts
- **Configuration**: Version-controlled configs
- **DNS**: Fast rollback via DNS switch

## 9. Capacity Planning

### 9.1 Current Capacity
- **Concurrent Users**: 100 (estimated)
- **Tasks per Hour**: 1,000 (estimated)
- **Memory Usage**: 32GB baseline, 64GB peak
- **Storage**: 100GB initial, 1TB/year growth

### 9.2 Scaling Triggers
- **CPU**: > 70% sustained for 5 minutes
- **Memory**: > 80% sustained for 5 minutes
- **Disk**: > 85% usage
- **Network**: > 80% bandwidth utilization

### 9.3 Scaling Strategy
- **Vertical**: Increase container resources
- **Horizontal**: Add more Ganglion nodes
- **Database**: Read replicas, connection pooling
- **Caching**: Redis cluster mode

## 10. Compliance & Governance

### 10.1 Security Standards
- **OWASP**: Top 10 compliance
- **CIS**: Container security benchmarks
- **NIST**: Cybersecurity framework
- **GDPR**: Data protection requirements

### 10.2 Audit Requirements
- **Access Logs**: All administrative access
- **Change Logs**: Configuration changes
- **Security Logs**: Failed authentication attempts
- **Compliance Reports**: Monthly security reports

### 10.3 Documentation Standards
- **Architecture**: Current state documentation
- **Procedures**: Operational runbooks
- **Incident Response**: Playbooks and escalation
- **Knowledge Base**: Troubleshooting guides

This architecture provides a robust, scalable, and secure hosting environment for the Longin EGO System with full support for distributed cognitive operations and autonomous software development workflows.