# Zero-Downtime Deployment Architecture

## Overview

This document describes the refactored CI/CD pipeline that fixes critical production issues:

1. **Eliminates Hard Downtime** - Blue-green/rolling updates with health checks
2. **Enforces Immutability** - Production server has no git/source code access
3. **Stabilizes Docker Build** - Proper DinD service configuration
4. **Adds Quality Gates** - Linting, unit tests, and security scanning before builds

## Architecture

### CI Pipeline (Drone)

```
┌─────────────────────────────────────────────────────────────────┐
│ DRONE CI SERVER                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. check-changes: Skip if no changes in component              │
│ 2. lint: Black, isort, flake8 for Python; ESLint for TypeScript│
│ 3. unit-tests: pytest for Python components                    │
│ 4. build-push: Build and push tagged images to registry         │
│ 5. scan-vulnerabilities: Trivy scan for HIGH/CRITICAL issues    │
│ 6. deploy-webhook: Trigger production deployment via webhook    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    Webhook Signature (HMAC-SHA256)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ PRODUCTION SERVER (Docker Swarm)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ Deploy Webhook Handler Service (Python Flask)                   │
│  • Listens on port 5000                                         │
│  • Verifies webhook signature                                   │
│  • Pulls images from registry (authenticated)                   │
│  • Updates services with rolling deployment                     │
│  • Monitors health checks                                       │
│  • NO SSH access, NO git, NO source code                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Improvements

#### 1. Quality Gates (Before Build)

**Linting:**
- Python: black, isort, flake8
- TypeScript: eslint

**Testing:**
- Unit tests with coverage reports
- Immediate failure on test errors

**Security:**
- Trivy scanning for HIGH/CRITICAL vulnerabilities
- Prevents deployment if vulnerabilities found

#### 2. Zero-Downtime Deployment

**Rolling Updates:**
```yaml
docker service update \
  --image new-image:tag \
  --update-order start-first \     # Start new before stopping old
  --update-delay 2s \              # Wait 2s between container updates
  --update-parallelism 1           # Update 1 container at a time
  service-name
```

**Health Checks:**
- Waits up to 30 retries (60 seconds) for tasks to reach Running state
- Monitors `docker service ps` output
- Automatically rolls back on timeout (Docker Swarm feature)

#### 3. Production Server Security

**What's NOT on production:**
- ❌ Git repository (.git folder)
- ❌ Source code
- ❌ SSH keys to repository
- ❌ SSH access for CI/CD deployments
- ❌ Drone CI credentials

**What's on production:**
- ✅ Docker images in registry (pulled on demand)
- ✅ Deployment webhook handler service
- ✅ Docker credentials for registry only
- ✅ Webhook signature verification
- ✅ Webhook secrets (HMAC verification)

## Setup Instructions

### 1. Add Drone CI Secrets

In Drone CI repository settings, add these secrets:

```
docker_username        = your-docker-registry-username
docker_password        = your-docker-registry-password
deploy_webhook_backend_prod        = https://prod-server.com:8443/deploy/webhook
deploy_webhook_frontend_prod       = https://prod-server.com:8443/deploy/webhook
deploy_webhook_bot_prod            = https://prod-server.com:8443/deploy/webhook
deploy_webhook_full_prod           = https://prod-server.com:8443/deploy/webhook
deploy_webhook_backend_dev         = https://dev-server.com:8443/deploy/webhook
deploy_webhook_frontend_dev        = https://dev-server.com:8443/deploy/webhook
deploy_webhook_bot_dev             = https://dev-server.com:8443/deploy/webhook
deploy_webhook_full_dev            = https://dev-server.com:8443/deploy/webhook
```

### 2. Production Server Setup

#### Step 1: Install Python dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip curl
pip3 install flask
```

#### Step 2: Create deployment user and directories

```bash
sudo mkdir -p /opt/subsora/scripts
sudo cp scripts/deploy-webhook-handler.py /opt/subsora/scripts/
sudo cp scripts/.deploy.env.example /opt/subsora/.deploy.env
```

#### Step 3: Configure deployment environment

