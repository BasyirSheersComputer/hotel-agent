"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.

Test script for the Performance Dashboard
Tests metrics collection, API endpoints, and data integrity
"""
import requests
import time
import json

API_BASE = "http://localhost:8000"

def test_chat_with_metrics():
    """Test that chat endpoint logs metrics"""
    print("Testing chat endpoint with metrics logging...")
    
    test_queries = [
        "What time does the pool close?",
        "Where is the nearest pharmacy?",
        "Is breakfast included?",
        "What activities are available?",
        "Show me restaurants at the resort"
    ]
    
    for query in test_queries:
        response = requests.post(
            f"{API_BASE}/api/chat",
            json={"query": query}
        )
        
        if response.status_code == 200:
            print(f"✓ Query: '{query}' - Success")
        else:
            print(f"✗ Query: '{query}' - Failed: {response.status_code}")
        
        time.sleep(0.5)  # Small delay between queries

def test_metrics_summary():
    """Test metrics summary endpoint"""
    print("\nTesting metrics summary endpoint...")
    
    response = requests.get(f"{API_BASE}/api/metrics/summary?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Metrics Summary Retrieved:")
        print(f"  - Total Queries: {data['total_queries']}")
        print(f"  - Avg Response Time: {data['avg_response_time_ms']}ms")
        print(f"  - Accuracy: {data['accuracy_percent']}%")
        print(f"  - AHT Reduction: {data['aht_reduction_percent']}%")
        print(f"  - Est. Cost: ${data['estimated_cost']}")
    else:
        print(f"✗ Failed to fetch metrics summary: {response.status_code}")
        print(response.text)

def test_categories():
    """Test category metrics endpoint"""
    print("\nTesting question categories endpoint...")
    
    response = requests.get(f"{API_BASE}/api/metrics/categories?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data)} categories")
        for cat in data[:3]:
            print(f"  - {cat['category']}: {cat['count']} queries, {cat['avg_ai_time']}ms avg, {cat['accuracy']}% acc")
    else:
        print(f"✗ Failed to fetch categories: {response.status_code}")

def test_trends():
    """Test hourly trends endpoint"""
    print("\nTesting hourly trends endpoint...")
    
    response = requests.get(f"{API_BASE}/api/metrics/trends?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data)} hourly data points")
        if data:
            latest = data[-1]
            print(f"  - Latest hour: {latest['time']}")
            print(f"  - Query volume: {latest['queryVolume']}")
    else:
        print(f"✗ Failed to fetch trends: {response.status_code}")

def test_agents():
    """Test agent performance endpoint"""
    print("\nTesting agent performance endpoint...")
    
    response = requests.get(f"{API_BASE}/api/metrics/agents?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data)} agents")
        for agent in data:
            print(f"  - {agent['name']}: {agent['queryCount']} queries, {agent['accuracyPercent']}% acc")
    else:
        print(f"✗ Failed to fetch agent metrics: {response.status_code}")

def test_sources():
    """Test source distribution endpoint"""
    print("\nTesting source distribution endpoint...")
    
    response = requests.get(f"{API_BASE}/api/metrics/sources?hours=24")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Retrieved {len(data)} source types")
        for source in data:
            print(f"  - {source['source']}: {source['count']} queries ({source['percentage']}%)")
    else:
        print(f"✗ Failed to fetch source distribution: {response.status_code}")

def main():
    print("=" * 60)
    print("PERFORMANCE DASHBOARD TEST SUITE (DESIGN V2)")
    print("=" * 60)
    
    # First, generate some test data
    print("\n1. Generating test data...")
    test_chat_with_metrics()
    
    # Wait a moment for metrics to be logged
    time.sleep(1)
    
    # Test all metrics endpoints
    print("\n2. Testing metrics endpoints...")
    test_metrics_summary()
    test_categories()
    test_trends()
    test_agents()
    test_sources()
    
    print("\n" + "=" * 60)
    print("Dashboard test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()

