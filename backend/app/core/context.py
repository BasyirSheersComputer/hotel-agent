"""
ContextVars for Tenant Isolation.
Allows deep access to tenant context (e.g. in DB event listeners) without passing Request object.
"""
from contextvars import ContextVar
from typing import Optional

# Context variable to hold the current Organization ID
# Default is None (no tenant context)
tenant_context: ContextVar[Optional[str]] = ContextVar("tenant_context", default=None)

def set_tenant_id(org_id: Optional[str]):
    return tenant_context.set(org_id)

def get_tenant_id() -> Optional[str]:
    return tenant_context.get()
