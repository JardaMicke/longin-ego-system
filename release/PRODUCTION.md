# Produkční nasazení

## Nasazení

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_prod.ps1
```

## Ověření dostupnosti

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_prod.ps1
```

## Přepnutí cíle

Proměnné prostředí:

- LONGIN_API_BASE (výchozí http://localhost:8000)
- LONGIN_UI_BASE (výchozí http://localhost:3000)
