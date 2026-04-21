# KP Rental System — UAT Environment Server Specification

> **Purpose**: Tencent Cloud server provisioning request for UAT (User Acceptance Testing)
> **Project**: KP Rental System (Odoo 19 CE + Custom Modules)
> **Date**: 2026-04-21

---

## 1. Project Overview

| Item | Detail |
|------|--------|
| Application | Odoo 19 Community Edition |
| Custom Modules | `ggg_rental` (Rental Management), `ggg_gantt` (Gantt View) |
| Deployment | Docker Compose (Odoo 19 + PostgreSQL 16) |
| Expected UAT Users | 5–10 concurrent users |
| Environment Purpose | User Acceptance Testing before production go-live |

---

## 2. Recommended Server Specification

### 2.1 CVM (Cloud Virtual Machine)

| Specification | Recommended | Minimum |
|--------------|-------------|---------|
| **Instance Type** | S5.MEDIUM8 or equivalent | S5.MEDIUM4 |
| **vCPU** | 4 cores | 2 cores |
| **RAM** | 8 GB | 4 GB |
| **OS** | Ubuntu 22.04 LTS (or 24.04 LTS) | Ubuntu 22.04 LTS |
| **Region** | Bangkok (ap-bangkok) or Hong Kong (ap-hongkong) | — |
| **Availability Zone** | Single AZ (UAT only) | — |

> [!NOTE]
> 4 vCPU / 8 GB is recommended for Odoo 19 with 2 workers + PostgreSQL running on the same instance. This provides headroom for UAT testing with multiple concurrent users and background cron jobs.

### 2.2 Storage (Cloud Block Storage - CBS)

| Specification | Recommended | Minimum |
|--------------|-------------|---------|
| **System Disk** | 50 GB SSD (Premium Cloud SSD) | 40 GB SSD |
| **Data Disk** | 100 GB SSD (Premium Cloud SSD) | 50 GB SSD |
| **IOPS** | ≥ 3,000 | ≥ 1,800 |
| **Throughput** | ≥ 150 MB/s | ≥ 100 MB/s |

> [!IMPORTANT]
> The data disk is for PostgreSQL data (`pgdata`) and Odoo filestore (`odoo-data`). SSD is mandatory for acceptable database performance. Mount the data disk separately at `/data`.

### 2.3 Network

| Specification | Detail |
|--------------|--------|
| **VPC** | Create dedicated VPC for UAT |
| **Bandwidth** | 10 Mbps (Bill-by-Traffic or Bandwidth Package) |
| **Elastic IP (EIP)** | 1x Static Public IP |
| **Security Group** | See Section 3 below |
| **DNS** | Optional: subdomain e.g. `uat-rental.yourcompany.com` |

---

## 3. Security Group Rules

### Inbound Rules

| Priority | Protocol | Port | Source | Description |
|----------|----------|------|--------|-------------|
| 1 | TCP | 22 | Office IP / VPN CIDR | SSH Access |
| 2 | TCP | 80 | 0.0.0.0/0 | HTTP (Nginx reverse proxy) |
| 3 | TCP | 443 | 0.0.0.0/0 | HTTPS (Nginx reverse proxy) |
| 4 | TCP | 8069 | Office IP / VPN CIDR | Odoo Direct (dev/debug only) |
| 100 | ALL | ALL | 0.0.0.0/0 | **DENY** — Default deny all |

### Outbound Rules

| Priority | Protocol | Port | Destination | Description |
|----------|----------|------|-------------|-------------|
| 1 | TCP | 80, 443 | 0.0.0.0/0 | OS updates, Docker Hub pulls |
| 2 | TCP | 587 | SMTP Server | Email notifications (optional) |
| 100 | ALL | ALL | 0.0.0.0/0 | Allow all outbound |

> [!WARNING]
> **Never expose PostgreSQL port (5432) to the public internet.** The database is only accessible within Docker's internal network.

---

## 4. Software Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Ubuntu | 22.04 or 24.04 LTS | Operating system |
| Docker Engine | 24+ | Container runtime |
| Docker Compose | v2 (bundled) | Service orchestration |
| Odoo | 19.0 (Official Docker image) | Application server |
| PostgreSQL | 16 (Official Docker image) | Database |
| Nginx | Latest | Reverse proxy + SSL termination |
| Certbot / Let's Encrypt | Latest | SSL certificate (if public domain) |

---

## 5. Deployment Architecture (UAT)

