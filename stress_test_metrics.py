import asyncio
import aiohttp
import time
import json
import random
from statistics import mean

API_URL = "http://localhost:8000"  # Note: 8000 is internal/mapped, checking port... backend is usually 8000.
NUM_USERS = 100

# Diverse queries to trigger meaningful metrics
QUERIES = [
    # TYPE 1: Booking Intent (Revenue)
    {"text": "I want to book the Presidential Suite for next week.", "type": "revenue"},
    {"text": "What is the price for a 5-night stay in a villa?", "type": "revenue"},
    
    # TYPE 2: Upsell Intent (Revenue)
    {"text": "Do you have any upgrades available?", "type": "revenue_upsell"},
    {"text": "I'd like to add a spa package to my reservation.", "type": "revenue_upsell"},
    
    # TYPE 3: Sentiment/CSAT (Positive)
    {"text": "Thank you, that was very helpful!", "type": "csat_pos"},
    {"text": "Great service, thanks a lot.", "type": "csat_pos"},
    
    # TYPE 4: Sentiment/CSAT (Negative)
    {"text": "This information is incorrect.", "type": "csat_neg"},
    {"text": "I am not happy with this answer.", "type": "csat_neg"},
    
    # TYPE 5: Efficiency (General Info)
    {"text": "What are the pool hours?", "type": "efficiency"},
    {"text": "Is breakfast included?", "type": "efficiency"},
]

async def simulated_user(session, user_id):
    # Randomly select a query type to simulate diverse traffic
    query_data = random.choice(QUERIES)
    
    start = time.time()
    payload = {
        "query": query_data["text"],
        "agent_id": f"load_agent_{user_id}",
        "language": "en",
        "session_id": f"load-test-{user_id}"
    }
    
    try:
        async with session.post(f"{API_URL}/api/chat", json=payload) as response:
            duration = time.time() - start
            if response.status == 200:
                data = await response.json()
                if user_id == 0:
                    print(f"DEBUG BODY: {json.dumps(data)}")
                return {
                    "status": "success", 
                    "duration": duration, 
                    "type": query_data["type"]
                }
            else:
                text = await response.text()
                return {
                    "status": "error", 
                    "code": response.status, 
                    "duration": duration, 
                    "error": text
                }
    except Exception as e:
        return {"status": "exception", "error": str(e), "duration": time.time() - start}

async def run_load_test():
    print(f"Starting STRESS TEST with {NUM_USERS} concurrent users...")
    print(f"Target URL: {API_URL}")
    start_total = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Launch all requests concurrently
        tasks = [simulated_user(session, i) for i in range(NUM_USERS)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_total
    
    # Analysis
    success_count = sum(1 for r in results if r["status"] == "success")
    errors = [r for r in results if r["status"] != "success"]
    durations = [r["duration"] for r in results if r["status"] == "success"]
    
    print(f"\n--- RESULTS ---")
    print(f"Total Time: {total_time:.2f}s")
    print(f"Throughput: {NUM_USERS / total_time:.2f} req/s")
    print(f"Success Rate: {success_count}/{NUM_USERS} ({success_count/NUM_USERS*100}%)")
    
    if success_count > 0:
        avg_duration = mean(durations)
        print(f"Avg Request Duration: {avg_duration:.2f}s")
        print(f"Min Duration: {min(durations):.2f}s")
        print(f"Max Duration: {max(durations):.2f}s")
        
        # Breakdown by Type
        type_counts = {}
        for r in results:
            if r["status"] == "success":
                t = r["type"]
                type_counts[t] = type_counts.get(t, 0) + 1
        print(f"\nBreakdown by Type (Successes): {type_counts}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        # Group errors
        error_counts = {}
        for e in errors:
            key = f"{e.get('code', 'EXC')}: {e.get('error', '')[:50]}"
            error_counts[key] = error_counts.get(key, 0) + 1
        for k, v in error_counts.items():
            print(f"  {k}: {v} occurrences")
            
    # DEBUG: Print first success full response
    if success_count > 0:
        print("\n--- DEBUG: First Success Response ---")
        first_success = next(r for r in results if r["status"] == "success")
        # We need to capture the body in the main loop to print it here, 
        # but 'results' currently only has metadata. 
        # Let's trust the simulated_user function's modification below.


if __name__ == "__main__":
    asyncio.run(run_load_test())
