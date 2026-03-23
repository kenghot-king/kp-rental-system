# KP Rental System — Production Deployment Guide

> Target: Ubuntu Server (LAN), Docker, 5 users
> Access: `http://server-ip:8071`

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Ubuntu | 22.04 or 24.04 LTS |
| Docker | 24+ |
| Docker Compose | v2 (included with Docker) |
| CPU | 2 cores minimum |
| RAM | 4 GB minimum |
| Disk | 50 GB SSD |

---

## 1. Install Docker

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in for group change to take effect
```

## 2. Clone Repository

```bash
git clone https://github.com/kenghot-king/kp-rental-system.git
cd kp-rental-system
```

## 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

Set a strong database password:

```
POSTGRES_PASSWORD=your-strong-password-here
```

## 4. Start Services

```bash
docker compose -f docker-compose.prod.yml up -d
```

Verify services are running:

```bash
docker compose -f docker-compose.prod.yml ps
```

## 5. Initialize Database

1. Open browser: `http://server-ip:8071`
2. Odoo will show the database creation page
3. Create database named **production**
4. Set master password, admin email, and admin password
5. Go to **Settings > Companies** > edit company > set **Country** to **Thailand** > Save
6. Install the **ggg_rental** module from Apps

## 6. Post-Install Configuration

After installing `ggg_rental`, configure the following manually:

### Taxes (Invoicing > Configuration > Taxes)

Create two taxes:

| Name | Type | Amount | Price Include | Tax Group | Account |
|------|------|--------|--------------|-----------|---------|
| Output 7% include | Sale | 7% | Tax Included | VAT 7% | 213200 Output VAT |
| Input 7% include | Purchase | 7% | Tax Included | VAT 7% | 114200 Input VAT |

### Rental Settings (Rental > Configuration > Settings)

- Set **Rental Location** (auto-created on first use)
- Configure **Default Delay Costs** if needed
- **Auto Refund Deposit** is enabled by default

## 7. Set Up Backups

```bash
sudo crontab -e
```

Add the following line (runs daily at 2 AM):

```
0 2 * * * /path/to/kp-rental-system/scripts/backup.sh
```

Create backup directory:

```bash
sudo mkdir -p /backups/odoo
```

### Manual Backup

```bash
./scripts/backup.sh
```

### Restore from Backup

```bash
# Stop Odoo
docker compose -f docker-compose.prod.yml stop odoo

# Restore database
gunzip < /backups/odoo/db_YYYY-MM-DD.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db \
  psql -U odoo -d production

# Restore filestore
docker compose -f docker-compose.prod.yml exec -T odoo \
  tar xzf - -C / < /backups/odoo/filestore_YYYY-MM-DD.tar.gz

# Start Odoo
docker compose -f docker-compose.prod.yml start odoo
```

---

## Updating the Application

When new code is pushed to the repository:

```bash
cd /path/to/kp-rental-system

# Pull latest code
git pull

# Restart Odoo (picks up code changes)
docker compose -f docker-compose.prod.yml restart odoo
```

If module upgrade is needed (new fields, views, etc.):

1. Go to `http://server-ip:8071`
2. Activate developer mode: Settings > General Settings > Developer Tools > Activate
3. Go to Apps, find **ggg_rental**, click Upgrade

Or via command line:

```bash
docker compose -f docker-compose.prod.yml exec odoo \
  odoo --addons-path=/mnt/extra-addons/custom \
  --db_host=db --db_user=odoo --db_password=$POSTGRES_PASSWORD \
  -d production -u ggg_rental --stop-after-init
```

---

## Troubleshooting

### View Logs

```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Odoo only
docker compose -f docker-compose.prod.yml logs -f odoo

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 odoo
```

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.prod.yml restart

# Restart Odoo only
docker compose -f docker-compose.prod.yml restart odoo
```

### Full Reset (caution: destroys data)

```bash
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d
```

---

## Architecture

```
 LAN Users
     │
     ▼
┌──────────────────────────────────┐
│  Ubuntu Server                   │
│                                  │
│  ┌────────────────────────────┐  │
│  │     Docker Compose         │  │
│  │                            │  │
│  │  ┌──────────────────────┐  │  │
│  │  │    Odoo 19 CE        │  │  │
│  │  │    :8071 → :8069     │  │  │
│  │  │    workers=2         │  │  │
│  │  └──────────┬───────────┘  │  │
│  │             │              │  │
│  │  ┌──────────▼───────────┐  │  │
│  │  │   PostgreSQL 16      │  │  │
│  │  └─────────────────────┘  │  │
│  │                            │  │
│  │  Volumes:                  │  │
│  │   pgdata    (database)    │  │
│  │   odoo-data (filestore)   │  │
│  └────────────────────────────┘  │
│                                  │
│  Cron: daily backup at 2 AM     │
└──────────────────────────────────┘
```