```
                    Internet
                       │
                       ▼
              ┌────────────────┐
              │  Tencent Cloud  │
              │  EIP (Public)   │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │  Security Group │
              │  (Firewall)     │
              └───────┬────────┘
                      │
┌─────────────────────▼─────────────────────────┐
│  CVM Instance (S5.MEDIUM8)                    │
│  Ubuntu 22.04 LTS                             │
│  4 vCPU / 8 GB RAM                            │
│                                               │
│  ┌─────────────────────────────────────────┐  │
│  │  Nginx (Reverse Proxy)                  │  │
│  │  :80 / :443 → localhost:8069            │  │
│  └──────────────────┬──────────────────────┘  │
│                     │                         │
│  ┌──────────────────▼──────────────────────┐  │
│  │  Docker Compose                         │  │
│  │                                         │  │
│  │  ┌───────────────────────────────────┐  │  │
│  │  │  Odoo 19 CE        (Container)    │  │  │
│  │  │  Port: 8069                       │  │  │
│  │  │  Workers: 2                       │  │  │
│  │  │  Max Cron Threads: 1              │  │  │
│  │  │  Volumes:                         │  │  │
│  │  │   - ./addons → custom modules     │  │  │
│  │  │   - odoo-data → /var/lib/odoo     │  │  │
│  │  └──────────────┬────────────────────┘  │  │
│  │                 │                       │  │
│  │  ┌──────────────▼────────────────────┐  │  │
│  │  │  PostgreSQL 16    (Container)     │  │  │
│  │  │  Volume: pgdata → /data/pgdata    │  │  │
│  │  └───────────────────────────────────┘  │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  Storage:                                     │
│   /         50 GB SSD  (System)               │
│   /data    100 GB SSD  (PostgreSQL + Odoo)    │
│                                               │
│  Cron: Daily backup at 2 AM                   │
└───────────────────────────────────────────────┘
```

---

## 6. Backup Strategy (UAT)

| Item | Specification |
|------|---------------|
| **CVM Snapshot** | Weekly (automatic via Tencent Cloud CBS snapshot) |
| **Database Backup** | Daily at 02:00 via cron script (`scripts/backup.sh`) |
| **Backup Retention** | 7 days rolling (UAT) |
| **Backup Storage** | Local disk or Tencent Cloud COS bucket |

---

## 7. Estimated Monthly Cost (Tencent Cloud)

> Prices are approximate and vary by region. Based on **ap-bangkok** or **ap-hongkong** region, Pay-as-you-go pricing.

| Resource | Specification | Est. Monthly (USD) |
|----------|--------------|-------------------|
| CVM | S5.MEDIUM8 (4C/8G) | ~$50–70 |
| System Disk | 50 GB Premium SSD | ~$5 |
| Data Disk | 100 GB Premium SSD | ~$10 |
| EIP + Bandwidth | 10 Mbps (Bill-by-Traffic) | ~$10–20 |
| CBS Snapshot | Weekly snapshots | ~$3–5 |
| **Total** | | **~$78–110 /month** |

> [!TIP]
> For cost savings, consider **Reserved Instance** pricing or **Spot Instance** if the UAT environment doesn't need 24/7 uptime. You can also schedule the CVM to shut down during non-business hours.

---

## 8. Provisioning Checklist

- [ ] Create Tencent Cloud account / project
- [ ] Set up VPC and subnet
- [ ] Create Security Group with rules (Section 3)
- [ ] Provision CVM instance (Section 2.1)
- [ ] Attach and mount data disk at `/data`
- [ ] Allocate Elastic IP (EIP) and bind to CVM
- [ ] Install Docker Engine + Docker Compose
- [ ] Install and configure Nginx reverse proxy
- [ ] Set up SSL certificate (Let's Encrypt / Tencent SSL)
- [ ] Clone repository and deploy (`docker-compose.prod.yml`)
- [ ] Initialize Odoo database
- [ ] Configure firewall / security group
- [ ] Set up automated backups
- [ ] Share UAT URL and credentials with test team
- [ ] (Optional) Configure domain DNS pointing to EIP

---

## 9. Access Information (To Fill After Provisioning)

| Item | Value |
|------|-------|
| CVM Public IP | ___________________ |
| UAT URL | `https://uat-rental.yourcompany.com` |
| SSH User | `ubuntu` |
| SSH Key | ___________________ |
| Odoo Admin Email | ___________________ |
| Odoo Admin Password | ___________________ |
| Database Name | `uat` |
| PostgreSQL Password | ___________________ |

---

## 10. Comparison: UAT vs Production

| Aspect | UAT (This Request) | Production (Future) |
|--------|--------------------|--------------------|
| CVM | 4C / 8G (single) | 4C / 16G or 8C / 16G |
| Database | Same CVM (Docker) | Separate TencentDB for PostgreSQL |
| Workers | 2 | 4–6 |
| Storage | 100 GB SSD | 200+ GB SSD |
| Backup | Daily + Weekly snapshot | Real-time replica + Daily + COS archival |
| HA | Single instance | Multi-AZ / Load Balance |
| SSL | Let's Encrypt | Tencent Cloud SSL Certificate |
| Monitoring | Basic Cloud Monitor | Cloud Monitor + Custom alerts |
| Est. Cost | ~$80–110/mo | ~$200–400/mo |

---

> **Note to Provider**: This specification is for a **UAT/testing environment**. Production will require a separate, higher-spec deployment with managed database services and high availability. Please provision according to the UAT specifications above and confirm the instance details back.
