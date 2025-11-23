import requests

BASE_URL = 'http://localhost:8000/api'

def test_api():
    # 1. Register
    print("Registering user...")
    reg_data = {
        'username': 'citizen1',
        'password': 'password123',
        'email': 'citizen1@example.com',
        'role': 'CITIZEN'
    }
    try:
        resp = requests.post(f'{BASE_URL}/users/register/', data=reg_data)
        print(f"Register: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Register failed (maybe already exists): {e}")

    # 2. Login
    print("Logging in...")
    login_data = {'username': 'citizen1', 'password': 'password123'}
    resp = requests.post(f'{BASE_URL}/users/login/', data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
    
    tokens = resp.json()
    access_token = tokens['access']
    print(f"Got token: {access_token[:20]}...")

    # 3. Create Petition
    print("Creating petition...")
    headers = {'Authorization': f'Bearer {access_token}'}
    petition_data = {
        'title': 'Test Petition',
        'description': 'This is a test petition description.',
        'urgency': 'LOW'
    }
    resp = requests.post(f'{BASE_URL}/petitions/', data=petition_data, headers=headers)
    print(f"Create Petition: {resp.status_code}")
    print(f"Response: {resp.json()}")

    # 4. List Petitions
    print("Listing petitions...")
    resp = requests.get(f'{BASE_URL}/petitions/', headers=headers)
    print(f"List Petitions: {resp.status_code} {resp.json()}")

if __name__ == '__main__':
    test_api()
