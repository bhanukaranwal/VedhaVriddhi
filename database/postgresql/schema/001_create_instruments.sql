-- VedhaVriddhi - Instruments Master Schema
-- This schema handles all fixed income instruments in the Indian market

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom enum types
CREATE TYPE bond_type AS ENUM (
    'government_security',
    'treasury_bill',
    'corporate_bond',
    'state_government_bond',
    'municipal_bond',
    'certificate_of_deposit',
    'commercial_paper'
);

CREATE TYPE rating_grade AS ENUM (
    'AAA', 'AA+', 'AA', 'AA-', 'A+', 'A', 'A-',
    'BBB+', 'BBB', 'BBB-', 'BB+', 'BB', 'BB-',
    'B+', 'B', 'B-', 'CCC+', 'CCC', 'CCC-',
    'CC', 'C', 'D', 'NR'
);

CREATE TYPE instrument_status AS ENUM (
    'active',
    'inactive',
    'matured',
    'delisted',
    'suspended'
);

-- Instruments master table
CREATE TABLE instruments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    isin VARCHAR(12) NOT NULL UNIQUE,
    symbol VARCHAR(50) NOT NULL,
    instrument_name TEXT NOT NULL,
    issuer_id UUID NOT NULL,
    bond_type bond_type NOT NULL,
    face_value DECIMAL(15,2) NOT NULL DEFAULT 100.00,
    coupon_rate DECIMAL(8,4),
    issue_date DATE NOT NULL,
    maturity_date DATE NOT NULL,
    coupon_payment_frequency INTEGER DEFAULT 2, -- Semi-annual by default
    day_count_convention VARCHAR(20) DEFAULT '30/360',
    settlement_days INTEGER DEFAULT 1,
    minimum_lot_size DECIMAL(15,2) DEFAULT 1.00,
    tick_size DECIMAL(10,6) DEFAULT 0.0001,
    currency VARCHAR(3) DEFAULT 'INR',
    exchange VARCHAR(10) NOT NULL,
    sector VARCHAR(50),
    sub_sector VARCHAR(50),
    credit_rating rating_grade,
    rating_agency VARCHAR(50),
    rating_date DATE,
    is_callable BOOLEAN DEFAULT FALSE,
    call_date DATE,
    call_price DECIMAL(15,4),
    is_puttable BOOLEAN DEFAULT FALSE,
    put_date DATE,
    put_price DECIMAL(15,4),
    status instrument_status DEFAULT 'active',
    listing_date DATE,
    delisting_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID
);

-- Issuers master table
CREATE TABLE issuers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issuer_code VARCHAR(20) NOT NULL UNIQUE,
    issuer_name TEXT NOT NULL,
    issuer_type VARCHAR(50) NOT NULL, -- Government, Corporate, Bank, etc.
    country VARCHAR(3) DEFAULT 'IND',
    sector VARCHAR(50),
    sub_sector VARCHAR(50),
    credit_rating rating_grade,
    rating_agency VARCHAR(50),
    rating_date DATE,
    parent_company_id UUID,
    website VARCHAR(255),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add foreign key constraint
ALTER TABLE instruments 
ADD CONSTRAINT fk_instruments_issuer 
FOREIGN KEY (issuer_id) REFERENCES issuers(id);

-- Government Securities specific table
CREATE TABLE government_securities (
    instrument_id UUID PRIMARY KEY,
    security_type VARCHAR(50) NOT NULL, -- FRB, ILB, SDL, etc.
    auction_date DATE,
    auction_type VARCHAR(20), -- Competitive, Non-competitive
    yield_at_issue DECIMAL(8,4),
    inflation_index VARCHAR(50), -- For inflation-linked bonds
    index_base_value DECIMAL(15,6), -- For inflation-linked bonds
    reopening_date DATE,
    total_issue_size DECIMAL(18,2),
    notified_amount DECIMAL(18,2),
    government_type VARCHAR(20) DEFAULT 'Central', -- Central, State
    FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
);

-- Corporate Bonds specific table
CREATE TABLE corporate_bonds (
    instrument_id UUID PRIMARY KEY,
    bond_series VARCHAR(20),
    subordination_type VARCHAR(30), -- Senior, Subordinated, etc.
    security_type VARCHAR(50), -- Secured, Unsecured
    asset_classification VARCHAR(50), -- Pass Through, Asset Backed, etc.
    interest_payment_type VARCHAR(20) DEFAULT 'Fixed', -- Fixed, Floating, Zero
    floating_rate_benchmark VARCHAR(20), -- MIBOR, Repo Rate, etc.
    spread_over_benchmark DECIMAL(8,4),
    reset_frequency INTEGER, -- In months
    conversion_ratio DECIMAL(15,6), -- For convertible bonds
    conversion_price DECIMAL(15,4), -- For convertible bonds
    trustee_name VARCHAR(255),
    debenture_trustee_id VARCHAR(50),
    security_details TEXT,
    use_of_funds TEXT,
    covenants TEXT,
    FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
);

