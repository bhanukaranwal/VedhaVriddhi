-- VedhaVriddhi - Users and Authentication Schema
-- This schema handles user management, authentication, and authorization

-- Create custom enum types
CREATE TYPE user_role AS ENUM (
    'trader',
    'risk_manager',
    'compliance_officer',
    'portfolio_manager',
    'administrator',
    'operations',
    'read_only'
);

CREATE TYPE user_status AS ENUM (
    'active',
    'inactive',
    'suspended',
    'locked',
    'pending_activation'
);

CREATE TYPE session_status AS ENUM (
    'active',
    'expired',
    'terminated'
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'trader',
    status user_status NOT NULL DEFAULT 'pending_activation',
    employee_id VARCHAR(50),
    department VARCHAR(100),
    manager_id UUID,
    phone_number VARCHAR(20),
    mobile_number VARCHAR(20),
    emergency_contact VARCHAR(255),
    date_of_birth DATE,
    joining_date DATE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    last_login_ip INET,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    password_expires_at TIMESTAMP WITH TIME ZONE,
    must_change_password BOOLEAN DEFAULT TRUE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    backup_codes TEXT[], -- Array of backup codes for 2FA
    preferences JSONB DEFAULT '{}',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID,
    FOREIGN KEY (manager_id) REFERENCES users(id)
);

-- User sessions table
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_token VARCHAR(255) NOT NULL UNIQUE,
    refresh_token VARCHAR(255) NOT NULL UNIQUE,
    ip_address INET NOT NULL,
    user_agent TEXT,
    device_info JSONB,
    location_info JSONB,
    status session_status NOT NULL DEFAULT 'active',
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    terminated_at TIMESTAMP WITH TIME ZONE,
    termination_reason VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    resource VARCHAR(100) NOT NULL, -- orders, trades, positions, etc.
    action VARCHAR(50) NOT NULL, -- create, read, update, delete, execute
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Role permissions mapping
CREATE TABLE role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role user_role NOT NULL,
    permission_id UUID NOT NULL,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID,
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    UNIQUE(role, permission_id)
);

-- User-specific permission overrides
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    permission_id UUID NOT NULL,
    is_granted BOOLEAN NOT NULL DEFAULT TRUE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    granted_by UUID NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE,
    reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    FOREIGN KEY (granted_by) REFERENCES users(id),
    UNIQUE(user_id, permission_id)
);

-- API keys for system integrations
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    key_name VARCHAR(100) NOT NULL,
    api_key VARCHAR(255) NOT NULL UNIQUE,
    api_secret VARCHAR(255) NOT NULL,
    permissions TEXT[], -- Array of permission names
    rate_limit_per_minute INTEGER DEFAULT 1000,
    rate_limit_per_hour INTEGER DEFAULT 50000,
    ip_whitelist INET[],
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count BIGINT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- User activity audit log
CREATE TABLE user_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_id UUID,
    activity_type VARCHAR(100) NOT NULL, -- login, logout, order_submit, etc.
    resource_type VARCHAR(100), -- order, trade, position, etc.
    resource_id UUID,
    action VARCHAR(50) NOT NULL, -- create, read, update, delete, execute
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(20) NOT NULL, -- success, failure, error
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES user_sessions(id)
);

-- User accounts (trading accounts)
CREATE TABLE user_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    account_number VARCHAR(50) NOT NULL UNIQUE,
    account_name VARCHAR(255) NOT NULL,
    account_type VARCHAR(50) NOT NULL, -- Individual, Corporate, Institutional
    entity_id VARCHAR(100), -- For corporate accounts
    base_currency VARCHAR(3) DEFAULT 'INR',
    is_active BOOLEAN DEFAULT TRUE,
    margin_enabled BOOLEAN DEFAULT FALSE,
    settlement_bank_account VARCHAR(50),
    dp_account VARCHAR(50), -- Demat account
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Password history for security
CREATE TABLE password_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Login attempts tracking
CREATE TABLE login_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50),
    email VARCHAR(255),
    ip_address INET NOT NULL,
    user_agent TEXT,
    success BOOLEAN NOT NULL,
    failure_reason VARCHAR(255),
    attempted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_last_login ON users(last_login_at);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_status ON user_sessions(status);
CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

CREATE INDEX idx_user_activity_user_id ON user_activity_log(user_id);
CREATE INDEX idx_user_activity_type ON user_activity_log(activity_type);
CREATE INDEX idx_user_activity_created ON user_activity_log(created_at);

CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX idx_api_keys_key ON api_keys(api_key);
CREATE INDEX idx_api_keys_active ON api_keys(is_active);

CREATE INDEX idx_user_accounts_user_id ON user_accounts(user_id);
CREATE INDEX idx_user_accounts_number ON user_accounts(account_number);

CREATE INDEX idx_login_attempts_ip ON login_attempts(ip_address);
CREATE INDEX idx_login_attempts_time ON login_attempts(attempted_at);

