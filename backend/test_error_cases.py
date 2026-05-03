import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 60)
print("TEST CASE CHO ENDPOINT /init")
print("=" * 60)

# Test Case 1: Graph ID không tồn tại
print("\n[TEST 1] Graph ID không tồn tại...")
response = requests.post(
    f"{BASE_URL}/init",
    json={
        "graph_id": 99999,
        "start_node": "A",
        "algorithm": "Dijkstra"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test Case 2: Start node không tồn tại
print("\n[TEST 2] Start node không tồn tại...")
response = requests.post(
    f"{BASE_URL}/init",
    json={
        "graph_id": 1,
        "start_node": "Z",  # Node không có trong graph
        "algorithm": "Dijkstra"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test Case 3: Thuật toán không hỗ trợ
print("\n[TEST 3] Thuật toán không hỗ trợ...")
response = requests.post(
    f"{BASE_URL}/init",
    json={
        "graph_id": 1,
        "start_node": "A",
        "algorithm": "BellmanFord"  # Chưa implement
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test Case 4: Request hợp lệ
print("\n[TEST 4] Request hợp lệ...")
response = requests.post(
    f"{BASE_URL}/init",
    json={
        "graph_id": 1,
        "start_node": "A",
        "algorithm": "Dijkstra"
    }
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

print("\n" + "=" * 60)