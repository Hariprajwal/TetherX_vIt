"""
UrbanSecure AI-ZeroTrust — Comprehensive API Test Suite
Tests: Admin login, registration, OTP, RBAC, CRUD, AI, Blockchain
"""
import requests
import json
import sys
import subprocess

BASE = "http://localhost:8000"
PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} -- {detail}")

def h(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

print("=" * 60)
print("UrbanSecure API Test Suite")
print("=" * 60)

# 1. ADMIN LOGIN
print("\n[1] Admin Login (superuser)")
r = requests.post(f"{BASE}/api/auth/login/", json={"username": "admin", "password": "Admin@123"})
test("Admin login returns 200", r.status_code == 200, f"got {r.status_code}: {r.text[:200]}")
admin_data = r.json()
test("Admin gets access token", "access" in admin_data, str(admin_data.keys()))
test("Admin gets refresh token", "refresh" in admin_data)
test("Admin role is admin", admin_data.get("user", {}).get("role") == "admin", admin_data.get("user", {}).get("role"))
ADMIN_TOKEN = admin_data.get("access", "")

r = requests.get(f"{BASE}/api/auth/me/", headers=h(ADMIN_TOKEN))
test("Admin /me returns 200", r.status_code == 200, f"got {r.status_code}")
test("Admin /me role is admin", r.json().get("role") == "admin")

# 2. USER REGISTRATION
print("\n[2] User Registration")

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "hacker_admin", "email": "hack@evil.com",
    "password": "Test@1234", "password_confirm": "Test@1234", "role": "admin"
})
test("Cannot register as admin", r.status_code == 400, f"got {r.status_code}")

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "test_viewer", "email": "viewer@test.com",
    "password": "View@1234", "password_confirm": "View@1234", "role": "viewer"
})
test("Register viewer returns 201", r.status_code == 201, f"got {r.status_code}: {r.text[:200]}")

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "test_engineer", "email": "eng@test.com",
    "password": "Eng@12345", "password_confirm": "Eng@12345", "role": "Engineer"
})
test("Register engineer returns 201", r.status_code == 201, f"got {r.status_code}: {r.text[:200]}")

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "test_municipal", "email": "muni@test.com",
    "password": "Muni@1234", "password_confirm": "Muni@1234", "role": "Municipal"
})
test("Register municipal returns 201", r.status_code == 201, f"got {r.status_code}: {r.text[:200]}")

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "test_viewer", "email": "other@test.com",
    "password": "View@1234", "password_confirm": "View@1234", "role": "viewer"
})
test("Duplicate username rejected", r.status_code == 400)

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "another_user", "email": "viewer@test.com",
    "password": "View@1234", "password_confirm": "View@1234", "role": "viewer"
})
test("Duplicate email rejected", r.status_code == 400)

r = requests.post(f"{BASE}/api/auth/register/", json={
    "username": "weakpw_user", "email": "weak@test.com",
    "password": "weak", "password_confirm": "weak", "role": "viewer"
})
test("Weak password rejected", r.status_code == 400)

# 3. UNVERIFIED USER LOGIN
print("\n[3] Unverified User Login")
r = requests.post(f"{BASE}/api/auth/login/", json={"username": "test_viewer", "password": "View@1234"})
test("Unverified login returns 403", r.status_code == 403, f"got {r.status_code}")
test("Response has needs_verification", r.json().get("needs_verification") == True)

# 4. VERIFY USERS VIA ORM
print("\n[4] OTP Verification (via Django ORM)")
verify_script = """
import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'urbanSecurity_pro.settings'
django.setup()
from urbanSecurity_app.models import User
for u in ['test_viewer', 'test_engineer', 'test_municipal']:
    user = User.objects.get(username=u)
    user.is_verified = True
    user.save()
    print(f'Verified: {u}')
"""
result = subprocess.run(
    [sys.executable, "-c", verify_script],
    capture_output=True, text=True, cwd=r"e:\TetherX\urbanSecurity_pro"
)
test("Users verified via ORM", "Verified: test_viewer" in result.stdout, result.stderr[:200] if result.stderr else result.stdout)

