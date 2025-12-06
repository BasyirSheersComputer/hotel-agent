
import asyncio
import aiohttp
import time
import json
from statistics import mean

API_URL = "http://localhost:8001"
NUM_USERS = 100
QUERY = "What are the check-in and check-out times?"

async def simulated_user(session, user_id):
    start = time.time()
    payload = {
        "query": QUERY,
        "agent_id": "default",
        "language": "en",
        "session_id": f"load-test-{user_id}"
    }
    
    try:
        async with session.post(f"{API_URL}/api/chat", json=payload) as response:
            duration = time.time() - start
            if response.status == 200:
                data = await response.json()
                return {"status": "success", "duration": duration, "answer": data.get("answer")}
            else:
                text = await response.text()
                return {"status": "error", "code": response.status, "duration": duration, "error": text}
    except Exception as e:
        return {"status": "exception", "error": str(e), "duration": time.time() - start}

async def run_load_test():
    print(f"Starting load test with {NUM_USERS} concurrent users...")
    start_total = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [simulated_user(session, i) for i in range(NUM_USERS)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.time() - start_total
    
    success_count = sum(1 for r in results if r["status"] == "success")
    errors = [r for r in results if r["status"] != "success"]
    durations = [r["duration"] for r in results if r["status"] == "success"]
    
    print(f"\nTotal Time: {total_time:.2f}s")
    print(f"Success Rate: {success_count}/{NUM_USERS} ({success_count/NUM_USERS*100}%)")
    
    if success_count > 0:
        avg_duration = mean(durations)
        print(f"Avg Request Duration: {avg_duration:.2f}s")
        print(f"Min Duration: {min(durations):.2f}s")
        print(f"Max Duration: {max(durations):.2f}s")
        
        # Log one sample
        print("\nSample Response (gpt-4o-mini):")
        print("-" * 40)
        print(results[0].get("answer"))
        print("-" * 40)
    
    if errors:
        print(f"\nErrors ({len(errors)}):")
        print(errors[0]) # Print first error

if __name__ == "__main__":
    asyncio.run(run_load_test())
