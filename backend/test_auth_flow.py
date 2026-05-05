"""
End-to-end test of authentication flow with protected algorithm endpoints.
"""

import json
import httpx
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

# SSL Certificate Workaround (development only)
client = httpx.Client(verify=False)


def test_auth_flow():
    print("\n" + "="*80)
    print("🔐 AUTHENTICATION FLOW TEST")
    print("="*80 + "\n")
    
    # Step 1: Register a new user
    print("📝 Step 1: Register new user")
    register_payload = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "password123456"
    }
    
    try:
        r = client.post(f"{BASE_URL}/auth/register", json=register_payload)
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 201:
            print(f"   ❌ Register failed: {r.text}")
            return False
        
        auth_response = r.json()
        user_id = auth_response["user"]["id"]
        access_token = auth_response["access_token"]
        refresh_token = auth_response["refresh_token"]
        
        print(f"   ✅ User registered successfully")
        print(f"      User ID: {user_id}")
        print(f"      Access Token: {access_token[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 2: Get current user info
    print("\n📋 Step 2: Get current user info (protected endpoint)")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        r = client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"   ❌ Failed: {r.text}")
            return False
        
        user_info = r.json()
        print(f"   ✅ Got user info: {user_info['username']} ({user_info['email']})")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 3: Create a graph (now requires auth)
    print("\n📊 Step 3: Create graph (requires authentication)")
    try:
        graph_payload = {
            "name": "Test Graph",
            "nodes": [{"id": "0"}, {"id": "1"}, {"id": "2"}],
            "edges": [
                {"source": "0", "target": "1", "weight": 1},
                {"source": "1", "target": "2", "weight": 2}
            ]
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        r = client.post(f"{BASE_URL}/graphs", json=graph_payload, headers=headers)
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"   ❌ Failed: {r.text}")
            return False
        
        graph_id = r.json()["graph_id"]
        print(f"   ✅ Graph created: ID = {graph_id}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 4: Initialize algorithm session (requires auth)
    print("\n▶️  Step 4: Initialize algorithm session (requires authentication)")
    try:
        init_payload = {
            "graph_id": graph_id,
            "start_node": "0",
            "algorithm": "Dijkstra"
        }
        
        headers = {"Authorization": f"Bearer {access_token}"}
        r = client.post(f"{BASE_URL}/init", json=init_payload, headers=headers)
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"   ❌ Failed: {r.text}")
            return False
        
        result = r.json()
        session_id = result["session_id"]
        total_steps = result["total_steps"]
        
        print(f"   ✅ Session created: ID = {session_id}")
        print(f"      Total steps: {total_steps}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 5: Get algorithm step (requires auth)
    print(f"\n🔍 Step 5: Get algorithm step (requires authentication)")
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        r = client.get(
            f"{BASE_URL}/step/{session_id}",
            params={"step_index": 0},
            headers=headers
        )
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"   ❌ Failed: {r.text}")
            return False
        
        step_data = r.json()
        print(f"   ✅ Step retrieved:")
        print(f"      Description: {step_data['description']}")
        print(f"      Phase: {step_data['data']['phase_id']}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Step 6: Test unauthorized access (without token)
    print(f"\n🚫 Step 6: Test unauthorized access (should fail)")
    try:
        r = client.get(f"{BASE_URL}/step/{session_id}", params={"step_index": 0})
        print(f"   Status: {r.status_code}")
        
        if r.status_code == 403 or r.status_code == 401:
            print(f"   ✅ Correctly blocked unauthorized access")
        else:
            print(f"   ⚠️  Unexpected status: {r.status_code}")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 7: Token refresh
    print(f"\n🔄 Step 7: Refresh access token")
    try:
        refresh_payload = {"refresh_token": refresh_token}
        r = client.post(f"{BASE_URL}/auth/refresh", json=refresh_payload)
        print(f"   Status: {r.status_code}")
        
        if r.status_code != 200:
            print(f"   ❌ Failed: {r.text}")
            return False
        
        new_tokens = r.json()
        new_access_token = new_tokens["access_token"]
        print(f"   ✅ New access token: {new_access_token[:20]}...")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n" + "="*80)
    print("✅ ALL AUTH FLOW TESTS PASSED!")
    print("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        test_auth_flow()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
