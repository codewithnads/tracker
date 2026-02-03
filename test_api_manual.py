import requests
import json

# API endpoint
BASE_URL = "http://localhost:5000"

# Test data - Payment of 181 rupees
test_payload = {
    "address": "+919876543210",
    "body": "Payment of 181 rupees to HDFC Account ending in 1234",
    "readable_date": "27-Jan-2026 19:30:00 PM",
    "refNo": "TXN123456789",
    "amount": 181,
    "type": "payment",
    "bank": "HDFC",
    "account": "1234",
    "description": "Test Payment"
}

headers = {
    "Content-Type": "application/json",
    "user": "Nadeem"
}

print("=" * 60)
print("🧪 TESTING TRACKER API - ADD PAYMENT RECORD")
print("=" * 60)

# Test 1: Root endpoint
print("\n✅ Test 1: Root Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Wake-up endpoint
print("\n✅ Test 2: Wake-up Endpoint")
print("-" * 60)
try:
    response = requests.get(f"{BASE_URL}/wake-up", timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Add payment record to Firebase
print("\n✅ Test 3: Add Payment Record (181 Rupees)")
print("-" * 60)
print(f"Payload: {json.dumps(test_payload, indent=2)}")
print()
try:
    response = requests.post(
        f"{BASE_URL}/add-record",
        json=test_payload,
        headers=headers,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Try to parse as JSON
    try:
        print(f"Parsed Response: {json.dumps(response.json(), indent=2)}")
    except:
        pass
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Retrieve records
print("\n✅ Test 4: Get Records (Authentication)")
print("-" * 60)
try:
    response = requests.get(
        f"{BASE_URL}/records",
        params={"uname": "nam", "key": "271016"},
        headers={"user": "Nadeem"},
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Records found: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Update records
print("\n✅ Test 5: Update Records")
print("-" * 60)
update_payload = {
    "HDFC~1234~TXN123456789": {
        "amount": 181,
        "description": "Test Payment Update",
        "status": "completed",
        "timestamp": "2026-01-27 19:30:00"
    }
}
print(f"Payload: {json.dumps(update_payload, indent=2)}")
print()
try:
    response = requests.post(
        f"{BASE_URL}/update-records",
        json=update_payload,
        headers=headers,
        timeout=10
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("✨ Testing Complete!")
print("=" * 60)
print("\n📝 Next Steps:")
print("1. Check Firebase Console: https://console.firebase.google.com")
print("2. Go to: tracker-851db > Firestore Database")
print("3. Look for collections: Nadeem > HDFC > 1234")
print("4. You should see the payment record with 181 rupees")
print("\n🔗 Firebase Console: https://console.firebase.google.com/project/tracker-851db")
