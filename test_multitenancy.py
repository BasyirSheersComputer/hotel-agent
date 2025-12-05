import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.metrics_service import get_metrics_service

def test_multitenancy():
    print("=" * 60)
    print("MULTI-TENANCY ISOLATION TEST")
    print("=" * 60)
    
    service = get_metrics_service()
    
    # IDs
    ORG_A = "org_aaaa_1111"
    ORG_B = "org_bbbb_2222"
    
    print(f"\n1. Logging data for Org A ({ORG_A})...")
    service.log_query("Query from Org A", 100, "General", "RAG", "agent_a", ORG_A)
    service.log_query("Another query from Org A", 150, "General", "RAG", "agent_a", ORG_A)
    
    print(f"2. Logging data for Org B ({ORG_B})...")
    service.log_query("Query from Org B", 200, "General", "RAG", "agent_b", ORG_B)
    
    # Verify Org A
    print("\n3. Verifying Org A metrics...")
    metrics_a = service.get_summary_metrics(hours=1, org_id=ORG_A)
    count_a = metrics_a['total_queries']
    print(f"   Org A Total Queries: {count_a}")
    
    if count_a == 2:
        print("   ✅ Org A sees only its own data")
    else:
        print(f"   ❌ Org A sees {count_a} queries (Expected 2)")
        
    # Verify Org B
    print("\n4. Verifying Org B metrics...")
    metrics_b = service.get_summary_metrics(hours=1, org_id=ORG_B)
    count_b = metrics_b['total_queries']
    print(f"   Org B Total Queries: {count_b}")
    
    if count_b == 1:
        print("   ✅ Org B sees only its own data")
    else:
        print(f"   ❌ Org B sees {count_b} queries (Expected 1)")
        
    # Verify Global (No Org ID - Admin view)
    print("\n5. Verifying Global metrics (Admin view)...")
    metrics_global = service.get_summary_metrics(hours=1)
    count_global = metrics_global['total_queries']
    print(f"   Global Total Queries: {count_global}")
    
    if count_global >= 3:
         print("   ✅ Global view sees all data")
    else:
         print(f"   ❌ Global view sees {count_global} queries (Expected >= 3)")

if __name__ == "__main__":
    test_multitenancy()
