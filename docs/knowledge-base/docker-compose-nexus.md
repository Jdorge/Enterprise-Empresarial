# docker-compose.yml - NEXUS PRODUCTION READY

```yaml
version: '3.9'

services:
  # ==================== POSTGRES ====================
  postgres:
    image: postgres:16-alpine
    container_name: n8n-postgres
    environment:
      POSTGRES_DB: n8n
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${DB_PASSWORD:-SecureN8nPass2025!}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "n8n"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nexus-network
    restart: unless-stopped

  # ==================== REDIS ====================
  redis:
    image: redis:7-alpine
    container_name: n8n-redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-RedisN8n2025!}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - nexus-network
    restart: unless-stopped

  # ==================== N8N ====================
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n-app
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=${DB_PASSWORD:-SecureN8nPass2025!}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD:-RedisN8n2025!}
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_TUNNEL_URL=${WEBHOOK_TUNNEL_URL:-http://localhost:5678}
      - GENERIC_TIMEZONE=${GENERIC_TIMEZONE:-America/Sao_Paulo}
      - NODE_ENV=production
      - LOG_LEVEL=info
    volumes:
      - n8n_data:/home/node/.n8n
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5678/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - nexus-network
    restart: unless-stopped

  # ==================== PROMETHEUS ====================
  prometheus:
    image: prom/prometheus:latest
    container_name: n8n-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./infrastructure/monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./infrastructure/monitoring/prometheus/prometheus-rules.yml:/etc/prometheus/prometheus-rules.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    networks:
      - nexus-network
    restart: unless-stopped
    depends_on:
      - n8n

  # ==================== GRAFANA ====================
  grafana:
    image: grafana/grafana:latest
    container_name: n8n-grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_USERS_ALLOW_SIGN_UP: 'false'
      GF_SERVER_ROOT_URL: http://localhost:3000
      GF_INSTALL_PLUGINS: grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./infrastructure/monitoring/grafana/grafana-provisioning.yml:/etc/grafana/provisioning/dashboards/provisioning.yml:ro
      - ./infrastructure/monitoring/grafana/grafana-datasource-prometheus.yml:/etc/grafana/provisioning/datasources/prometheus.yml:ro
      - ./infrastructure/monitoring/grafana/grafana-dashboard-nexus.json:/var/lib/grafana/dashboards/nexus.json:ro
    networks:
      - nexus-network
    restart: unless-stopped
    depends_on:
      - prometheus

  # ==================== ALERTMANAGER ====================
  alertmanager:
    image: prom/alertmanager:latest
    container_name: n8n-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./infrastructure/monitoring/alerting/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    networks:
      - nexus-network
    restart: unless-stopped

networks:
  nexus-network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  n8n_data:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  alertmanager_data:
    driver: local
```

## 🚀 COMO USAR

```bash
# 1. Copiar e colar em n8n-workflows-enterprise/docker-compose.yml

# 2. Criar arquivo .env
cat > .env << EOF
DB_PASSWORD=SecureN8nPass2025!
REDIS_PASSWORD=RedisN8n2025!
GRAFANA_PASSWORD=admin
N8N_HOST=localhost
WEBHOOK_TUNNEL_URL=http://localhost:5678
GENERIC_TIMEZONE=America/Sao_Paulo
EOF

# 3. Subir todos os serviços
docker-compose up -d

# 4. Verificar status
docker-compose ps

# 5. Ver logs
docker-compose logs -f n8n

# 6. Acessar
# n8n: http://localhost:5678
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000
# AlertManager: http://localhost:9093
```

## ✅ VALIDAÇÃO DE SAÚDE

```bash
# Verificar n8n
curl -s http://localhost:5678/health | jq

# Verificar Prometheus
curl -s http://localhost:9090/-/healthy

# Verificar Grafana
curl -s http://localhost:3000/api/health | jq

# Verificar PostgreSQL
docker-compose exec postgres pg_isready -U n8n

# Verificar Redis
docker-compose exec redis redis-cli ping
```

## 🛑 PARA TUDO

```bash
docker-compose down -v  # Remove todos os volumes
```
