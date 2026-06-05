"""
AstraNotes — 50 User Scenario Tests
Runs against a live server at BASE_URL.
Usage: python app/tests/scenario_tests.py
"""
import sys
import time
import random
import string
import requests

BASE_URL = "http://127.0.0.1:8001"

# Use a unique suffix each run to avoid conflicts with leftover DB data
_suffix = "".join(random.choices(string.ascii_lowercase, k=6))
ALICE = f"alice_{_suffix}"
BOB   = f"bob_{_suffix}"

# ── helpers ──────────────────────────────────────────────────────────────────

PASS = "\033[32m✅ PASS\033[0m"
FAIL = "\033[31m❌ FAIL\033[0m"

results = []


def check(num: int, desc: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    line = f"[{num:02d}] {status}  {desc}"
    if detail:
        line += f"\n       → {detail}"
    print(line)
    results.append(passed)


def register(username, password):
    return requests.post(f"{BASE_URL}/auth/register",
                         json={"username": username, "password": password})


def login(username, password):
    return requests.post(f"{BASE_URL}/auth/login",
                         json={"username": username, "password": password})


def token_header(token):
    return {"Authorization": f"Bearer {token}"}


def safe_json(r):
    try:
        return r.json()
    except Exception:
        return {}


def create_note(token, title, body=None, visibility="public", tags=None):
    payload = {"title": title, "visibility": visibility}
    if body is not None:
        payload["body"] = body
    if tags is not None:
        payload["tags"] = tags
    return requests.post(f"{BASE_URL}/notes/",
                         json=payload, headers=token_header(token))


def list_notes(token, tags=None):
    params = {}
    if tags:
        params["tags"] = tags
    return requests.get(f"{BASE_URL}/notes/",
                        headers=token_header(token), params=params)


def get_note(token, note_id):
    return requests.get(f"{BASE_URL}/notes/{note_id}",
                        headers=token_header(token))


def update_note(token, note_id, **kwargs):
    return requests.patch(f"{BASE_URL}/notes/{note_id}",
                          json=kwargs, headers=token_header(token))


def delete_note(token, note_id):
    return requests.delete(f"{BASE_URL}/notes/{note_id}",
                           headers=token_header(token))


# ── wait for server ───────────────────────────────────────────────────────────

print("\n--- Waiting for server ---")
for _ in range(20):
    try:
        requests.get(f"{BASE_URL}/health", timeout=1)
        print("Server ready.\n")
        break
    except Exception:
        time.sleep(0.5)
else:
    print("Server did not start in time. Exiting.")
    sys.exit(1)

# ════════════════════════════════════════════════════════════════════════════
print("--- Section 1: User Registration & Authentication (1~10) ---")
# ════════════════════════════════════════════════════════════════════════════

# 1. Alice registers successfully
r = register(ALICE, "securepass123")
alice_token = safe_json(r).get("access_token", "") if r.status_code == 201 else ""
check(1, f"Alice({ALICE}) register → 201 + access_token", r.status_code == 201 and bool(alice_token))

# 2. Bob registers successfully
r = register(BOB, "bobpass456")
bob_token = safe_json(r).get("access_token", "") if r.status_code == 201 else ""
check(2, f"Bob({BOB}) register → 201 + access_token", r.status_code == 201 and bool(bob_token))

# 3. Duplicate username → 400
r = register(ALICE, "anotherpass")
check(3, "Duplicate username register → 400 Bad Request", r.status_code == 400,
      safe_json(r).get("detail", ""))

# 4. Alice logs in with correct password → 200 + token
r = login(ALICE, "securepass123")
alice_token2 = safe_json(r).get("access_token", "") if r.status_code == 200 else ""
check(4, "Alice correct password login → 200 + token", r.status_code == 200 and bool(alice_token2))
alice_token = alice_token2

# 5. Alice logs in with wrong password → 401
r = login(ALICE, "wrongpassword")
check(5, "Wrong password login → 401 Unauthorized", r.status_code == 401,
      safe_json(r).get("detail", ""))

# 6. Non-existent user login → 401
r = login("ghost_user_xyz", "anypass")
check(6, "Non-existent user login → 401 Unauthorized", r.status_code == 401,
      safe_json(r).get("detail", ""))

# 7. No token accessing /notes/ → 401
r = requests.get(f"{BASE_URL}/notes/")
check(7, "No token GET /notes/ → 401", r.status_code == 401,
      f"got {r.status_code}")

# 8. Invalid token accessing /notes/ → 401
r = requests.get(f"{BASE_URL}/notes/",
                 headers={"Authorization": "Bearer invalid.jwt.token"})
check(8, "Invalid token GET /notes/ → 401", r.status_code == 401,
      f"got {r.status_code}")

# 9. Empty username → 422 Validation Error
r = register("", "somepass")
check(9, "Empty username register → 422 Validation Error", r.status_code == 422,
      f"got {r.status_code}")

# 10. Empty password → 422 Validation Error
r = register("newuser", "")
check(10, "Empty password register → 422 Validation Error", r.status_code == 422,
      f"got {r.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 2: Create Notes (11~18) ---")
# ════════════════════════════════════════════════════════════════════════════

# 11. Alice creates a public note
r = create_note(alice_token, "Alice Public Note", "Hello world", "public")
alice_pub_id = r.json().get("id", "") if r.status_code == 201 else ""
check(11, "Alice creates public note → 201", r.status_code == 201 and bool(alice_pub_id),
      f"id={alice_pub_id}")

# 12. Alice creates a private note
r = create_note(alice_token, "Alice Private Note", "Secret content", "private")
alice_priv_id = r.json().get("id", "") if r.status_code == 201 else ""
check(12, "Alice creates private note → 201", r.status_code == 201 and bool(alice_priv_id),
      f"id={alice_priv_id}")

# 13. Alice creates a tagged note
r = create_note(alice_token, "Alice Tagged Note", "Python content",
                "public", tags=["Python", "AI"])
alice_tagged_id = r.json().get("id", "") if r.status_code == 201 else ""
check(13, "Alice creates note with tags=[Python, AI] → 201",
      r.status_code == 201 and bool(alice_tagged_id),
      f"tags={r.json().get('tags', [])}")

# 14. Bob creates a public note
r = create_note(bob_token, "Bob Public Note", "Bob says hello", "public")
bob_pub_id = r.json().get("id", "") if r.status_code == 201 else ""
check(14, "Bob creates public note → 201", r.status_code == 201 and bool(bob_pub_id))

# 15. Bob creates a private note
r = create_note(bob_token, "Bob Private Note", "Bob secret", "private")
bob_priv_id = r.json().get("id", "") if r.status_code == 201 else ""
check(15, "Bob creates private note → 201", r.status_code == 201 and bool(bob_priv_id))

# 16. Empty title → 422
r = create_note(alice_token, "", "body content")
check(16, "Empty title → 422", r.status_code == 422,
      f"got {r.status_code}")

# 17. Whitespace-only title → 422/400
r = create_note(alice_token, "   ", "body content")
check(17, "Whitespace-only title → 422/400 (whitespace validation)",
      r.status_code in (400, 422),
      f"got {r.status_code}: {r.json()}")

# 18. No body (optional field) → 201
r = create_note(alice_token, "Note Without Body")
check(18, "No body (optional) → 201", r.status_code == 201,
      f"got {r.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 3: List Notes (19~26) ---")
# ════════════════════════════════════════════════════════════════════════════

# 19. Alice lists notes: sees own public + private
r = list_notes(alice_token)
alice_list = safe_json(r).get("notes", []) if r.status_code == 200 else []
alice_ids_in_list = [n["id"] for n in alice_list]
check(19, "Alice list: sees own public + private notes",
      alice_pub_id in alice_ids_in_list and alice_priv_id in alice_ids_in_list,
      f"total={safe_json(r).get('total', 0)}")

# 20. Alice list: sees Bob's public note
check(20, "Alice list: sees Bob's public note",
      bob_pub_id in alice_ids_in_list,
      f"bob_pub_id={'found' if bob_pub_id in alice_ids_in_list else 'missing'}")

# 21. Alice list: cannot see Bob's private note
check(21, "Alice list: cannot see Bob's private note",
      bob_priv_id not in alice_ids_in_list,
      f"bob_priv_id={'hidden (correct)' if bob_priv_id not in alice_ids_in_list else 'EXPOSED (bug)'}")

# 22. Bob list: cannot see Alice's private note
r = list_notes(bob_token)
bob_list = r.json().get("notes", []) if r.status_code == 200 else []
bob_ids_in_list = [n["id"] for n in bob_list]
check(22, "Bob list: cannot see Alice's private note",
      alice_priv_id not in bob_ids_in_list,
      f"alice_priv_id={'hidden (correct)' if alice_priv_id not in bob_ids_in_list else 'EXPOSED (bug)'}")

# 23. Tag filter [Python]: returns only notes with that tag
r = list_notes(alice_token, tags=["Python"])
tagged_ids = [n["id"] for n in r.json().get("notes", [])]
check(23, "Tag filter [Python]: returns only matching notes",
      alice_tagged_id in tagged_ids and bob_pub_id not in tagged_ids,
      f"matched={len(tagged_ids)} note(s)")

# 24. Non-existent tag → empty list
r = list_notes(alice_token, tags=["NonExistentTag99"])
check(24, "Non-existent tag filter → empty list",
      r.json().get("total", -1) == 0,
      f"total={r.json().get('total')}")

# 25. Tag is case-sensitive: 'python' != 'Python'
r = list_notes(alice_token, tags=["python"])
check(25, "Tag case-sensitive: 'python' does not match 'Python'",
      alice_tagged_id not in [n["id"] for n in r.json().get("notes", [])],
      f"matched={r.json().get('total', 0)}")

# 26. Unauthenticated access to /notes/ → 401
r = requests.get(f"{BASE_URL}/notes/")
check(26, "Unauthenticated GET /notes/ → 401", r.status_code == 401)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 4: Get Note by ID (27~32) ---")
# ════════════════════════════════════════════════════════════════════════════

# 27. Alice gets her own public note → 200
r = get_note(alice_token, alice_pub_id)
check(27, "Alice gets own public note by ID → 200",
      r.status_code == 200 and r.json().get("id") == alice_pub_id)

# 28. Alice gets her own private note → 200
r = get_note(alice_token, alice_priv_id)
check(28, "Alice gets own private note by ID → 200",
      r.status_code == 200 and r.json().get("id") == alice_priv_id)

# 29. Bob gets Alice's public note → 200
r = get_note(bob_token, alice_pub_id)
check(29, "Bob gets Alice's public note by ID → 200", r.status_code == 200)

# 30. Bob gets Alice's private note → 403
r = get_note(bob_token, alice_priv_id)
check(30, "Bob gets Alice's private note by ID → 403 Access Denied",
      r.status_code == 403, r.json().get("detail", ""))

# 31. Non-existent note ID → 404
r = get_note(alice_token, "00000000-0000-0000-0000-000000000000")
check(31, "Non-existent note_id → 404", r.status_code == 404)

# 32. No token get note → 401
r = requests.get(f"{BASE_URL}/notes/{alice_pub_id}")
check(32, "No token GET note by ID → 401", r.status_code == 401)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 5: Update Notes (33~39) ---")
# ════════════════════════════════════════════════════════════════════════════

# 33. Alice updates her note title → 200
r = update_note(alice_token, alice_pub_id, title="Alice Public Note (Updated)")
check(33, "Alice updates own note title → 200",
      r.status_code == 200 and "Updated" in r.json().get("title", ""),
      f"new title: {r.json().get('title', '')}")

# 34. Alice updates her note body → 200
r = update_note(alice_token, alice_pub_id, body="Updated body content")
check(34, "Alice updates own note body → 200",
      r.status_code == 200 and r.json().get("body") == "Updated body content")

# 35. Alice makes public note private → 200
r = update_note(alice_token, alice_pub_id, visibility="private")
check(35, "Alice sets note to private → 200",
      r.status_code == 200 and r.json().get("visibility") == "private")

# 36. Alice makes private note public → 200
r = update_note(alice_token, alice_pub_id, visibility="public")
check(36, "Alice sets note back to public → 200",
      r.status_code == 200 and r.json().get("visibility") == "public")

# 37. Bob tries to update Alice's note → 403
r = update_note(bob_token, alice_pub_id, title="Hacked!")
check(37, "Bob tries to update Alice's note → 403 Access Denied",
      r.status_code == 403, r.json().get("detail", ""))

# 38. Update to whitespace-only title → 422/400
r = update_note(alice_token, alice_pub_id, title="   ")
check(38, "Update to whitespace-only title → 422/400",
      r.status_code in (400, 422),
      f"got {r.status_code}")

# 39. Update non-existent note → 404
r = update_note(alice_token, "00000000-0000-0000-0000-000000000000", title="Ghost")
check(39, "Update non-existent note → 404", r.status_code == 404)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 6: Delete Notes (40~45) ---")
# ════════════════════════════════════════════════════════════════════════════

# Create a temporary note for deletion tests
r = create_note(alice_token, "Alice Temp Note To Delete", "will be deleted")
alice_del_id = r.json().get("id", "") if r.status_code == 201 else ""

# 40. Bob tries to delete Alice's note → 403
r = delete_note(bob_token, alice_del_id)
check(40, "Bob tries to delete Alice's note → 403", r.status_code == 403)

# 41. Alice deletes her own note → 204
r = delete_note(alice_token, alice_del_id)
check(41, "Alice deletes own note → 204 No Content", r.status_code == 204)

# 42. Deleted note is gone → 404
r = get_note(alice_token, alice_del_id)
check(42, "Deleted note GET → 404", r.status_code == 404)

# 43. Delete same note again → 404
r = delete_note(alice_token, alice_del_id)
check(43, "Delete already-deleted note → 404", r.status_code == 404)

# 44. Alice deletes her own private note → 204
r = create_note(alice_token, "Alice Private To Delete", "secret", "private")
del_priv_id = r.json().get("id", "") if r.status_code == 201 else ""
r = delete_note(alice_token, del_priv_id)
check(44, "Alice deletes own private note → 204", r.status_code == 204)

# 45. Bob deletes his own note → 204
r = create_note(bob_token, "Bob Note To Delete", "bye")
bob_del_id = r.json().get("id", "") if r.status_code == 201 else ""
r = delete_note(bob_token, bob_del_id)
check(45, "Bob deletes own note → 204", r.status_code == 204)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 7: Privacy Isolation & Visibility Toggle (46~50) ---")
# ════════════════════════════════════════════════════════════════════════════

# 46. Alice makes note private → disappears from Bob's list
r = update_note(alice_token, alice_pub_id, visibility="private")
r2 = list_notes(bob_token)
bob_ids = [n["id"] for n in safe_json(r2).get("notes", [])]
check(46, "Alice note set private → disappears from Bob's list",
      r.status_code == 200 and alice_pub_id not in bob_ids,
      f"update={r.status_code} hidden={'yes' if alice_pub_id not in bob_ids else 'NO (bug)'}")

# 47. Alice note now private → Bob gets 403 by ID
r = get_note(bob_token, alice_pub_id)
check(47, "Alice note private → Bob GET by ID → 403",
      r.status_code == 403, f"got {r.status_code}")

# 48. Alice makes note public again → reappears in Bob's list
r = update_note(alice_token, alice_pub_id, visibility="public")
r2 = list_notes(bob_token)
bob_ids = [n["id"] for n in safe_json(r2).get("notes", [])]
check(48, "Alice note set public again → reappears in Bob's list",
      r.status_code == 200 and alice_pub_id in bob_ids,
      f"update={r.status_code} visible={'yes' if alice_pub_id in bob_ids else 'NO (bug)'}")

# 49. Alice always sees her own private notes in list
r = list_notes(alice_token)
alice_ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(49, "Alice always sees own private note in her list",
      alice_priv_id in alice_ids,
      f"private note {'visible' if alice_priv_id in alice_ids else 'MISSING (bug)'}")

# 50. Bob's private note: invisible to Alice in list + 403 by ID
r1 = list_notes(alice_token)
alice_ids = [n["id"] for n in safe_json(r1).get("notes", [])]
r2 = get_note(alice_token, bob_priv_id)
check(50, "Bob private note: not in Alice's list AND 403 by ID",
      bob_priv_id not in alice_ids and r2.status_code == 403,
      f"list hidden={'yes' if bob_priv_id not in alice_ids else 'NO'}  ID={r2.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Summary ---")
# ════════════════════════════════════════════════════════════════════════════
passed = sum(results)
total = len(results)
failed = total - passed
print(f"\nTotal: {total} scenarios")
print(f"  \033[32m✅ Passed: {passed}\033[0m")
if failed:
    print(f"  \033[31m❌ Failed: {failed}\033[0m")
else:
    print("  All scenarios passed!")

failed_nums = [i + 1 for i, r in enumerate(results) if not r]
if failed_nums:
    print(f"\nFailed scenario numbers: {failed_nums}")

sys.exit(0 if failed == 0 else 1)
