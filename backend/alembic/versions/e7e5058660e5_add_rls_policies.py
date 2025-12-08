"""add_rls_policies

Revision ID: e7e5058660e5
Revises: 
Create Date: 2025-12-08 22:30:51.839386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7e5058660e5'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable RLS on core tables
    op.execute("ALTER TABLE users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE organizations ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE queries ENABLE ROW LEVEL SECURITY")

    # 2. Create Tenant Policy
    # Policy: Users can only see rows where org_id matches current session variable
    # We use a session variable 'app.current_org_id' which is set by middleware
    
    # User Policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON users
        USING (org_id::text = current_setting('app.current_org_id', true))
    """)
    
    # Org Policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON organizations
        USING (org_id::text = current_setting('app.current_org_id', true))
    """)

    # Chat Session Policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON chat_sessions
        USING (org_id::text = current_setting('app.current_org_id', true))
        WITH CHECK (org_id::text = current_setting('app.current_org_id', true))
    """)
    
    # Chat Message Policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON chat_messages
        USING (org_id::text = current_setting('app.current_org_id', true))
        WITH CHECK (org_id::text = current_setting('app.current_org_id', true))
    """)
    
    # Metrics Policy
    op.execute("""
        CREATE POLICY tenant_isolation_policy ON queries
        USING (org_id::text = current_setting('app.current_org_id', true))
    """)


def downgrade() -> None:
    # Remove Policies
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON users")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON organizations")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON chat_sessions")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON chat_messages")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON queries")
    
    # Disable RLS
    op.execute("ALTER TABLE users DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE organizations DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_sessions DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE queries DISABLE ROW LEVEL SECURITY")
