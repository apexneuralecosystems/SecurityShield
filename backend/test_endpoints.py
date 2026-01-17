#!/usr/bin/env python3
"""Test script to verify all API endpoints work correctly"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoints():
    """Test all endpoints"""
    print("=" * 60)
    print("Testing ShieldOps API Endpoints")
    print("=" * 60)
    
    # Test data
    test_email = "test@example.com"
    test_password = "testpassword123"
    test_name = "Test User"
    
    results = []
    
    # 1. Test Signup (should work)
    print("\n1. Testing POST /auth/signup")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": test_email,
                "password": test_password,
                "full_name": test_name
            }
        )
        if response.status_code == 201:
            print("✅ Signup successful")
            results.append(("Signup", True))
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  User already exists (this is OK)")
            results.append(("Signup", True))
        else:
            print(f"❌ Signup failed: {response.status_code} - {response.text}")
            results.append(("Signup", False))
    except Exception as e:
        print(f"❌ Signup error: {e}")
        results.append(("Signup", False))
    
    # 2. Test Login (should work)
    print("\n2. Testing POST /auth/login")
    token = None
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_email,
                "password": test_password
            }
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print("✅ Login successful, token received")
                results.append(("Login", True))
            else:
                print("❌ Login successful but no token")
                results.append(("Login", False))
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            results.append(("Login", False))
    except Exception as e:
        print(f"❌ Login error: {e}")
        results.append(("Login", False))
    
    if not token:
        print("\n⚠️  Cannot continue testing protected endpoints without token")
        print_summary(results)
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Test Get Current User (should work with token)
    print("\n3. Testing GET /auth/me")
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ Get current user successful")
            results.append(("Get Current User", True))
        else:
            print(f"❌ Get current user failed: {response.status_code} - {response.text}")
            results.append(("Get Current User", False))
    except Exception as e:
        print(f"❌ Get current user error: {e}")
        results.append(("Get Current User", False))
    
    # 4. Test Landing Page Data (should work with or without token)
    print("\n4. Testing GET /landing-page-data (with token)")
    try:
        response = requests.get(f"{BASE_URL}/landing-page-data", headers=headers)
        if response.status_code == 200:
            print("✅ Landing page data (authenticated) successful")
            results.append(("Landing Page Data (Auth)", True))
        else:
            print(f"❌ Landing page data failed: {response.status_code} - {response.text}")
            results.append(("Landing Page Data (Auth)", False))
    except Exception as e:
        print(f"❌ Landing page data error: {e}")
        results.append(("Landing Page Data (Auth)", False))
    
    # 5. Test Landing Page Data without token (should work)
    print("\n5. Testing GET /landing-page-data (without token)")
    try:
        response = requests.get(f"{BASE_URL}/landing-page-data")
        if response.status_code == 200:
            print("✅ Landing page data (unauthenticated) successful")
            results.append(("Landing Page Data (No Auth)", True))
        else:
            print(f"❌ Landing page data failed: {response.status_code} - {response.text}")
            results.append(("Landing Page Data (No Auth)", False))
    except Exception as e:
        print(f"❌ Landing page data error: {e}")
        results.append(("Landing Page Data (No Auth)", False))
    
    # 6. Test Create Website (should work with token)
    print("\n6. Testing POST /websites")
    website_id = None
    try:
        response = requests.post(
            f"{BASE_URL}/websites",
            headers=headers,
            json={
                "url": "https://example.com",
                "name": "Example Site",
                "description": "Test website"
            }
        )
        if response.status_code == 201:
            data = response.json()
            website_id = data.get("id")
            print(f"✅ Create website successful (ID: {website_id})")
            results.append(("Create Website", True))
        else:
            print(f"❌ Create website failed: {response.status_code} - {response.text}")
            results.append(("Create Website", False))
    except Exception as e:
        print(f"❌ Create website error: {e}")
        results.append(("Create Website", False))
    
    # 7. Test Get Websites (should work with token)
    print("\n7. Testing GET /websites")
    try:
        response = requests.get(f"{BASE_URL}/websites", headers=headers)
        if response.status_code == 200:
            websites = response.json()
            print(f"✅ Get websites successful ({len(websites)} websites)")
            results.append(("Get Websites", True))
        else:
            print(f"❌ Get websites failed: {response.status_code} - {response.text}")
            results.append(("Get Websites", False))
    except Exception as e:
        print(f"❌ Get websites error: {e}")
        results.append(("Get Websites", False))
    
    # 8. Test Get Website by ID (should work with token)
    if website_id:
        print(f"\n8. Testing GET /websites/{website_id}")
        try:
            response = requests.get(f"{BASE_URL}/websites/{website_id}", headers=headers)
            if response.status_code == 200:
                print("✅ Get website by ID successful")
                results.append(("Get Website by ID", True))
            else:
                print(f"❌ Get website by ID failed: {response.status_code} - {response.text}")
                results.append(("Get Website by ID", False))
        except Exception as e:
            print(f"❌ Get website by ID error: {e}")
            results.append(("Get Website by ID", False))
    
    # 9. Test Create Scan (should work with token)
    if website_id:
        print(f"\n9. Testing POST /scans")
        scan_id = None
        try:
            response = requests.post(
                f"{BASE_URL}/scans",
                headers=headers,
                json={
                    "website_id": website_id,
                    "scan_type": "quick"
                }
            )
            if response.status_code == 201:
                data = response.json()
                scan_id = data.get("id")
                print(f"✅ Create scan successful (ID: {scan_id})")
                results.append(("Create Scan", True))
            else:
                print(f"❌ Create scan failed: {response.status_code} - {response.text}")
                results.append(("Create Scan", False))
        except Exception as e:
            print(f"❌ Create scan error: {e}")
            results.append(("Create Scan", False))
    
    # 10. Test Get Scans (should work with token)
    print("\n10. Testing GET /scans")
    try:
        response = requests.get(f"{BASE_URL}/scans", headers=headers)
        if response.status_code == 200:
            scans = response.json()
            print(f"✅ Get scans successful ({len(scans)} scans)")
            results.append(("Get Scans", True))
        else:
            print(f"❌ Get scans failed: {response.status_code} - {response.text}")
            results.append(("Get Scans", False))
    except Exception as e:
        print(f"❌ Get scans error: {e}")
        results.append(("Get Scans", False))
    
    # 11. Test Get Summary (should work with token)
    print("\n11. Testing GET /summary")
    try:
        response = requests.get(f"{BASE_URL}/summary", headers=headers)
        if response.status_code == 200:
            print("✅ Get summary successful")
            results.append(("Get Summary", True))
        else:
            print(f"❌ Get summary failed: {response.status_code} - {response.text}")
            results.append(("Get Summary", False))
    except Exception as e:
        print(f"❌ Get summary error: {e}")
        results.append(("Get Summary", False))
    
    # 12. Test Get Issues (should work with token)
    print("\n12. Testing GET /issues")
    try:
        response = requests.get(f"{BASE_URL}/issues", headers=headers)
        if response.status_code == 200:
            issues = response.json()
            print(f"✅ Get issues successful ({len(issues)} issues)")
            results.append(("Get Issues", True))
        else:
            print(f"❌ Get issues failed: {response.status_code} - {response.text}")
            results.append(("Get Issues", False))
    except Exception as e:
        print(f"❌ Get issues error: {e}")
        results.append(("Get Issues", False))
    
    # Print summary
    print_summary(results)

def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, status in results if status)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print("\nDetailed Results:")
    for name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {name}")
    print("=" * 60)

if __name__ == "__main__":
    test_endpoints()

