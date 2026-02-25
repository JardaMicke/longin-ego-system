
# Deployment Guide: LONGIN EGO System na <www.longinegesystem.eu>

Tento dokument popisuje postup nasazení systému LONGIN EGO na produkční server s doménou `www.longinegesystem.eu` registrovanou u Webglobe.

## 1. Příprava Serveru (VPS)

Systém vyžaduje server s podporou Docker a ideálně GPU (pokud běží Kernel na serveru). Pokud Kernel běží lokálně (Hybrid mode), server slouží jen pro Cortex (Frontend) a API Proxy.

**Doporučená konfigurace VPS:**

- **OS:** Ubuntu 22.04 LTS
- **CPU:** 4+ vCPU
- **RAM:** 8GB+ (32GB+ pro plný AI běh)
- **Disk:** 100GB+ SSD/NVMe
- **GPU:** NVIDIA (pro plný běh), jinak volitelné

### Instalace prerekvizit

Připojte se k serveru přes SSH:

```bash
ssh root@<VAŠE_IP_ADRESA_VPS>
```

Aktualizace a instalace Dockeru:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git apt-transport-https ca-certificates software-properties-common
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

Instalace NVIDIA Container Toolkit (pouze pokud máte GPU):

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-docker2
sudo systemctl restart docker
```

## 2. Nastavení DNS u Webglobe

1. Přihlaste se do administrace Webglobe (<https://admin.webglobe.cz/>).
2. Přejděte do správy domén a vyberte `longinegesystem.eu`.
3. Otevřete **DNS Záznamy**.
4. Zjistěte IP adresu vašeho serveru (VPS):
   - **Kde ji najdu?** IP adresu naleznete v e-mailu o zřízení služby od Webglobe nebo v zákaznické administraci v sekci VPS / Servery -> Detail služby.
   - Bude ve formátu např.: `89.123.45.67`.

5. Vytvořte/Upravte následující **A záznamy** (místo `<VAŠE_IP_ADRESA_VPS>` doplňte skutečnou IP adresu vašeho serveru):

| Typ | Název (Host) | Hodnota (Cíl) | TTL |
|---|---|---|---|
| A | @ | <VAŠE_IP_ADRESA_VPS> | 600 |
| A | www | <VAŠE_IP_ADRESA_VPS> | 600 |
| A | api | <VAŠE_IP_ADRESA_VPS> | 600 |

*Poznámka: Propagace DNS změn může trvat až 24 hodin, obvykle je to ale do hodiny.*

## 3. Nasazení Aplikace

Na serveru naklonujte repozitář nebo nahrajte soubory:

```bash
mkdir -p /opt/longin-ego
# Zde nahrajte obsah složky projektu (např. přes SCP nebo Git)
cd /opt/longin-ego
```

### Konfigurace prostředí

Vytvořte soubor `.env.prod`:

```bash
POSTGRES_USER=longin_master
POSTGRES_PASSWORD=<SILNE_HESLO_DB>
POSTGRES_DB=longin_memory
JWT_SECRET=<VYGENERUJTE_DLOUHY_SECRET_KOD>
REDIS_PASSWORD=<SILNE_HESLO_REDIS>
DOMAIN=longinegesystem.eu
EMAIL=admin@longinegesystem.eu
```

### Spuštění přes Docker Compose

```bash
# Sestavení a spuštění kontejnerů na pozadí
docker compose -f deployment/docker-compose.prod.yml up -d --build
```

## 4. Nastavení SSL (HTTPS)

Při prvním spuštění je potřeba získat SSL certifikát od Let's Encrypt. Nginx kontejner bude zpočátku selhávat, protože chybí certifikáty.

1. Spusťte dočasný certbot příkaz:

```bash
docker compose -f deployment/docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d longinegesystem.eu -d www.longinegesystem.eu
```

1. Restartujte Nginx pro načtení certifikátů:

```bash
docker compose -f deployment/docker-compose.prod.yml restart nginx
```

## 5. Ověření Funkčnosti

- Otevřete prohlížeč a jděte na `https://www.longinegesystem.eu`
- Měli byste vidět přihlašovací obrazovku Cortexu.
- API je dostupné na `https://www.longinegesystem.eu/api/docs` (Swagger UI).
- Metriky (pokud jsou povoleny) na `https://www.longinegesystem.eu/grafana`.

## 6. Hybridní Režim (Volitelné)

Pokud nemáte GPU server a chcete, aby "mozek" běžel u vás doma, ale web byl veřejný:

1. Na VPS spusťte pouze Nginx a Frontend.
2. Nastavte VPN (WireGuard/Tailscale) mezi VPS a vaším domácím PC.
3. V Nginx konfiguraci na VPS přesměrujte `/api/` na IP adresu vašeho domácího PC ve VPN tunelu.

Tím získáte veřejnou doménu s výkonem domácího hardware.