```bash
sudo vim /opt/subsora/.deploy.env
# Edit with:
# - WEBHOOK_SECRET (generate: openssl rand -hex 32)
# - REGISTRY_USERNAME and REGISTRY_PASSWORD
# - DOCKER_STACK_NAME (should be "subsora")
```

#### Step 4: Setup systemd service

```bash
sudo cp scripts/subsora-deploy.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable subsora-deploy
sudo systemctl start subsora-deploy
```

#### Step 5: Verify service

```bash
sudo systemctl status subsora-deploy
# Should show: active (running)

# Test health endpoint
curl http://localhost:5000/health
# Response: {"status": "healthy"}
```

### 3. Nginx Reverse Proxy Configuration

Configure nginx on production to forward webhooks to the handler:

```nginx
server {
    listen 8443 ssl;
    server_name prod-server.com;
    
    ssl_certificate /etc/ssl/certs/prod-cert.crt;
    ssl_certificate_key /etc/ssl/private/prod-key.key;
    
    location /deploy/webhook {
        proxy_pass http://localhost:5000;
        proxy_set_header X-Webhook-Signature $http_x_webhook_signature;
        proxy_set_header Content-Type application/json;
        
        # Timeout for long deployments
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

### 4. Test Deployment

```bash
# Generate webhook signature
SECRET="your-webhook-secret"
PAYLOAD='{"type":"service","image":"cicd.zerity.ru:55000/subsora/backend:test123"}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')

# Send test webhook
curl -X POST https://prod-server.com:8443/deploy/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Signature: $SIGNATURE" \
  -d "$PAYLOAD"
```

## Monitoring & Logging

### View deployment logs

```bash
# Real-time logs
sudo journalctl -u subsora-deploy -f

# Recent logs (last 100 lines)
sudo journalctl -u subsora-deploy -n 100

# Service restart count
sudo systemctl status subsora-deploy
```

### Monitor service health

```bash
# Check service status
docker service ps subsora_backend

# View service logs
docker service logs subsora_backend -f

# Get detailed service info
docker service inspect subsora_backend
```

## Migration from Old Pipeline

### Before pushing to production:

1. **Update Drone secrets** with new webhook URLs
2. **Setup production server** with deployment handler
3. **Test in dev environment** first (deploy-webhook-handler-dev)
4. **Verify zero-downtime** deployment works
5. **Enable new pipeline** for main branch

### Rollback procedure

If issues arise:

```bash
# Rollback to previous image version
docker service update \
  --image cicd.zerity.ru:55000/subsora/backend:previous-tag \
  --update-order start-first \
  subsora_backend

# Wait for rollback to complete
watch docker service ps subsora_backend
```

## Troubleshooting

### Webhook not triggering

```bash
# Check if handler is running
sudo systemctl status subsora-deploy

# Check if listening on port 5000
sudo ss -tlnp | grep 5000

# Check iptables/firewall
sudo ufw status
sudo ufw allow 8443
```

### Deployment stuck in updating

```bash
# Check service status
docker service ps subsora_backend

# If stuck, force update with same image
docker service update --force subsora_backend
```

### Docker login failures

```bash
# Verify credentials in .deploy.env
cat /opt/subsora/.deploy.env

# Test credentials manually
docker login cicd.zerity.ru:55000 -u username -p password
```

## Security Considerations

1. **Webhook Secret**: Use strong secret, rotate periodically
   - Generate: `openssl rand -hex 32`
   
2. **HTTPS Only**: Always use HTTPS for webhook URLs
   - Use self-signed cert or Let's Encrypt
   
3. **Rate Limiting**: Add rate limiting at nginx level
   
4. **Audit Logging**: Enable Docker audit logging for service updates
   
5. **Least Privilege**: Run handler as non-root if possible

## Future Improvements

- [ ] Add metrics/Prometheus export
- [ ] Slack notifications on deployment start/completion
- [ ] Database backups before full redeploy
- [ ] Canary deployments (1 task at a time with traffic switching)
- [ ] Automated rollback on health check failures
- [ ] Deployment history/audit log
