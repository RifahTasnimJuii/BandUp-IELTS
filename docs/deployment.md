# Production deployment guide

This project is designed to run as a Docker Compose deployment with a reverse proxy, Django backend, Next.js frontend, PostgreSQL, Redis, and Celery workers.

## 1. Server prerequisites

On Ubuntu 22.04 or newer:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin git nginx certbot python3-certbot-nginx
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in, or run:

```bash
newgrp docker
```

## 2. Clone and configure

```bash
git clone <your-repository-url>
cd BandUp-IELTS
cp .env.prod.example .env.prod
```

Update `.env.prod` with your real values:

- `DJANGO_SECRET_KEY`
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `OPENAI_API_KEY`
- `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_WS_URL`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`

Example:

```env
DJANGO_SECRET_KEY=very-long-random-secret
POSTGRES_DB=bandup_db
POSTGRES_USER=bandup_user
POSTGRES_PASSWORD=change-this-password
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOWED_ORIGINS=https://your-domain.com
NEXT_PUBLIC_API_URL=https://your-domain.com/api
NEXT_PUBLIC_WS_URL=wss://your-domain.com/ws
```

## 3. Build and start production containers

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

Check status:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod ps
```

View logs:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod logs -f backend frontend nginx
```

## 4. Run database migrations

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend python manage.py migrate
```

Create an admin user:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend python manage.py createsuperuser
```

Collect static files if needed:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend python manage.py collectstatic --noinput
```

## 5. Health checks

The stack includes health checks for PostgreSQL, Redis, backend, and frontend.

Check the backend health endpoint:

```bash
curl http://localhost/api/health/
```

## 6. SSL / HTTPS with Let's Encrypt

Recommended for VPS deployments behind a public domain.

Install Certbot and request a certificate:

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Then verify automatic renewal:

```bash
sudo certbot renew --dry-run
```

If you are using Nginx as a TLS terminator, point your domain to the server and update the Nginx config to listen on 443 with the generated certificate files.

## 7. Useful production commands

Restart all services:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod restart
```

Stop everything:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod down
```

Remove volumes (destructive):

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod down -v
```

## 8. Recommended VPS checklist

- Use a non-root user with Docker access
- Configure firewall rules for ports 22, 80, and 443
- Keep `.env.prod` outside the repository if possible
- Store backups of PostgreSQL data and media files
- Monitor logs and uptime with a service like Uptime Kuma or Datadog
- Set up automatic SSL renewal

## 9. Production notes

- The Django app runs behind Gunicorn.
- The frontend is served by a standalone Next.js production server.
- Nginx terminates incoming requests and proxies backend/frontend traffic.
- Static files and media are stored in Docker volumes and are served by Nginx.