-- Money Market Instruments table (CDs, CPs, T-Bills)
CREATE TABLE money_market_instruments (
    instrument_id UUID PRIMARY KEY,
    discount_rate DECIMAL(8,4),
    issue_price DECIMAL(15,4),
    maturity_value DECIMAL(15,4),
    minimum_investment DECIMAL(15,2),
    maximum_investment DECIMAL(15,2),
    is_negotiable BOOLEAN DEFAULT TRUE,
    backing_bank VARCHAR(255), -- For CDs
    credit_facility_details TEXT, -- For CPs
    FOREIGN KEY (instrument_id) REFERENCES instruments(id) ON DELETE CASCADE
);

-- Instrument trading sessions
CREATE TABLE trading_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(50) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    instrument_type bond_type,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    pre_open_start TIME,
    pre_open_end TIME,
    post_close_start TIME,
    post_close_end TIME,
    is_active BOOLEAN DEFAULT TRUE,
    effective_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Instrument corporate actions
CREATE TABLE corporate_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instrument_id UUID NOT NULL,
    action_type VARCHAR(50) NOT NULL, -- Interest Payment, Redemption, Call, etc.
    record_date DATE NOT NULL,
    ex_date DATE,
    payment_date DATE,
    amount_per_unit DECIMAL(15,4),
    currency VARCHAR(3) DEFAULT 'INR',
    description TEXT,
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (instrument_id) REFERENCES instruments(id)
);

-- Interest rate benchmarks
CREATE TABLE interest_rate_benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    benchmark_name VARCHAR(50) NOT NULL,
    benchmark_code VARCHAR(20) NOT NULL UNIQUE,
    description TEXT,
    currency VARCHAR(3) DEFAULT 'INR',
    tenor VARCHAR(10), -- ON, 1M, 3M, 6M, 1Y, etc.
    calculation_method TEXT,
    publisher VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Daily benchmark rates
CREATE TABLE benchmark_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    benchmark_id UUID NOT NULL,
    rate_date DATE NOT NULL,
    rate_value DECIMAL(8,4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (benchmark_id) REFERENCES interest_rate_benchmarks(id),
    UNIQUE(benchmark_id, rate_date)
);

-- Indexes
CREATE INDEX idx_instruments_isin ON instruments(isin);
CREATE INDEX idx_instruments_symbol ON instruments(symbol);
CREATE INDEX idx_instruments_issuer ON instruments(issuer_id);
CREATE INDEX idx_instruments_type ON instruments(bond_type);
CREATE INDEX idx_instruments_maturity ON instruments(maturity_date);
CREATE INDEX idx_instruments_status ON instruments(status);
CREATE INDEX idx_instruments_exchange ON instruments(exchange);

CREATE INDEX idx_issuers_code ON issuers(issuer_code);
CREATE INDEX idx_issuers_name ON issuers(issuer_name);
CREATE INDEX idx_issuers_type ON issuers(issuer_type);

CREATE INDEX idx_corporate_actions_instrument ON corporate_actions(instrument_id);
CREATE INDEX idx_corporate_actions_record_date ON corporate_actions(record_date);
CREATE INDEX idx_corporate_actions_type ON corporate_actions(action_type);

CREATE INDEX idx_benchmark_rates_date ON benchmark_rates(rate_date);
CREATE INDEX idx_benchmark_rates_benchmark ON benchmark_rates(benchmark_id);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for automatic timestamp updates
CREATE TRIGGER update_instruments_updated_at 
    BEFORE UPDATE ON instruments 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_issuers_updated_at 
    BEFORE UPDATE ON issuers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE instruments IS 'Master table for all fixed income instruments traded on Indian exchanges';
COMMENT ON TABLE issuers IS 'Master table for all bond issuers including government and corporate entities';
COMMENT ON TABLE government_securities IS 'Additional details specific to government securities';
COMMENT ON TABLE corporate_bonds IS 'Additional details specific to corporate bonds';
COMMENT ON TABLE money_market_instruments IS 'Details for money market instruments like CDs, CPs, and T-Bills';
COMMENT ON TABLE corporate_actions IS 'Corporate actions affecting instruments like interest payments and redemptions';
COMMENT ON TABLE interest_rate_benchmarks IS 'Reference interest rate benchmarks used for floating rate instruments';
COMMENT ON TABLE benchmark_rates IS 'Daily rates for various interest rate benchmarks';
