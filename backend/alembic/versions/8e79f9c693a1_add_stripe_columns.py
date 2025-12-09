"""add_stripe_columns

Revision ID: 8e79f9c693a1
Revises: e7e5058660e5
Create Date: 2025-12-09 09:02:19.371894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e79f9c693a1'
down_revision: Union[str, Sequence[str], None] = 'e7e5058660e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    is_sqlite = bind.engine.name == "sqlite"

    # Add columns (Supported by SQLite if nullable)
    op.add_column('organizations', sa.Column('stripe_customer_id', sa.String(length=255), nullable=True))
    op.add_column('organizations', sa.Column('subscription_status', sa.String(length=50), nullable=True))
    op.add_column('organizations', sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True))

    if not is_sqlite:
        # Postgres supports ADD CONSTRAINT
        op.create_unique_constraint('uq_organizations_stripe_customer_id', 'organizations', ['stripe_customer_id'])
    else:
        print("Skipping Unique Constraint for SQLite to avoid batch migration issues on root table.")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    is_sqlite = bind.engine.name == "sqlite"
    
    if not is_sqlite:
        op.drop_constraint('uq_organizations_stripe_customer_id', 'organizations', type_='unique')

    op.drop_column('organizations', 'current_period_end')
    op.drop_column('organizations', 'subscription_status')
    op.drop_column('organizations', 'stripe_customer_id')