# 5. VERIFIED USER LOGINS
print("\n[5] Verified User Logins")
tokens = {}
for uname, pw, expected_role in [
    ("test_viewer", "View@1234", "viewer"),
    ("test_engineer", "Eng@12345", "Engineer"),
    ("test_municipal", "Muni@1234", "Municipal"),
]:
    r = requests.post(f"{BASE}/api/auth/login/", json={"username": uname, "password": pw})
    test(f"{uname} login 200", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")
    data = r.json()
    test(f"{uname} role is {expected_role}", data.get("user", {}).get("role", "").lower() == expected_role.lower(), data.get("user", {}).get("role"))
    tokens[uname] = data.get("access", "")

VIEWER_T = tokens.get("test_viewer", "")
ENGINEER_T = tokens.get("test_engineer", "")
MUNICIPAL_T = tokens.get("test_municipal", "")

# 6. RBAC - Access Logs
print("\n[6] RBAC - Access Logs")

r = requests.post(f"{BASE}/api/access-logs/", headers=h(ADMIN_TOKEN), json={
    "user_identifier": "admin_sensor", "endpoint": "/api/test", "method": "GET", "role": "admin"
})
test("Admin create access log", r.status_code == 201, f"got {r.status_code}: {r.text[:100]}")
admin_log_id = r.json().get("id")

r = requests.post(f"{BASE}/api/access-logs/", headers=h(ENGINEER_T), json={
    "user_identifier": "eng_device", "endpoint": "/api/sensor", "method": "POST", "role": "Engineer"
})
test("Engineer create access log", r.status_code == 201, f"got {r.status_code}")

r = requests.post(f"{BASE}/api/access-logs/", headers=h(VIEWER_T), json={
    "user_identifier": "viewer_try", "endpoint": "/api/test", "method": "GET", "role": "viewer"
})
test("Viewer CANNOT create access log", r.status_code == 403, f"got {r.status_code}")

r = requests.get(f"{BASE}/api/access-logs/", headers=h(ADMIN_TOKEN))
admin_log_count = len(r.json())
test("Admin sees all logs", admin_log_count >= 2, f"got {admin_log_count}")

r = requests.get(f"{BASE}/api/access-logs/", headers=h(VIEWER_T))
viewer_log_count = len(r.json())
test("Viewer sees only own logs", viewer_log_count < admin_log_count, f"viewer={viewer_log_count}, admin={admin_log_count}")

r = requests.delete(f"{BASE}/api/access-logs/{admin_log_id}/", headers=h(VIEWER_T))
test("Viewer CANNOT delete log", r.status_code == 403, f"got {r.status_code}")

r = requests.delete(f"{BASE}/api/access-logs/{admin_log_id}/", headers=h(ADMIN_TOKEN))
test("Admin CAN delete log", r.status_code == 204, f"got {r.status_code}")

# 7. RBAC - Audit Logs
print("\n[7] RBAC - Audit Logs")

r = requests.post(f"{BASE}/api/audit-logs/", headers=h(ADMIN_TOKEN), json={
    "action": "test_action", "actor": "admin", "details": "Testing audit"
})
test("Admin create audit log", r.status_code == 201, f"got {r.status_code}: {r.text[:100]}")
test("Audit log has block_hash", "block_hash" in r.json() and r.json()["block_hash"] and len(r.json()["block_hash"]) == 64)

r = requests.post(f"{BASE}/api/audit-logs/", headers=h(VIEWER_T), json={
    "action": "viewer_try", "actor": "viewer", "details": "Should be denied"
})
test("Viewer CANNOT create audit", r.status_code == 403, f"got {r.status_code}")

# 8. RBAC - ABAC Policies
print("\n[8] RBAC - ABAC Policies")

r = requests.post(f"{BASE}/api/abac-policies/", headers=h(ADMIN_TOKEN), json={
    "name": "Test Night Block", "description": "Block viewer at night",
    "role": "viewer", "attribute": "time_of_day", "condition": ">= 22",
    "action": "deny", "is_active": True, "priority": 100
})
test("Admin create ABAC policy", r.status_code == 201, f"got {r.status_code}: {r.text[:100]}")
policy_id = r.json().get("id")

r = requests.post(f"{BASE}/api/abac-policies/", headers=h(ENGINEER_T), json={
    "name": "Eng Policy", "role": "viewer", "attribute": "ip", "condition": "blocked", "action": "deny"
})
test("Engineer CANNOT create policy", r.status_code == 403, f"got {r.status_code}")

r = requests.delete(f"{BASE}/api/abac-policies/{policy_id}/", headers=h(MUNICIPAL_T))
test("Municipal CANNOT delete policy", r.status_code == 403, f"got {r.status_code}")

r = requests.delete(f"{BASE}/api/abac-policies/{policy_id}/", headers=h(ADMIN_TOKEN))
test("Admin CAN delete policy", r.status_code == 204, f"got {r.status_code}")

# 9. AI - Adapt Role
print("\n[9] AI - Adapt Role (LSTM)")

r = requests.post(f"{BASE}/api/adapt-role/", headers=h(ADMIN_TOKEN), json={
    "context": [0.9, 0.3, 0.8, 0.5, 0.1], "user_identifier": "engineer_01", "current_role": "viewer"
})
test("Admin run adapt-role", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")
test("Returns recommended_role", "recommended_role" in r.json(), str(r.json().keys()))
print(f"      AI recommended: {r.json().get('recommended_role')} (source: {'edge' if r.json().get('from_edge') else 'local'})")

r = requests.post(f"{BASE}/api/adapt-role/", headers=h(VIEWER_T), json={
    "context": [0.5, 0.5, 0.5, 0.5, 0.5], "user_identifier": "test", "current_role": "viewer"
})
test("Viewer CANNOT use adapt-role", r.status_code == 403, f"got {r.status_code}")

# 10. AI - Anomaly Detection
print("\n[10] AI - Anomaly Detection")

r = requests.post(f"{BASE}/api/anomaly-detect/", headers=h(ENGINEER_T), json={
    "input_vector": [0.95, 0.88, 0.1, 0.99, 0.05], "user_identifier": "sensor_42"
})
test("Engineer run anomaly detect", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")
test("Returns is_anomalous", "is_anomalous" in r.json())
print(f"      Result: {'ANOMALY' if r.json().get('is_anomalous') else 'NORMAL'} (score: {r.json().get('anomaly_score')})")

r = requests.post(f"{BASE}/api/anomaly-detect/", headers=h(VIEWER_T), json={
    "input_vector": [0.5, 0.5, 0.5, 0.5, 0.5], "user_identifier": "test"
})
test("Viewer CANNOT use anomaly detect", r.status_code == 403, f"got {r.status_code}")

# 11. Blockchain Verify
print("\n[11] Blockchain Verify")

r = requests.get(f"{BASE}/api/blockchain-verify/", headers=h(ADMIN_TOKEN))
test("Blockchain GET chain", r.status_code == 200, f"got {r.status_code}")
test("Chain has blocks", r.json().get("chain_length", 0) > 0, f"length={r.json().get('chain_length')}")
print(f"      Chain length: {r.json().get('chain_length')}")

r = requests.post(f"{BASE}/api/blockchain-verify/", headers=h(ADMIN_TOKEN))
test("Blockchain verify POST", r.status_code == 200, f"got {r.status_code}")
test("Chain is valid", r.json().get("is_valid") == True, r.json().get("verification"))
print(f"      Verification: {r.json().get('verification')}")

r = requests.get(f"{BASE}/api/blockchain-verify/", headers=h(VIEWER_T))
test("Viewer CAN verify blockchain", r.status_code == 200, f"got {r.status_code}")

# 12. Username/Email Check
print("\n[12] Username/Email Availability")

r = requests.get(f"{BASE}/api/auth/check-username/?username=admin")
test("Admin username is taken", r.json().get("available") == False)

r = requests.get(f"{BASE}/api/auth/check-username/?username=new_unique_user")
test("New username available", r.json().get("available") == True)

r = requests.get(f"{BASE}/api/auth/check-email/?email=viewer@test.com")
test("Registered email taken", r.json().get("available") == False)

# 13. Password Change
print("\n[13] Password Change")

r = requests.post(f"{BASE}/api/auth/change-password/", headers=h(ENGINEER_T), json={
    "current_password": "Eng@12345", "new_password": "NewEng@9876", "new_password_confirm": "NewEng@9876"
})
test("Engineer change password", r.status_code == 200, f"got {r.status_code}: {r.text[:100]}")

r = requests.post(f"{BASE}/api/auth/login/", json={"username": "test_engineer", "password": "NewEng@9876"})
test("Login with new password", r.status_code == 200, f"got {r.status_code}")

# SUMMARY
print("\n" + "=" * 60)
print(f"RESULTS: {PASS} passed, {FAIL} failed, {PASS + FAIL} total")
print("=" * 60)
if FAIL == 0:
    print("ALL TESTS PASSED!")
else:
    print(f"{FAIL} test(s) failed")
