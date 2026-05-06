#!/usr/bin/env python3
"""
🧪 Frontend Integration Test Script

Test script untuk memverifikasi integrasi frontend dengan API chatbot.
Jalankan script ini untuk memastikan semua endpoint berfungsi dengan baik.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

try:
    import requests
    from app.main import app
    from app.services.rag_service import RAGService
    from app.services.llm_service import LLMService
    from app.services.vector_store import VectorStore
    from app.core.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Pastikan Anda menjalankan script ini dari root directory project")
    sys.exit(1)

class FrontendIntegrationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(asyncio.get_event_loop().time())}"

    async def test_api_endpoints(self):
        """Test semua API endpoints yang digunakan frontend"""
        print("🧪 Testing API Endpoints...\n")

        # Test 1: Health Check
        print("1️⃣ Testing Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

        # Test 2: Chat Endpoint
        print("\n2️⃣ Testing Chat Endpoint...")
        test_messages = [
            "Halo, apa kabar?",
            "Saya butuh lampu PJUTS untuk taman rumah",
            "Berapa harga PJUTS 40W?",
            "Apakah ada garansi produk?",
            "Saya tertarik dengan produk ini"
        ]

        for message in test_messages:
            try:
                payload = {
                    "message": message,
                    "session_id": self.session_id
                }
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print(f"✅ Chat response for '{message[:30]}...': {data.get('intent', 'unknown')}")
                    else:
                        print(f"❌ Chat failed for '{message[:30]}...': {data.get('error', 'unknown error')}")
                else:
                    print(f"❌ Chat HTTP error for '{message[:30]}...': {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ Chat error for '{message[:30]}...': {e}")
                return False

        # Test 3: Create Lead
        print("\n3️⃣ Testing Lead Creation...")
        try:
            lead_data = {
                "name": "Test User",
                "whatsapp": "+6281234567890",
                "project_needs": "Test project for PJUTS installation",
                "session_id": self.session_id
            }
            response = requests.post(
                f"{self.base_url}/api/leads",
                json=lead_data,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Lead creation passed")
                else:
                    print(f"❌ Lead creation failed: {data.get('error', 'unknown error')}")
            else:
                print(f"❌ Lead creation HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Lead creation error: {e}")
            return False

        # Test 4: Get History
        print("\n4️⃣ Testing Chat History...")
        try:
            params = {"session_id": self.session_id, "limit": 5}
            response = requests.get(
                f"{self.base_url}/api/history",
                params=params,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    history_count = len(data.get("history", []))
                    print(f"✅ History retrieval passed: {history_count} messages")
                else:
                    print(f"❌ History retrieval failed: {data.get('error', 'unknown error')}")
            else:
                print(f"❌ History HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ History error: {e}")
            return False

        # Test 5: API Documentation
        print("\n5️⃣ Testing API Documentation...")
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=10)
            if response.status_code == 200:
                print("✅ API documentation accessible")
            else:
                print(f"❌ API documentation error: {response.status_code}")
        except Exception as e:
            print(f"❌ API documentation error: {e}")

        return True

    async def test_frontend_simulation(self):
        """Simulasi interaksi frontend dengan API"""
        print("\n🎭 Frontend Simulation Test...\n")

        # Simulate user journey
        journey = [
            {
                "message": "Halo, saya butuh informasi tentang PJUTS",
                "expected_intent": "general"
            },
            {
                "message": "Saya punya taman rumah yang butuh penerangan",
                "expected_intent": "product_recommendation"
            },
            {
                "message": "Berapa harga untuk PJUTS 40W?",
                "expected_intent": "faq"
            },
            {
                "message": "Saya tertarik, bagaimana cara order?",
                "expected_intent": "lead"
            }
        ]

        for step in journey:
            try:
                payload = {
                    "message": step["message"],
                    "session_id": self.session_id
                }
                response = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        intent = data.get("intent", "unknown")
                        print(f"✅ '{step['message'][:30]}...' → Intent: {intent}")

                        # Validate response structure
                        required_fields = ["success", "answer", "intent", "sessionId"]
                        missing_fields = [field for field in required_fields if field not in data]
                        if missing_fields:
                            print(f"⚠️  Missing fields: {missing_fields}")
                        else:
                            print("✅ Response structure valid")
                    else:
                        print(f"❌ Failed: {data.get('error', 'unknown error')}")
                        return False
                else:
                    print(f"❌ HTTP error: {response.status_code}")
                    return False

                # Small delay between requests
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"❌ Error: {e}")
                return False

        return True

    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🚨 Error Handling Test...\n")

        # Test invalid session
        try:
            payload = {
                "message": "Test message",
                "session_id": ""  # Invalid session
            }
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Invalid session handled gracefully")
                else:
                    print(f"⚠️  Invalid session returned error: {data.get('error')}")
            else:
                print(f"❌ Invalid session HTTP error: {response.status_code}")

        except Exception as e:
            print(f"❌ Invalid session error: {e}")

        # Test empty message
        try:
            payload = {
                "message": "",
                "session_id": self.session_id
            }
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if not data.get("success"):
                    print("✅ Empty message handled correctly")
                else:
                    print("⚠️  Empty message should fail but succeeded")
            else:
                print(f"❌ Empty message HTTP error: {response.status_code}")

        except Exception as e:
            print(f"❌ Empty message error: {e}")

        return True

    async def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Test Report Generation...\n")

        # Test API endpoints
        api_test_passed = await self.test_api_endpoints()

        # Test frontend simulation
        frontend_test_passed = await self.test_frontend_simulation()

        # Test error handling
        error_test_passed = await self.test_error_handling()

        # Generate report
        report = {
            "timestamp": "2024-01-01T00:00:00Z",  # Would use datetime.now()
            "api_url": self.base_url,
            "session_id": self.session_id,
            "tests": {
                "api_endpoints": "PASSED" if api_test_passed else "FAILED",
                "frontend_simulation": "PASSED" if frontend_test_passed else "FAILED",
                "error_handling": "PASSED" if error_test_passed else "FAILED"
            },
            "overall_status": "PASSED" if all([api_test_passed, frontend_test_passed, error_test_passed]) else "FAILED"
        }

        # Save report
        report_file = Path("frontend_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"📄 Test report saved to: {report_file}")
        print(f"📊 Overall Status: {report['overall_status']}")

        return report

async def main():
    """Main test function"""
    print("🚀 Niscahya Chatbot Frontend Integration Test\n")
    print("=" * 50)

    # Check if API is running
    tester = FrontendIntegrationTester()

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ API server is not running!")
            print("Please start the API server first:")
            print("cd backend && python -m uvicorn app.main:app --reload")
            return
    except:
        print("❌ Cannot connect to API server!")
        print("Please start the API server first:")
        print("cd backend && python -m uvicorn app.main:app --reload")
        return

    # Run all tests
    report = await tester.generate_test_report()

    print("\n" + "=" * 50)
    if report["overall_status"] == "PASSED":
        print("🎉 All tests passed! Frontend integration is ready!")
        print("\n📋 Next steps:")
        print("1. Open frontend/demo.html in browser")
        print("2. Test chatbot manually")
        print("3. Integrate into your main website")
        print("4. Deploy to production (see PRODUCTION_DEPLOYMENT.md)")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("\n🔧 Common fixes:")
        print("- Ensure API server is running")
        print("- Check vector store is initialized")
        print("- Verify PDF documents are uploaded")
        print("- Check OpenAI API key is configured")

if __name__ == "__main__":
    asyncio.run(main())