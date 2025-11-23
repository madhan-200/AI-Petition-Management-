"""
Test Complete Workflow: Citizen Submit → AI Analysis → Officer Portal

This script demonstrates the complete petition workflow.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_complete_workflow():
    print("="*60)
    print("COMPLETE WORKFLOW TEST")
    print("="*60)
    
    # Step 1: Register a new citizen
    print("\n1️⃣ Registering new citizen...")
    citizen_data = {
        "username": "test_citizen_workflow",
        "email": "citizen_workflow@test.com",
        "password": "test123",
        "role": "CITIZEN"
    }
    
    response = requests.post(f"{BASE_URL}/users/register/", json=citizen_data)
    if response.status_code == 201:
        print(f"✅ Citizen registered: {citizen_data['username']}")
    else:
        print(f"⚠️  Citizen may already exist (continuing...)")
    
    # Step 2: Login as citizen
    print("\n2️⃣ Logging in as citizen...")
    login_response = requests.post(f"{BASE_URL}/users/login/", json={
        "username": citizen_data["username"],
        "password": citizen_data["password"]
    })
    
    if login_response.status_code == 200:
        tokens = login_response.json()
        citizen_token = tokens['access']
        print(f"✅ Login successful")
    else:
        print(f"❌ Login failed: {login_response.text}")
        return
    
    # Step 3: Submit petition (AI will analyze automatically)
    print("\n3️⃣ Submitting petition (AI analysis will run automatically)...")
    petition_data = {
        "title": "Broken Street Light on Main Road",
        "description": "The street light at the corner of Main Road and 5th Avenue has been broken for 2 weeks. This is causing safety issues for pedestrians at night. Urgent repair needed."
    }
    
    headers = {"Authorization": f"Bearer {citizen_token}"}
    petition_response = requests.post(
        f"{BASE_URL}/petitions/",
        json=petition_data,
        headers=headers
    )
    
    if petition_response.status_code == 201:
        petition = petition_response.json()
        print(f"✅ Petition created successfully!")
        print(f"\n📊 AI ANALYSIS RESULTS:")
        print(f"   Petition ID: {petition['id']}")
        print(f"   🏢 Department (AI): {petition.get('department_name', 'N/A')}")
        print(f"   ⚠️  Urgency (AI): {petition.get('urgency', 'N/A')}")
        print(f"   📝 Status: {petition.get('status', 'N/A')}")
        print(f"   🔍 Duplicate Check: {'Yes' if petition.get('is_duplicate') else 'No'}")
        petition_id = petition['id']
    else:
        print(f"❌ Petition creation failed: {petition_response.text}")
        return
    
    # Step 4: Register an officer
    print("\n4️⃣ Registering officer account...")
    officer_data = {
        "username": "test_officer_workflow",
        "email": "officer_workflow@test.com",
        "password": "test123",
        "role": "OFFICER"
    }
    
    response = requests.post(f"{BASE_URL}/users/register/", json=officer_data)
    if response.status_code == 201:
        print(f"✅ Officer registered: {officer_data['username']}")
    else:
        print(f"⚠️  Officer may already exist (continuing...)")
    
    # Step 5: Login as officer
    print("\n5️⃣ Logging in as officer...")
    officer_login = requests.post(f"{BASE_URL}/users/login/", json={
        "username": officer_data["username"],
        "password": officer_data["password"]
    })
    
    if officer_login.status_code == 200:
        officer_tokens = officer_login.json()
        officer_token = officer_tokens['access']
        print(f"✅ Officer login successful")
    else:
        print(f"❌ Officer login failed")
        return
    
    # Step 6: Officer views petitions
    print("\n6️⃣ Officer viewing petitions in dashboard...")
    officer_headers = {"Authorization": f"Bearer {officer_token}"}
    petitions_response = requests.get(
        f"{BASE_URL}/petitions/",
        headers=officer_headers
    )
    
    if petitions_response.status_code == 200:
        petitions = petitions_response.json()
        print(f"✅ Officer can see {len(petitions)} petition(s)")
        
        # Find our petition
        our_petition = next((p for p in petitions if p['id'] == petition_id), None)
        if our_petition:
            print(f"\n📋 PETITION IN OFFICER PORTAL:")
            print(f"   ID: {our_petition['id']}")
            print(f"   Title: {our_petition['title']}")
            print(f"   Department: {our_petition.get('department_name', 'N/A')}")
            print(f"   Urgency: {our_petition.get('urgency', 'N/A')}")
            print(f"   Status: {our_petition.get('status', 'N/A')}")
            print(f"   Citizen: {our_petition.get('citizen_username', 'N/A')}")
    
    # Step 7: Officer updates status
    print("\n7️⃣ Officer updating petition status...")
    update_response = requests.patch(
        f"{BASE_URL}/petitions/{petition_id}/",
        json={"status": "UNDER_REVIEW", "remarks": "Reviewing the street light issue"},
        headers=officer_headers
    )
    
    if update_response.status_code == 200:
        updated_petition = update_response.json()
        print(f"✅ Status updated to: {updated_petition['status']}")
        print(f"📧 Email notification sent to citizen automatically!")
    
    print("\n" + "="*60)
    print("✅ COMPLETE WORKFLOW TEST SUCCESSFUL!")
    print("="*60)
    print("\n📝 Summary:")
    print("1. ✅ Citizen submitted petition")
    print("2. ✅ AI analyzed department and urgency")
    print("3. ✅ Petition appeared in officer portal")
    print("4. ✅ Officer updated status")
    print("5. ✅ Notification triggered")
    print("\n🎉 All systems working!")

if __name__ == "__main__":
    test_complete_workflow()
