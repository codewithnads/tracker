#!/usr/bin/env python3
"""
Simple test script to add payment record to Firebase via the Tracker API
"""
import time
import requests
import json

time.sleep(2)  # Wait for server to start

BASE_URL = "http://localhost:5000"

# Test payment data - 181 rupees
payment_data = {
    "address": "+919876543210",
    "body": "Payment of 181 rupees to HDFC Account ending in 1234",
    "readable_date": "27-Jan-2026 19:30:00 PM",
    "refNo": "TXN123456789",
    "amount": 181,
    "type": "payment"
}

headers = {
    "Content-Type": "application/json",
    "user": "Nadeem"
}

print("\n" + "="*70)
print("🎯 ADDING PAYMENT RECORD TO FIREBASE")
print("="*70)

print(f"\n📤 Sending payment data...")
print(f"Amount: ₹181")
print(f"Account: HDFC ending in 1234")
print(f"Reference: TXN123456789")

try:
    response = requests.post(
        f"{BASE_URL}/add-record",
        json=payment_data,
        headers=headers,
        timeout=15
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n🎉 Payment record successfully added to Firebase!")
        print("\n📌 Next steps:")
        print("1. Open Firebase Console: https://console.firebase.google.com")
        print("2. Select project: tracker-851db")
        print("3. Go to Firestore Database")
        print("4. Navigate to: Nadeem > HDFC > 1234")
        print("5. You should see the payment record with 181 rupees")
    else:
        print(f"\n⚠️  Got status code {response.status_code}")
        print("Check Flask server logs for details")
        
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection Error: {e}")
    print("Make sure Flask server is running on port 5000")
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*70 + "\n")
