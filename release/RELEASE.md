# Release artefakty

## Docker image build

### Ganglion API

```bash
docker build -f docker/Dockerfile.ganglion -t longin-ego/ganglion:latest .
```

### Cortex UI

```bash
docker build -f docker/Dockerfile.cortex -t longin-ego/cortex:latest .
```

## Release compose

```bash
docker compose -f docker-compose.release.yml up -d
```

## Artefakty

- docker/Dockerfile.ganglion
- docker/Dockerfile.cortex
- docker-compose.release.yml
- requirements.txt
- release/PRODUCTION.md
- scripts/deploy_prod.ps1
- scripts/check_prod.ps1
