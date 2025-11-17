"""
Simple test script for the QA API
"""
import asyncio
import httpx
import json


async def test_api():
    #Test the API endpoints
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test health endpoint
        print("Testing /health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"✓ Health check: {response.json()}")
        except Exception as e:
            print(f"✗ Health check failed: {e}")
            return
        
        # Test root endpoint
        print("\nTesting / endpoint...")
        try:
            response = await client.get(f"{base_url}/")
            print(f"✓ Root endpoint: {response.status_code}")
        except Exception as e:
            print(f"✗ Root endpoint failed: {e}")
        
        # Test /ask endpoint
        print("\nTesting /ask endpoint...")
        test_questions = [
            "When is Layla planning her trip to London?",
            "How many cars does Vikram Desai have?",
            "What are Amira's favorite restaurants?",
        ]
        
        for question in test_questions:
            try:
                response = await client.post(
                    f"{base_url}/ask",
                    json={"question": question}
                )
                result = response.json()
                print(f"\nQuestion: {question}")
                print(f"Answer: {result.get('answer', 'No answer')}")
            except Exception as e:
                print(f"✗ Failed to ask question '{question}': {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Member Data QA API")
    print("=" * 60)
    print("\nMake sure the server is running: python main.py")
    print("=" * 60)
    asyncio.run(test_api())