-- Triggers for automatic updates
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_accounts_updated_at 
    BEFORE UPDATE ON user_accounts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE user_sessions 
    SET status = 'expired', 
        terminated_at = CURRENT_TIMESTAMP,
        termination_reason = 'expired'
    WHERE status = 'active' 
    AND expires_at < CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to check user permissions
CREATE OR REPLACE FUNCTION user_has_permission(
    p_user_id UUID,
    p_resource VARCHAR,
    p_action VARCHAR
) RETURNS BOOLEAN AS $$
DECLARE
    user_role_val user_role;
    has_permission BOOLEAN := FALSE;
    permission_override BOOLEAN;
BEGIN
    -- Get user role
    SELECT role INTO user_role_val FROM users WHERE id = p_user_id;
    
    -- Check role-based permissions
    SELECT COUNT(*) > 0 INTO has_permission
    FROM role_permissions rp
    JOIN permissions p ON rp.permission_id = p.id
    WHERE rp.role = user_role_val
    AND p.resource = p_resource
    AND p.action = p_action;
    
    -- Check user-specific permission overrides
    SELECT is_granted INTO permission_override
    FROM user_permissions up
    JOIN permissions p ON up.permission_id = p.id
    WHERE up.user_id = p_user_id
    AND p.resource = p_resource
    AND p.action = p_action
    AND (up.expires_at IS NULL OR up.expires_at > CURRENT_TIMESTAMP);
    
    -- Override takes precedence
    IF permission_override IS NOT NULL THEN
        has_permission := permission_override;
    END IF;
    
    RETURN has_permission;
END;
$$ LANGUAGE plpgsql;

-- Insert default permissions
INSERT INTO permissions (name, description, resource, action) VALUES
('orders.create', 'Create new orders', 'orders', 'create'),
('orders.read', 'View orders', 'orders', 'read'),
('orders.update', 'Modify orders', 'orders', 'update'),
('orders.delete', 'Cancel orders', 'orders', 'delete'),
('trades.read', 'View trades', 'trades', 'read'),
('positions.read', 'View positions', 'positions', 'read'),
('positions.update', 'Modify positions', 'positions', 'update'),
('portfolio.read', 'View portfolio', 'portfolio', 'read'),
('portfolio.manage', 'Manage portfolio', 'portfolio', 'update'),
('risk.read', 'View risk reports', 'risk', 'read'),
('risk.manage', 'Manage risk limits', 'risk', 'update'),
('compliance.read', 'View compliance reports', 'compliance', 'read'),
('compliance.manage', 'Manage compliance rules', 'compliance', 'update'),
('admin.users', 'Manage users', 'users', 'update'),
('admin.system', 'System administration', 'system', 'update'),
('market_data.read', 'View market data', 'market_data', 'read'),
('reports.read', 'View reports', 'reports', 'read'),
('reports.generate', 'Generate reports', 'reports', 'create');

-- Insert default role permissions
INSERT INTO role_permissions (role, permission_id, granted_by) 
SELECT 'trader', id, (SELECT id FROM users WHERE username = 'system' LIMIT 1)
FROM permissions 
WHERE name IN (
    'orders.create', 'orders.read', 'orders.update', 'orders.delete',
    'trades.read', 'positions.read', 'portfolio.read', 'market_data.read'
);

INSERT INTO role_permissions (role, permission_id, granted_by) 
SELECT 'risk_manager', id, (SELECT id FROM users WHERE username = 'system' LIMIT 1)
FROM permissions 
WHERE name IN (
    'orders.read', 'trades.read', 'positions.read', 'portfolio.read',
    'risk.read', 'risk.manage', 'market_data.read', 'reports.read', 'reports.generate'
);

INSERT INTO role_permissions (role, permission_id, granted_by) 
SELECT 'compliance_officer', id, (SELECT id FROM users WHERE username = 'system' LIMIT 1)
FROM permissions 
WHERE name IN (
    'orders.read', 'trades.read', 'positions.read', 'portfolio.read',
    'compliance.read', 'compliance.manage', 'reports.read', 'reports.generate'
);

INSERT INTO role_permissions (role, permission_id, granted_by) 
SELECT 'administrator', id, (SELECT id FROM users WHERE username = 'system' LIMIT 1)
FROM permissions;

-- Comments
COMMENT ON TABLE users IS 'Master table for all system users with authentication and profile information';
COMMENT ON TABLE user_sessions IS 'Active user sessions with security tracking';
COMMENT ON TABLE permissions IS 'System permissions for role-based access control';
COMMENT ON TABLE role_permissions IS 'Permissions assigned to user roles';
COMMENT ON TABLE user_permissions IS 'User-specific permission overrides';
COMMENT ON TABLE api_keys IS 'API keys for system integration and programmatic access';
COMMENT ON TABLE user_activity_log IS 'Audit log for all user activities in the system';
COMMENT ON TABLE user_accounts IS 'Trading accounts associated with users';
