
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
4. Zjistěte **Veřejnou IPv4 adresu** vašeho stroje (Host):

   **A) Pokud máte VPS (např. u Webglobe):**
   - IP adresu naleznete v **e-mailu o zřízení služby** nebo v **administraci hostingu** (sekce VPS/Servery -> Detail).
   - *Důležité:* Docker kontejner nemá vlastní veřejnou IP. Pro doménu se používá IP adresa celého serveru (VPS), na kterém Docker běží.

   **B) Pokud hostujete doma (na vlastním PC/Serveru):**
   - Pokud jste již připojeni k terminálu, zjistíte ji příkazem:

     ```bash
     curl ifconfig.me
     ```

   - Nebo otevřete v prohlížeči stránku [whatismyip.com](https://www.whatismyip.com/).
   - *Pozor:* Pro domácí hosting musíte mít od poskytovatele internetu přidělenou **veřejnou IP adresu** a na routeru nastavené přesměrování portů (Port Forwarding) 80 a 443 na váš počítač.

5. Vytvořte/Upravte následující **A záznamy** (místo `<VAŠE_IP_ADRESA_VPS>` doplňte zjištěnou veřejnou IP):

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

## 4. Nastavení SSL (HTTPS) - Let's Encrypt (Certbot)

Pro zabezpečení komunikace (HTTPS) využijeme **Let's Encrypt**, který poskytuje důvěryhodné certifikáty zdarma. Pro validaci a instalaci použijeme nástroj **Certbot** v Dockeru, který je již předpřipraven v konfiguraci.

### Proč Let's Encrypt?

- **Zdarma:** Žádné poplatky za vydání ani obnovu.
- **Automatizované:** Certbot se stará o validaci a obnovu.
- **Důvěryhodné:** Podporováno všemi moderními prohlížeči.
- **Bezpečné:** Moderní šifrování.

### Postup instalace certifikátů

1. **Ověřte DNS a Porty:**
    - Ujistěte se, že doména `longinegesystem.eu` (A záznam) správně směřuje na IP adresu vašeho serveru.
    - Ujistěte se, že na firewallu serveru (nebo u poskytovatele VPS) jsou otevřené porty **80** (HTTP) a **443** (HTTPS).

2. **Spusťte Certbot (Dry Run - Test):**
    Nejprve zkuste "testovací" běh, abyste se ujistili, že vše funguje, aniž byste vyčerpali limity Let's Encrypt.

    ```bash
    docker compose -f deployment/docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot --dry-run -d longinegesystem.eu -d www.longinegesystem.eu
    ```

    Pokud tento příkaz skončí úspěšně ("The dry run was successful"), pokračujte.

3. **Vygenerujte ostrý certifikát:**

    ```bash
    docker compose -f deployment/docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot --email admin@longinegesystem.eu --agree-tos --no-eff-email -d longinegesystem.eu -d www.longinegesystem.eu
    ```

    - Tento příkaz vygeneruje soubory `fullchain.pem` a `privkey.pem` do složky `./certbot/conf/live/longinegesystem.eu/`.

4. **Restartujte Nginx:**
    Nginx nyní potřebuje načíst nově vytvořené certifikáty.

    ```bash
    docker compose -f deployment/docker-compose.prod.yml restart nginx
    ```

### Automatická obnova (Auto-Renewal)

Certifikáty Let's Encrypt platí 90 dní. Náš Docker setup již obsahuje kontejner `certbot`, který běží na pozadí a každých 12 hodin kontroluje, zda je potřeba certifikát obnovit.

- **Jak to funguje:** Kontejner `certbot` periodicky spouští `certbot renew`. Pokud je certifikát blízko expirace (méně než 30 dní), automaticky se obnoví.
- **Reload Nginx:** Po obnově je třeba, aby Nginx načetl nový certifikát. To je v produkčním prostředí řešeno sdíleným volume nebo restart scriptem. Pro jednoduchost můžete nastavit cron job na hostitelském systému:

  ```bash
  # Otevřít crontab
  crontab -e
  
  # Přidat řádek (restartuje Nginx každé pondělí ve 3:00 ráno pro načtení případných nových certifikátů)
  0 3 * * 1 docker compose -f /opt/longin-ego/deployment/docker-compose.prod.yml restart nginx
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
