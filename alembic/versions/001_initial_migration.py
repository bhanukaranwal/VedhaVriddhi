"""Initial migration for VedhaVriddhi Phase 4

Revision ID: 001
Revises: 
Create Date: 2025-09-09 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Quantum Job Records
    op.create_table('quantum_job_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('algorithm_type', sa.String(), nullable=True),
        sa.Column('input_data', sa.JSON(), nullable=True),
        sa.Column('output_data', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )
    op.create_index('ix_quantum_job_records_user_id', 'quantum_job_records', ['user_id'])
    
    # AGI Agents
    op.create_table('agi_agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(), nullable=False),
        sa.Column('capabilities', sa.JSON(), nullable=True),
        sa.Column('current_load', sa.Float(), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=True),
        sa.Column('last_active', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id')
    )
    
    # Carbon Emission Records
    op.create_table('carbon_emission_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_id', sa.String(), nullable=False),
        sa.Column('emission_scope', sa.String(), nullable=True),
        sa.Column('activity_type', sa.String(), nullable=True),
        sa.Column('emission_amount', sa.Float(), nullable=True),
        sa.Column('emission_unit', sa.String(), nullable=True),
        sa.Column('emission_date', sa.DateTime(), nullable=True),
        sa.Column('verification_status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_carbon_emission_records_entity_id', 'carbon_emission_records', ['entity_id'])
    
    # Biometric Templates
    op.create_table('biometric_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('biometric_type', sa.String(), nullable=True),
        sa.Column('template_data', sa.LargeBinary(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_id')
    )
    op.create_index('ix_biometric_templates_user_id', 'biometric_templates', ['user_id'])

def downgrade():
    op.drop_index('ix_biometric_templates_user_id', 'biometric_templates')
    op.drop_table('biometric_templates')
    op.drop_index('ix_carbon_emission_records_entity_id', 'carbon_emission_records')
    op.drop_table('carbon_emission_records')
    op.drop_table('agi_agents')
    op.drop_index('ix_quantum_job_records_user_id', 'quantum_job_records')
    op.drop_table('quantum_job_records')
