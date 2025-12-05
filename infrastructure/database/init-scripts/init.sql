-- ═══════════════════════════════════════════════════════════════════════════════
-- ENTERPRISE EMPRESARIAL v2.0.0 - DATABASE INITIALIZATION
-- ═══════════════════════════════════════════════════════════════════════════════
-- Este script inicializa todas as tabelas necessárias para o sistema.
-- Execute automaticamente via Docker ou manualmente com: psql -f init.sql
-- ═══════════════════════════════════════════════════════════════════════════════

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ═══════════════════════════════════════════════════════════════════════════════
-- SCHEMAS
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS leads;
CREATE SCHEMA IF NOT EXISTS operations;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS audit;

-- ═══════════════════════════════════════════════════════════════════════════════
-- CORE TABLES
-- ═══════════════════════════════════════════════════════════════════════════════

-- Usuários do sistema
CREATE TABLE IF NOT EXISTS core.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    department VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Configurações do sistema
CREATE TABLE IF NOT EXISTS core.settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    is_secret BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- LEADS TABLES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS leads.leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    company VARCHAR(255),
    position VARCHAR(100),
    source VARCHAR(50),
    score INTEGER DEFAULT 0,
    classification VARCHAR(20) DEFAULT 'cold',
    status VARCHAR(50) DEFAULT 'new',
    assigned_to UUID REFERENCES core.users(id),
    hubspot_contact_id VARCHAR(100),
    hubspot_deal_id VARCHAR(100),
    notion_page_id VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads.lead_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads.leads(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    description TEXT,
    performed_by UUID REFERENCES core.users(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- OPERATIONS TABLES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS operations.projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    owner_id UUID REFERENCES core.users(id),
    start_date DATE,
    end_date DATE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operations.tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    project_id UUID REFERENCES operations.projects(id),
    assignee_id UUID REFERENCES core.users(id),
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(50) DEFAULT 'pending',
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    sla_deadline TIMESTAMP,
    sla_breached BOOLEAN DEFAULT false,
    notion_page_id VARCHAR(100),
    tags TEXT[],
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- FINANCE TABLES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS finance.transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    external_id VARCHAR(100),
    type VARCHAR(20) NOT NULL, -- income, expense, transfer
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'BRL',
    category VARCHAR(50),
    description TEXT,
    reference VARCHAR(100),
    transaction_date DATE NOT NULL,
    tax_amount DECIMAL(15, 2) DEFAULT 0,
    tax_rate DECIMAL(5, 4) DEFAULT 0,
    notion_page_id VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finance.budgets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    spent DECIMAL(15, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- MONITORING TABLES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS monitoring.health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    latency_ms INTEGER,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monitoring.alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    severity VARCHAR(20) NOT NULL, -- info, warning, critical
    service VARCHAR(100),
    title VARCHAR(255) NOT NULL,
    message TEXT,
    status VARCHAR(20) DEFAULT 'active',
    acknowledged_by UUID REFERENCES core.users(id),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- AUDIT TABLES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS audit.request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(50),
    intent TEXT,
    source VARCHAR(50),
    priority VARCHAR(20),
    status VARCHAR(50),
    duration_ms INTEGER,
    error_message TEXT,
    client_ip VARCHAR(50),
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit.activity_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES core.users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ═══════════════════════════════════════════════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_leads_email ON leads.leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads.leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_classification ON leads.leads(classification);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads.leads(created_at);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON operations.tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON operations.tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON operations.tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON operations.tasks(due_date);

CREATE INDEX IF NOT EXISTS idx_transactions_type ON finance.transactions(type);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON finance.transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON finance.transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_health_checks_service ON monitoring.health_checks(service_name);
CREATE INDEX IF NOT EXISTS idx_health_checks_status ON monitoring.health_checks(status);
CREATE INDEX IF NOT EXISTS idx_health_checks_time ON monitoring.health_checks(checked_at);

CREATE INDEX IF NOT EXISTS idx_request_logs_domain ON audit.request_logs(domain);
CREATE INDEX IF NOT EXISTS idx_request_logs_status ON audit.request_logs(status);
CREATE INDEX IF NOT EXISTS idx_request_logs_created ON audit.request_logs(created_at);

-- ═══════════════════════════════════════════════════════════════════════════════
-- FUNCTIONS & TRIGGERS
-- ═══════════════════════════════════════════════════════════════════════════════

-- Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger nas tabelas principais
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON core.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads.leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON operations.tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_transactions_updated_at BEFORE UPDATE ON finance.transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ═══════════════════════════════════════════════════════════════════════════════
-- INITIAL DATA
-- ═══════════════════════════════════════════════════════════════════════════════

-- Usuário admin padrão (senha: admin123 - MUDAR EM PRODUÇÃO!)
INSERT INTO core.users (email, password_hash, name, role)
VALUES ('admin@enterprise.local', crypt('admin123', gen_salt('bf')), 'Administrator', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Configurações iniciais
INSERT INTO core.settings (key, value, description) VALUES
('system.version', '"2.0.0"', 'Versão atual do sistema'),
('system.maintenance_mode', 'false', 'Modo de manutenção'),
('leads.auto_assign', 'true', 'Distribuir leads automaticamente'),
('leads.score_threshold_hot', '70', 'Score mínimo para lead hot'),
('leads.score_threshold_warm', '40', 'Score mínimo para lead warm'),
('finance.high_value_threshold', '10000', 'Valor para alerta de transação alta'),
('tasks.sla_critical_hours', '4', 'SLA para tarefas críticas'),
('tasks.sla_high_hours', '24', 'SLA para tarefas alta prioridade')
ON CONFLICT (key) DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════════════════
-- GRANT PERMISSIONS
-- ═══════════════════════════════════════════════════════════════════════════════

-- Ajustar conforme necessário para seu usuário
GRANT USAGE ON ALL SCHEMAS IN DATABASE enterprise_db TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA core TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA leads TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA operations TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA finance TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA monitoring TO admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audit TO admin;

-- ═══════════════════════════════════════════════════════════════════════════════
-- DONE
-- ═══════════════════════════════════════════════════════════════════════════════

SELECT 'Enterprise Empresarial v2.0.0 - Database initialized successfully!' as status;
