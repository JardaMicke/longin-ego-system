# Produkční nasazení

## Nasazení

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_prod.ps1
```

## Doména

DNS:

- A záznam pro longinegosystem.eu na IP produkčního serveru
- A záznam pro www.longinegosystem.eu na IP produkčního serveru

Reverse proxy:

- Caddy obsluhuje www.longinegosystem.eu a přesměrovává longinegosystem.eu na www

## CI/CD

GitHub Secrets:

- PROD_SSH_HOST
- PROD_SSH_USER
- PROD_SSH_KEY
- PROD_SSH_PORT
- PROD_DEPLOY_PATH

## Ověření dostupnosti

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_prod.ps1
```

## Přepnutí cíle

Proměnné prostředí:

- LONGIN_API_BASE (výchozí http://localhost:8000)
- LONGIN_UI_BASE (výchozí http://localhost:3000)
