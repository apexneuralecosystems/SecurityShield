"""Initial migration - create tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-16 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create websites table
    op.create_table(
        'websites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_websites_id'), 'websites', ['id'], unique=False)
    op.create_index(op.f('ix_websites_url'), 'websites', ['url'], unique=True)
    
    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('website_id', sa.Integer(), nullable=False),
        sa.Column('scan_type', sa.String(length=50), nullable=False),
        sa.Column('scan_time', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('total_issues', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('high_issues', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('medium_issues', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('low_issues', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('security_score', sa.Float(), nullable=True),
        sa.Column('owasp_aligned', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('scan_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['website_id'], ['websites.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scans_id'), 'scans', ['id'], unique=False)
    op.create_index(op.f('ix_scans_website_id'), 'scans', ['website_id'], unique=False)
    op.create_index(op.f('ix_scans_scan_type'), 'scans', ['scan_type'], unique=False)
    op.create_index(op.f('ix_scans_scan_time'), 'scans', ['scan_time'], unique=False)
    
    # Create issues table
    op.create_table(
        'issues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('impact', sa.String(length=20), nullable=False),
        sa.Column('issue_type', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('reported_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(length=255), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_issues_id'), 'issues', ['id'], unique=False)
    op.create_index(op.f('ix_issues_scan_id'), 'issues', ['scan_id'], unique=False)
    op.create_index(op.f('ix_issues_impact'), 'issues', ['impact'], unique=False)
    op.create_index(op.f('ix_issues_status'), 'issues', ['status'], unique=False)
    
    # Create security_features table
    op.create_table(
        'security_features',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scan_id', sa.Integer(), nullable=False),
        sa.Column('feature_name', sa.String(length=255), nullable=False),
        sa.Column('feature_type', sa.String(length=100), nullable=False),
        sa.Column('is_implemented', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('implementation_details', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_security_features_id'), 'security_features', ['id'], unique=False)
    op.create_index(op.f('ix_security_features_scan_id'), 'security_features', ['scan_id'], unique=False)
    op.create_index(op.f('ix_security_features_feature_name'), 'security_features', ['feature_name'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_security_features_feature_name'), table_name='security_features')
    op.drop_index(op.f('ix_security_features_scan_id'), table_name='security_features')
    op.drop_index(op.f('ix_security_features_id'), table_name='security_features')
    op.drop_table('security_features')
    
    op.drop_index(op.f('ix_issues_status'), table_name='issues')
    op.drop_index(op.f('ix_issues_impact'), table_name='issues')
    op.drop_index(op.f('ix_issues_scan_id'), table_name='issues')
    op.drop_index(op.f('ix_issues_id'), table_name='issues')
    op.drop_table('issues')
    
    op.drop_index(op.f('ix_scans_scan_time'), table_name='scans')
    op.drop_index(op.f('ix_scans_scan_type'), table_name='scans')
    op.drop_index(op.f('ix_scans_website_id'), table_name='scans')
    op.drop_index(op.f('ix_scans_id'), table_name='scans')
    op.drop_table('scans')
    
    op.drop_index(op.f('ix_websites_url'), table_name='websites')
    op.drop_index(op.f('ix_websites_id'), table_name='websites')
    op.drop_table('websites')

