import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
import json

class VedhaVriddhiLoadTester:
    """Comprehensive load testing for all VedhaVriddhi services"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[Dict] = []
        
    async def test_quantum_service(self, concurrent_users: int = 50, requests_per_user: int = 10):
        """Load test quantum optimization endpoint"""
        print(f"Testing Quantum Service with {concurrent_users} concurrent users...")
        
        async def quantum_request(session: aiohttp.ClientSession):
            payload = {
                "portfolio": {
                    "assets": ["AAPL", "GOOGL", "TSLA", "MSFT"],
                    "expected_returns": [0.12, 0.15, 0.18, 0.14],
                    "covariance_matrix": [
                        [0.1, 0.02, 0.03, 0.01],
                        [0.02, 0.15, 0.04, 0.02],
                        [0.03, 0.04, 0.2, 0.03],
                        [0.01, 0.02, 0.03, 0.12]
                    ],
                    "constraints": {"min_weight": 0.0, "max_weight": 0.5, "target_return": 0.15}
                },
                "optimization_params": {"algorithm": "QAOA", "layers": 3, "shots": 1024}
            }
            
            start_time = time.time()
            try:
                async with session.post(f"{self.base_url}/quantum/optimize", json=payload) as response:
                    result = await response.json()
                    response_time = time.time() - start_time
                    return {"success": response.status == 200, "response_time": response_time, "result": result}
            except Exception as e:
                return {"success": False, "response_time": time.time() - start_time, "error": str(e)}
        
        async def user_simulation(user_id: int):
            async with aiohttp.ClientSession() as session:
                tasks = [quantum_request(session) for _ in range(requests_per_user)]
                return await asyncio.gather(*tasks)
        
        # Execute load test
        start_time = time.time()
        user_tasks = [user_simulation(i) for i in range(concurrent_users)]
        all_results = await asyncio.gather(*user_tasks)
        total_time = time.time() - start_time
        
        # Flatten results
        flat_results = [result for user_results in all_results for result in user_results]
        
        # Calculate statistics
        successful_requests = len([r for r in flat_results if r["success"]])
        response_times = [r["response_time"] for r in flat_results if r["success"]]
        
        stats = {
            "service": "quantum",
            "total_requests": len(flat_results),
            "successful_requests": successful_requests,
            "failed_requests": len(flat_results) - successful_requests,
            "success_rate": successful_requests / len(flat_results),
            "total_time": total_time,
            "requests_per_second": len(flat_results) / total_time,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0,
            "p95_response_time": statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else 0,
            "p99_response_time": statistics.quantiles(response_times, n=100)[98] if len(response_times) > 100 else 0
        }
        
        self.results.append(stats)
        print(f"Quantum Service Results: {stats['requests_per_second']:.2f} RPS, {stats['success_rate']:.2%} success rate")
        return stats
    
    async def test_agi_service(self, concurrent_users: int = 30, requests_per_user: int = 5):
        """Load test AGI reasoning endpoint"""
        print(f"Testing AGI Service with {concurrent_users} concurrent users...")
        
        async def agi_request(session: aiohttp.ClientSession):
            payload = {
                "reasoning_type": "deductive",
                "premises": [
                    "All technology stocks are volatile",
                    "AAPL is a technology stock",
                    "Market volatility increases during economic uncertainty"
                ],
                "query": "What can we conclude about AAPL's behavior during economic uncertainty?",
                "context": {"domain": "financial_markets", "urgency": "medium"}
            }
            
            start_time = time.time()
            try:
                async with session.post(f"{self.base_url}/agi/reason", json=payload) as response:
                    result = await response.json()
                    response_time = time.time() - start_time
                    return {"success": response.status == 200, "response_time": response_time}
            except Exception as e:
                return {"success": False, "response_time": time.time() - start_time, "error": str(e)}
        
        return await self._execute_service_test("agi", agi_request, concurrent_users, requests_per_user)
    
    async def test_consciousness_service(self, concurrent_users: int = 20, requests_per_user: int = 3):
        """Load test consciousness synthesis endpoint"""
        print(f"Testing Consciousness Service with {concurrent_users} concurrent users...")
        
        async def consciousness_request(session: aiohttp.ClientSession):
            payload = {
                "consciousness_inputs": [
                    {
                        "entity_id": "trader_001",
                        "awareness": 0.8,
                        "emotional_resonance": 0.7,
                        "integration": 0.9,
                        "wisdom_elements": ["patience", "intuition", "analysis"]
                    },
                    {
                        "entity_id": "ai_agent_002", 
                        "awareness": 0.95,
                        "emotional_resonance": 0.6,
                        "integration": 0.85,
                        "wisdom_elements": ["logic", "pattern_recognition", "optimization"]
                    }
                ]
            }
            
            start_time = time.time()
            try:
                async with session.post(f"{self.base_url}/consciousness/synthesize", json=payload) as response:
                    result = await response.json()
                    response_time = time.time() - start_time
                    return {"success": response.status == 200, "response_time": response_time}
            except Exception as e:
                return {"success": False, "response_time": time.time() - start_time, "error": str(e)}
        
        return await self._execute_service_test("consciousness", consciousness_request, concurrent_users, requests_per_user)
    
    async def _execute_service_test(self, service_name: str, request_func, concurrent_users: int, requests_per_user: int):
        """Execute load test for any service"""
        async def user_simulation(user_id: int):
            async with aiohttp.ClientSession() as session:
                tasks = [request_func(session) for _ in range(requests_per_user)]
                return await asyncio.gather(*tasks)
        
        start_time = time.time()
        user_tasks = [user_simulation(i) for i in range(concurrent_users)]
        all_results = await asyncio.gather(*user_tasks)
        total_time = time.time() - start_time
        
        flat_results = [result for user_results in all_results for result in user_results]
        successful_requests = len([r for r in flat_results if r["success"]])
        response_times = [r["response_time"] for r in flat_results if r["success"]]
        
        stats = {
            "service": service_name,
            "total_requests": len(flat_results),
            "successful_requests": successful_requests,
            "success_rate": successful_requests / len(flat_results),
            "total_time": total_time,
            "requests_per_second": len(flat_results) / total_time,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "median_response_time": statistics.median(response_times) if response_times else 0
        }
        
        self.results.append(stats)
        print(f"{service_name.title()} Service Results: {stats['requests_per_second']:.2f} RPS, {stats['success_rate']:.2%} success rate")
        return stats
    
    async def run_full_load_test(self):
        """Run comprehensive load test across all services"""
        print("🚀 Starting VedhaVriddhi Universal Financial Intelligence System Load Test")
        print("=" * 80)
        
        # Test all services
        await self.test_quantum_service(concurrent_users=25, requests_per_user=8)
        await self.test_agi_service(concurrent_users=20, requests_per_user=5)
        await self.test_consciousness_service(concurrent_users=15, requests_per_user=3)
        
        # Generate summary report
        print("\n" + "=" * 80)
        print("📊 LOAD TEST SUMMARY REPORT")
        print("=" * 80)
        
        for result in self.results:
            print(f"\n{result['service'].upper()} SERVICE:")
            print(f"  • Total Requests: {result['total_requests']:,}")
            print(f"  • Success Rate: {result['success_rate']:.2%}")
            print(f"  • Requests/Second: {result['requests_per_second']:.2f}")
            print(f"  • Avg Response Time: {result['avg_response_time']:.3f}s")
            print(f"  • Median Response Time: {result['median_response_time']:.3f}s")
        
        # Overall system performance
        total_requests = sum(r['total_requests'] for r in self.results)
        overall_success_rate = sum(r['successful_requests'] for r in self.results) / total_requests
        overall_rps = sum(r['requests_per_second'] for r in self.results)
        
        print(f"\n🎯 OVERALL SYSTEM PERFORMANCE:")
        print(f"  • Total Requests Processed: {total_requests:,}")
        print(f"  • Overall Success Rate: {overall_success_rate:.2%}")
        print(f"  • Combined Throughput: {overall_rps:.2f} RPS")
        print(f"  • System Status: {'✅ EXCELLENT' if overall_success_rate > 0.95 else '⚠️ NEEDS OPTIMIZATION'}")
        
        return self.results

async def main():
    """Run the load test"""
    tester = VedhaVriddhiLoadTester()
    results = await tester.run_full_load_test()
    
    # Save results to file
    with open('load_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Results saved to load_test_results.json")

if __name__ == "__main__":
    asyncio.run(main())
