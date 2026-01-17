"""add_zap_results_to_scans

Revision ID: 003_add_zap_results
Revises: 91782b460205
Create Date: 2026-01-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_zap_results'
down_revision = '1ba003f6fdbb'  # Changed to depend on sessions migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add zap_results JSON column to scans table
    op.add_column('scans', sa.Column('zap_results', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade() -> None:
    # Remove zap_results column from scans table
    op.drop_column('scans', 'zap_results')

