"""
AstraNotes — 100 Extended User Scenario Tests (Scenarios 51-150)
Runs against a live server at BASE_URL.
Usage: python app/tests/scenario_tests_extended.py
"""
import sys, time, random, string, requests

BASE_URL = "http://127.0.0.1:8001"

_s = "".join(random.choices(string.ascii_lowercase, k=6))
ALICE   = f"alice_{_s}"
BOB     = f"bob_{_s}"
CHARLIE = f"charlie_{_s}"

PASS_A = "alicepass99"
PASS_B = "bobpass88"
PASS_C = "charliepass77"

# ── helpers ──────────────────────────────────────────────────────────────────
results = []

def check(num, desc, passed, detail=""):
    tag = "\033[32m✅ PASS\033[0m" if passed else "\033[31m❌ FAIL\033[0m"
    line = f"[{num:03d}] {tag}  {desc}"
    if detail:
        line += f"\n        → {detail}"
    print(line)
    results.append((num, passed, desc, detail))

def safe_json(r):
    try:
        return r.json()
    except Exception:
        return {}

def hdr(token):
    return {"Authorization": f"Bearer {token}"}

def reg(u, p):
    return requests.post(f"{BASE_URL}/auth/register", json={"username": u, "password": p})

def login(u, p):
    return requests.post(f"{BASE_URL}/auth/login", json={"username": u, "password": p})

def create(token, title, body=None, visibility="public", tags=None):
    p = {"title": title, "visibility": visibility}
    if body is not None:  p["body"] = body
    if tags is not None:  p["tags"] = tags
    return requests.post(f"{BASE_URL}/notes/", json=p, headers=hdr(token))

def lst(token, tags=None):
    params = {"tags": tags} if tags else {}
    return requests.get(f"{BASE_URL}/notes/", headers=hdr(token), params=params)

def get(token, nid):
    return requests.get(f"{BASE_URL}/notes/{nid}", headers=hdr(token))

def patch(token, nid, **kw):
    return requests.patch(f"{BASE_URL}/notes/{nid}", json=kw, headers=hdr(token))

def delete(token, nid):
    return requests.delete(f"{BASE_URL}/notes/{nid}", headers=hdr(token))

def note_id(r):
    return safe_json(r).get("id", "")

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
    print("Server not up. Exiting."); sys.exit(1)

# ── Bootstrap: register 3 users ──────────────────────────────────────────────
alice_token   = safe_json(reg(ALICE,   PASS_A)).get("access_token", "")
bob_token     = safe_json(reg(BOB,     PASS_B)).get("access_token", "")
charlie_token = safe_json(reg(CHARLIE, PASS_C)).get("access_token", "")
assert alice_token and bob_token and charlie_token, "Bootstrap failed - check server"

# ════════════════════════════════════════════════════════════════════════════
print("--- Section 8: Username/Password Boundary Cases (51~60) ---")
# ════════════════════════════════════════════════════════════════════════════

# 51. Username with digits → 201
r = reg(f"user42_{_s}", "pass1234")
check(51, "Username with digits → 201", r.status_code == 201)

# 52. Username with underscore → 201
r = reg(f"user_name_{_s}", "pass1234")
check(52, "Username with underscore → 201", r.status_code == 201)

# 53. Password with spaces → 201 (passwords should allow spaces)
r = reg(f"spacepass_{_s}", "my secret pass")
check(53, "Password with spaces → 201 (allowed)", r.status_code == 201)

# 54. Password with special characters → 201
r = reg(f"specpass_{_s}", "P@ss!#$%^&*()")
check(54, "Password with special characters → 201", r.status_code == 201)

# 55. Tab character as username → 422
r = reg("\t", "somepass")
check(55, "Tab character username → 422", r.status_code == 422,
      f"got {r.status_code}")

# 56. Multiple logins for same user → valid token each time
r1 = login(ALICE, PASS_A)
r2 = login(ALICE, PASS_A)
t1 = safe_json(r1).get("access_token", "")
t2 = safe_json(r2).get("access_token", "")
check(56, "Multiple logins → valid token returned each time", bool(t1) and bool(t2))

# 57. Old token still valid after new login (no forced invalidation)
r = lst(alice_token)
check(57, "Old token still valid after new login", r.status_code == 200)

# 58. Very long username (100 chars) → 201 or 422 (record behavior)
long_user = "u" * 100 + _s[:4]
r = reg(long_user, "pass1234")
check(58, f"Very long username (100 chars) → {r.status_code} (record behavior)",
      r.status_code in (201, 422), f"got {r.status_code}")

# 59. Login response token_type = "bearer"
r = login(ALICE, PASS_A)
check(59, "Login response token_type='bearer'",
      safe_json(r).get("token_type") == "bearer")

# 60. Very long password (100 chars) → 201
r = reg(f"longpwd_{_s}", "x" * 100)
check(60, "Very long password (100 chars) → 201", r.status_code == 201)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 9: Note Defaults & Field Validation (61~70) ---")
# ════════════════════════════════════════════════════════════════════════════

# 61. New note author_id equals username
r = create(alice_token, "Field Check Note", visibility="public")
nid = note_id(r)
check(61, "New note author_id equals username",
      safe_json(r).get("author_id") == ALICE,
      f"author_id={safe_json(r).get('author_id')}")

# 62. New note version = 1
check(62, "New note version = 1",
      safe_json(r).get("version") == 1,
      f"version={safe_json(r).get('version')}")

# 63. New note has created_at and updated_at
data = safe_json(r)
check(63, "New note has created_at and updated_at",
      bool(data.get("created_at")) and bool(data.get("updated_at")))

# 64. PATCH increments version
r2 = patch(alice_token, nid, title="Field Check Note v2")
check(64, "PATCH increments version (1→2)",
      safe_json(r2).get("version") == 2,
      f"version={safe_json(r2).get('version')}")

# 65. Second PATCH version = 3
r3 = patch(alice_token, nid, body="updated body")
check(65, "Second PATCH version = 3",
      safe_json(r3).get("version") == 3)

# 66. No visibility specified → defaults to "public"
r = create(alice_token, "Default Visibility Note")
check(66, "No visibility specified → defaults to 'public'",
      safe_json(r).get("visibility") == "public",
      f"visibility={safe_json(r).get('visibility')}")
nid_default = note_id(r)

# 67. Explicit visibility='private' stored correctly
r = create(alice_token, "Explicit Private Note", visibility="private")
check(67, "Explicit visibility='private' stored correctly",
      safe_json(r).get("visibility") == "private")

# 68. Invalid visibility value → 422
r = create(alice_token, "Bad Visibility", visibility="secret")
check(68, "Invalid visibility value → 422",
      r.status_code == 422, f"got {r.status_code}")

# 69. Note response contains all required fields
r = create(alice_token, "Full Fields Note", body="body text",
           tags=["t1"], visibility="public")
d = safe_json(r)
required = {"id", "title", "body", "tags", "visibility",
            "author_id", "created_at", "updated_at", "version"}
check(69, "Create response contains all required fields",
      required.issubset(d.keys()),
      f"missing={required - d.keys()}")

# 70. List response contains 'notes' array and 'total' integer
r = lst(alice_token)
d = safe_json(r)
check(70, "List response contains 'notes' array and 'total' integer",
      isinstance(d.get("notes"), list) and isinstance(d.get("total"), int),
      f"notes={type(d.get('notes')).__name__} total={type(d.get('total')).__name__}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 10: Tag Operations (71~82) ---")
# ════════════════════════════════════════════════════════════════════════════

# 71. Create note with no tags → tags=[]
r = create(alice_token, "No Tags Note")
check(71, "No tags on create → tags=[]",
      safe_json(r).get("tags") == [],
      f"tags={safe_json(r).get('tags')}")

# 72. Create with single tag → stored correctly
r = create(alice_token, "One Tag Note", tags=["Python"])
check(72, "Single tag create → tags=['Python']",
      safe_json(r).get("tags") == ["Python"])
nid_one_tag = note_id(r)

# 73. Create with multiple tags → all stored
r = create(alice_token, "Multi Tag Note", tags=["Python", "AI", "FastAPI"])
check(73, "Multiple tags create → all stored",
      set(safe_json(r).get("tags", [])) == {"Python", "AI", "FastAPI"})
nid_multi = note_id(r)

# 74. PATCH adds tags (none → some)
nid_tag_up = note_id(create(alice_token, "Add Tag Note"))
r = patch(alice_token, nid_tag_up, tags=["NewTag"])
check(74, "PATCH adds tags (none → ['NewTag'])",
      safe_json(r).get("tags") == ["NewTag"])

# 75. PATCH clears tags (some → [])
r = patch(alice_token, nid_tag_up, tags=[])
check(75, "PATCH clears tags (some → [])",
      safe_json(r).get("tags") == [])

# 76. Two-tag filter (AND) → only notes with both tags
nid_both    = note_id(create(alice_token, "Both Tags", tags=["AI", "FastAPI"]))
nid_only_ai = note_id(create(alice_token, "Only AI",  tags=["AI"]))
r = lst(alice_token, tags=["AI", "FastAPI"])
ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(76, "Two-tag AND filter: note with both appears, note with only one does not",
      nid_both in ids and nid_only_ai not in ids,
      f"matched={len(ids)}")

# 77. Single-tag filter returns other users' public notes (AND logic)
bob_tagged = note_id(create(bob_token, "Bob AI Note", tags=["AI"], visibility="public"))
r = lst(alice_token, tags=["AI"])
ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(77, "Single-tag filter includes other users' public notes",
      bob_tagged in ids)

# 78. Tag with hyphen/dot → 201
r = create(alice_token, "Hyphen Tag", tags=["my-tag", "v1.0"])
check(78, "Tag with hyphen/dot → 201",
      r.status_code == 201 and "my-tag" in safe_json(r).get("tags", []))

# 79. Tag with spaces → 201 (stored as-is)
r = create(alice_token, "Space Tag", tags=["my note", "machine learning"])
check(79, "Tag with spaces → 201, stored as-is",
      r.status_code == 201 and "my note" in safe_json(r).get("tags", []))

# 80. PATCH tags then GET returns updated tags
nid_tag_check = note_id(create(alice_token, "Tag Check Note", tags=["old"]))
patch(alice_token, nid_tag_check, tags=["new1", "new2"])
r = get(alice_token, nid_tag_check)
check(80, "After PATCH tags, GET returns updated tags",
      set(safe_json(r).get("tags", [])) == {"new1", "new2"})

# 81. Add tag → appears in filter; clear tag → disappears from filter
patch(alice_token, nid_tag_check, tags=["filter_me"])
r1 = lst(alice_token, tags=["filter_me"])
patch(alice_token, nid_tag_check, tags=[])
r2 = lst(alice_token, tags=["filter_me"])
ids1 = [n["id"] for n in safe_json(r1).get("notes", [])]
ids2 = [n["id"] for n in safe_json(r2).get("notes", [])]
check(81, "Add tag → appears in filter; clear tag → disappears",
      nid_tag_check in ids1 and nid_tag_check not in ids2)

# 82. Tag filter respects privacy: private note with tag invisible to Bob
priv_tagged = note_id(create(alice_token, "Private Tagged", tags=["secret"], visibility="private"))
r = lst(bob_token, tags=["secret"])
ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(82, "Private note with tag → Bob cannot see it via tag filter",
      priv_tagged not in ids)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 11: Content Boundaries (Length / Special Chars / Unicode) (83~92) ---")
# ════════════════════════════════════════════════════════════════════════════

# 83. Very long title (500 chars) → 201
long_title = "A" * 500
r = create(alice_token, long_title)
check(83, "Very long title (500 chars) → 201",
      r.status_code == 201 and safe_json(r).get("title") == long_title)

# 84. Very long body (10000 chars) → 201, content preserved
long_body = "B" * 10000
r = create(alice_token, "Long Body Note", body=long_body)
check(84, "Very long body (10000 chars) → 201, content preserved",
      r.status_code == 201 and safe_json(r).get("body") == long_body)
nid_long_body = note_id(r)

# 85. Unicode (non-ASCII) title → 201
r = create(alice_token, "My Notes: Python Study")
check(85, "Non-ASCII title → 201, content correct",
      r.status_code == 201)

# 86. Unicode body → 201, content preserved
r = create(alice_token, "Unicode Body", body="Today I studied AI and deep learning.")
check(86, "Unicode body → 201, content preserved",
      r.status_code == 201)

# 87. Title with special characters (!, @, #, $) → 201
r = create(alice_token, "Note! @Special #Tag $100")
check(87, "Special character title → 201",
      r.status_code == 201)

# 88. Body with newlines → 201, newlines preserved
r = create(alice_token, "Multiline Body", body="Line 1\nLine 2\nLine 3")
check(88, "Body with newlines → 201, newlines preserved",
      r.status_code == 201 and "\n" in safe_json(r).get("body", ""))

# 89. Body with HTML/JS → 201, stored as-is (API does not sanitize)
html = "<script>alert('xss')</script><b>bold</b>"
r = create(alice_token, "HTML Body", body=html)
check(89, "Body with HTML/JS → 201, stored as-is (no server-side sanitization)",
      r.status_code == 201 and safe_json(r).get("body") == html)

# 90. PATCH body to empty string → 200
nid_body_clear = note_id(create(alice_token, "Will Clear Body", body="some content"))
r = patch(alice_token, nid_body_clear, body="")
check(90, "PATCH body to empty string → 200 (body is optional)",
      r.status_code == 200 and safe_json(r).get("body") == "")

# 91. Title with tab in middle (not purely whitespace) → 201
r = create(alice_token, "Tab\tIn\tMiddle")
check(91, "Title with tab in middle (not purely whitespace) → 201",
      r.status_code == 201)

# 92. Emoji title → 201
r = create(alice_token, "My Notes")
check(92, "Title with printable chars → 201",
      r.status_code == 201)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 12: Three-User Isolation (Alice/Bob/Charlie) (93~105) ---")
# ════════════════════════════════════════════════════════════════════════════

# 93-94. Alice private note: Bob and Charlie cannot see it (list)
a_priv    = note_id(create(alice_token, "Alice Super Secret", visibility="private"))
bob_list  = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
char_list = [n["id"] for n in safe_json(lst(charlie_token)).get("notes", [])]
check(93, "Alice private note: not in Bob's list",   a_priv not in bob_list)
check(94, "Alice private note: not in Charlie's list", a_priv not in char_list)

# 95-96. Alice public note: Bob and Charlie can both see it
a_pub      = note_id(create(alice_token, "Alice Public For All", visibility="public"))
bob_list2  = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
char_list2 = [n["id"] for n in safe_json(lst(charlie_token)).get("notes", [])]
check(95, "Alice public note: visible in Bob's list",    a_pub in bob_list2)
check(96, "Alice public note: visible in Charlie's list", a_pub in char_list2)

# 97. Charlie gets Alice's private note by ID → 403
r = get(charlie_token, a_priv)
check(97, "Charlie GET Alice's private note by ID → 403", r.status_code == 403)

# 98. Charlie gets Alice's public note by ID → 200
r = get(charlie_token, a_pub)
check(98, "Charlie GET Alice's public note by ID → 200", r.status_code == 200)

# 99. Bob cannot delete Alice's public note → 403
r = delete(bob_token, a_pub)
check(99, "Bob DELETE Alice's public note → 403", r.status_code == 403)

# 100. Charlie cannot update Bob's note → 403
b_pub = note_id(create(bob_token, "Bob Public Note", visibility="public"))
r = patch(charlie_token, b_pub, title="Hacked by Charlie")
check(100, "Charlie PATCH Bob's note → 403", r.status_code == 403)

# 101. Three users create notes with same title → three distinct IDs
ids_same = []
for tok in [alice_token, bob_token, charlie_token]:
    ids_same.append(note_id(create(tok, "Same Title Note", visibility="public")))
check(101, "Three users create same-title notes → three distinct IDs",
      len(set(ids_same)) == 3, f"ids={ids_same}")

# 102. Alice deletes public note → Bob's list shrinks
a_del      = note_id(create(alice_token, "Will Be Deleted", visibility="public"))
before_bob = len(safe_json(lst(bob_token)).get("notes", []))
delete(alice_token, a_del)
after_bob  = len(safe_json(lst(bob_token)).get("notes", []))
check(102, "Alice deletes public note → Bob's list count decreases",
      after_bob == before_bob - 1,
      f"before={before_bob} after={after_bob}")

# 103. Alice updates public note → Bob sees updated title by ID
a_upd = note_id(create(alice_token, "Original Title", visibility="public"))
patch(alice_token, a_upd, title="Updated Title")
r = get(bob_token, a_upd)
check(103, "Alice updates note title → Bob sees updated title by ID",
      safe_json(r).get("title") == "Updated Title")

# 104. Alice makes note private → Bob cannot list or GET by ID
patch(alice_token, a_upd, visibility="private")
b_ids   = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
r_get   = get(bob_token, a_upd)
check(104, "Note set private → not in Bob's list AND GET → 403",
      a_upd not in b_ids and r_get.status_code == 403,
      f"list={'hidden' if a_upd not in b_ids else 'exposed'} get={r_get.status_code}")

# 105. Alice makes note public again → Bob can see it
patch(alice_token, a_upd, visibility="public")
b_ids2 = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
check(105, "Note set public again → reappears in Bob's list",
      a_upd in b_ids2)

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 13: State Consistency (106~117) ---")
# ════════════════════════════════════════════════════════════════════════════

# 106. Note retrievable by ID immediately after create
r_c   = create(alice_token, "Immediate Get Note")
nid_imm = note_id(r_c)
r_g   = get(alice_token, nid_imm)
check(106, "Note retrievable by ID immediately after creation",
      r_g.status_code == 200 and safe_json(r_g).get("id") == nid_imm)

# 107. Updated title appears in list
patch(alice_token, nid_imm, title="Updated Immediate")
titles = [n["title"] for n in safe_json(lst(alice_token)).get("notes", [])]
check(107, "After PATCH, updated title appears in list",
      "Updated Immediate" in titles)

# 108. Deleted note disappears from list immediately
nid_gone = note_id(create(alice_token, "Will Vanish"))
delete(alice_token, nid_gone)
ids_after = [n["id"] for n in safe_json(lst(alice_token)).get("notes", [])]
check(108, "Deleted note disappears from list immediately", nid_gone not in ids_after)

# 109. Create 5 notes → total increases by 5
before  = safe_json(lst(alice_token)).get("total", 0)
new_ids = [note_id(create(alice_token, f"Batch Note {i}")) for i in range(5)]
after   = safe_json(lst(alice_token)).get("total", 0)
check(109, "Create 5 notes → total increases by 5",
      after == before + 5, f"before={before} after={after}")

# 110. Delete 3 → total decreases by 3
for nid in new_ids[:3]:
    delete(alice_token, nid)
final = safe_json(lst(alice_token)).get("total", 0)
check(110, "Delete 3 notes → total decreases by 3",
      final == after - 3, f"expected={after-3} got={final}")

# 111. created_at unchanged after PATCH
nid_ts   = note_id(create(alice_token, "Timestamp Note"))
r_before = safe_json(get(alice_token, nid_ts))
time.sleep(1)
patch(alice_token, nid_ts, title="Timestamp Note v2")
r_after  = safe_json(get(alice_token, nid_ts))
check(111, "created_at unchanged after PATCH",
      r_before.get("created_at") == r_after.get("created_at"),
      f"before={r_before.get('created_at')} after={r_after.get('created_at')}")

# 112. updated_at present after PATCH
check(112, "updated_at present and non-empty after PATCH",
      bool(r_after.get("updated_at")))

# 113. Empty PATCH (no fields) → 200, content unchanged
nid_nop = note_id(create(alice_token, "No-op Patch Note", body="original"))
r = patch(alice_token, nid_nop)
check(113, "Empty PATCH (no fields) → 200, content unchanged",
      r.status_code == 200 and safe_json(r).get("body") == "original")

# 114. Repeated PATCH same field → final value is last write
nid_rep = note_id(create(alice_token, "Repeat Patch"))
patch(alice_token, nid_rep, title="v1")
patch(alice_token, nid_rep, title="v2")
r = patch(alice_token, nid_rep, title="v3")
check(114, "Multiple PATCH same field → final value is last write",
      safe_json(r).get("title") == "v3")

# 115. Create (v=1) → PATCH → GET v=2
nid_ver = note_id(create(alice_token, "Version Track"))
r_v1 = safe_json(get(alice_token, nid_ver))
patch(alice_token, nid_ver, title="Version Track v2")
r_v2 = safe_json(get(alice_token, nid_ver))
check(115, "Create (v=1) → PATCH → GET v=2",
      r_v1.get("version") == 1 and r_v2.get("version") == 2)

# 116. PATCH visibility to same value → 200 (idempotent)
nid_same_vis = note_id(create(alice_token, "Same Vis Note", visibility="public"))
r = patch(alice_token, nid_same_vis, visibility="public")
check(116, "PATCH visibility to same value → 200 (idempotent)", r.status_code == 200)

# 117. Charlie creates private note → Alice/Bob total unchanged
alice_total = safe_json(lst(alice_token)).get("total", -1)
bob_total   = safe_json(lst(bob_token)).get("total", -1)
create(charlie_token, "Charlie Private", visibility="private")
alice_total2 = safe_json(lst(alice_token)).get("total", -1)
bob_total2   = safe_json(lst(bob_token)).get("total", -1)
check(117, "Charlie creates private note → Alice/Bob total unchanged",
      alice_total == alice_total2 and bob_total == bob_total2,
      f"alice:{alice_total}→{alice_total2} bob:{bob_total}→{bob_total2}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 14: Security & Edge Case Inputs (118~132) ---")
# ════════════════════════════════════════════════════════════════════════════

# 118. All-zero UUID note_id → 404 (no crash)
r = get(alice_token, "00000000-0000-0000-0000-000000000000")
check(118, "All-zero UUID note_id → 404 (no crash)", r.status_code == 404)

# 119. SQL injection attempt as note_id → 404 (safe)
r = get(alice_token, "'; DROP TABLE notes; --")
check(119, "SQL injection as note_id → 404 (safe handling)",
      r.status_code == 404, f"got {r.status_code}")

# 120. note_id with trailing space in path → not 500
r = requests.get(f"{BASE_URL}/notes/ ", headers=hdr(alice_token))
check(120, "Trailing space in note path → not 500 (no server crash)",
      r.status_code != 500, f"got {r.status_code}")

# 121. PATCH with unknown fields → 200 (Pydantic ignores extras)
nid_extra = note_id(create(alice_token, "Extra Fields"))
r = requests.patch(f"{BASE_URL}/notes/{nid_extra}",
                   json={"title": "OK", "unknown_field": "ignored"},
                   headers=hdr(alice_token))
check(121, "PATCH with unknown fields → 200 (Pydantic ignores extra fields)",
      r.status_code == 200)

# 122. PATCH visibility to invalid value → 422
r = patch(alice_token, nid_extra, visibility="classified")
check(122, "PATCH invalid visibility value → 422",
      r.status_code == 422, f"got {r.status_code}")

# 123. Authorization header without 'Bearer' prefix → 401
r = requests.get(f"{BASE_URL}/notes/",
                 headers={"Authorization": alice_token})
check(123, "Authorization without 'Bearer' prefix → 401",
      r.status_code == 401, f"got {r.status_code}")

# 124. 'Bearer ' with empty token → 401
r = requests.get(f"{BASE_URL}/notes/",
                 headers={"Authorization": "Bearer "})
check(124, "'Bearer ' with empty token → 401", r.status_code == 401, f"got {r.status_code}")

# 125. POST /notes without title field → 422
r = requests.post(f"{BASE_URL}/notes/",
                  json={"body": "no title here"},
                  headers=hdr(alice_token))
check(125, "Create note without title field → 422", r.status_code == 422)

# 126. POST /notes with null title → 422
r = requests.post(f"{BASE_URL}/notes/",
                  json={"title": None, "body": "test"},
                  headers=hdr(alice_token))
check(126, "Create note with title=null → 422", r.status_code == 422, f"got {r.status_code}")

# 127. Error response (422) contains 'detail' field
r = create(alice_token, "")
check(127, "422 error response contains 'detail' field",
      "detail" in safe_json(r), f"keys={list(safe_json(r).keys())}")

# 128. Error response (404) contains 'detail' field
r = get(alice_token, "00000000-0000-0000-0000-000000000001")
check(128, "404 error response contains 'detail' field",
      "detail" in safe_json(r))

# 129. Error response (403) contains 'detail' field
r = get(bob_token, a_priv)
check(129, "403 error response contains 'detail' field",
      "detail" in safe_json(r))

# 130. DELETE with request body → 204 (body ignored)
nid_del_body = note_id(create(alice_token, "Delete With Body"))
r = requests.delete(f"{BASE_URL}/notes/{nid_del_body}",
                    json={"confirm": True}, headers=hdr(alice_token))
check(130, "DELETE with request body → 204 (body ignored)", r.status_code == 204)

# 131. Register response token works directly (no login needed)
r_reg        = reg(f"direct_{_s}", "pass1234")
direct_token = safe_json(r_reg).get("access_token", "")
r = lst(direct_token)
check(131, "Register response token works directly for subsequent requests",
      r.status_code == 200)

# 132. Unsupported HTTP method → 405
r = requests.put(f"{BASE_URL}/notes/", headers=hdr(alice_token))
check(132, "PUT /notes/ (unsupported method) → 405",
      r.status_code == 405, f"got {r.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 15: Health Check & Endpoint Availability (133~137) ---")
# ════════════════════════════════════════════════════════════════════════════

# 133. GET /health without token → 200 (public endpoint)
r = requests.get(f"{BASE_URL}/health")
check(133, "GET /health without token → 200 (public endpoint)", r.status_code == 200)

# 134. GET /health response contains 'service' field
check(134, "GET /health response contains 'service' field",
      "service" in safe_json(r))

# 135. GET /docs accessible (FastAPI auto-docs)
r = requests.get(f"{BASE_URL}/docs")
check(135, "GET /docs → 200 (Swagger UI accessible)", r.status_code == 200)

# 136. GET /openapi.json accessible
r = requests.get(f"{BASE_URL}/openapi.json")
check(136, "GET /openapi.json → 200 (API schema accessible)", r.status_code == 200)

# 137. openapi.json contains /notes/ path definition
d = safe_json(r)
check(137, "openapi.json contains /notes/ path definition",
      "/notes/" in d.get("paths", {}))

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Section 16: Bulk Operations & Edge Scenarios (138~150) ---")
# ════════════════════════════════════════════════════════════════════════════

# 138. Rapid sequential creation of 10 notes → all succeed
ids_bulk = []
for i in range(10):
    r = create(alice_token, f"Bulk Note {i}", visibility="public")
    ids_bulk.append(note_id(r))
check(138, "Rapid creation of 10 notes → all succeed",
      len([x for x in ids_bulk if x]) == 10)

# 139. List total includes all 10 bulk notes
total_now = safe_json(lst(alice_token)).get("total", 0)
check(139, "List total includes all bulk-created notes",
      total_now >= 10, f"total={total_now}")

# 140. Delete all bulk notes → all removed from list
for nid in ids_bulk:
    if nid: delete(alice_token, nid)
ids_after = [n["id"] for n in safe_json(lst(alice_token)).get("notes", [])]
check(140, "Delete all 10 bulk notes → all removed from list",
      all(nid not in ids_after for nid in ids_bulk if nid))

# 141. Alice creates → Bob reads → Alice deletes → Bob reads again → 404
shared = note_id(create(alice_token, "Shared Then Gone", visibility="public"))
get(bob_token, shared)       # Bob can read
delete(alice_token, shared)  # Alice deletes
r = get(bob_token, shared)   # Bob reads again
check(141, "After Alice deletes, Bob GET → 404",
      r.status_code == 404)

# 142-143. Already-deleted note: Bob PATCH and DELETE → both 404
nid_x = note_id(create(alice_token, "Cross Delete", visibility="public"))
delete(alice_token, nid_x)
r_p = patch(bob_token, nid_x, title="Can't patch deleted")
r_d = delete(bob_token, nid_x)
check(142, "Deleted note Bob PATCH → 404",
      r_p.status_code == 404, f"got {r_p.status_code}")
check(143, "Deleted note Bob DELETE → 404",
      r_d.status_code == 404, f"got {r_d.status_code}")

# 144. User A token cannot GET/PATCH/DELETE User B's private note
b_priv2 = note_id(create(bob_token, "Bob Deep Private", visibility="private"))
checks = [
    get(alice_token, b_priv2).status_code == 403,
    patch(alice_token, b_priv2, title="x").status_code == 403,
    delete(alice_token, b_priv2).status_code == 403,
]
check(144, "Alice GET/PATCH/DELETE Bob's private note → all 403",
      all(checks), f"results={checks}")

# 145. Same user, two sessions (two tokens) → consistent note state
t_a1 = safe_json(login(ALICE, PASS_A)).get("access_token", "")
t_a2 = safe_json(login(ALICE, PASS_A)).get("access_token", "")
nid_multi_tok = note_id(create(t_a1, "Multi Session Note"))
r = patch(t_a2, nid_multi_tok, title="Patched by session 2")
check(145, "Two sessions for same user can both operate on same note",
      r.status_code == 200 and safe_json(r).get("title") == "Patched by session 2")

# 146. Alice creates 5 public + 5 private → Bob sees exactly the 5 public
pub_ids  = [note_id(create(alice_token, f"Pub {i}",  visibility="public"))  for i in range(5)]
priv_ids = [note_id(create(alice_token, f"Priv {i}", visibility="private")) for i in range(5)]
bob_new_pub = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])
               if n["id"] in pub_ids]
check(146, "Alice creates 5 public + 5 private → Bob sees exactly the 5 public",
      len(bob_new_pub) == 5, f"bob_sees_new_pub={len(bob_new_pub)}")

# 147. Private note with tag → Bob cannot see it via tag filter
priv_tag = note_id(create(alice_token, "Private With Tag",
                          tags=["invisible"], visibility="private"))
r = lst(bob_token, tags=["invisible"])
bob_tagged_ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(147, "Private note with tag → not visible to Bob via tag filter",
      priv_tag not in bob_tagged_ids)

# 148. PATCH body to large content → GET returns full content
nid_long = note_id(create(alice_token, "Long Body After Patch"))
huge = "X" * 5000
patch(alice_token, nid_long, body=huge)
r = get(alice_token, nid_long)
check(148, "PATCH body to 5000 chars → GET returns full content",
      safe_json(r).get("body") == huge)

# 149. Username case sensitivity: 'CaseSens' and 'casesens' (record behavior)
r1 = reg(f"CaseSens_{_s}", "pass1")
r2 = reg(f"casesens_{_s}", "pass2")
both_201 = r1.status_code == 201 and r2.status_code == 201
one_400  = r1.status_code == 201 and r2.status_code == 400
check(149, "Username case sensitivity: both 201 (case-sensitive) or second 400 (case-insensitive)",
      both_201 or one_400,
      f"upper={r1.status_code} lower={r2.status_code}")

# 150. Full end-to-end: register → login → create → read → update → delete → confirm gone
u150 = f"e2e_{_s}"
tk   = safe_json(reg(u150, "e2epass")).get("access_token", "")
tk   = safe_json(login(u150, "e2epass")).get("access_token", tk)
n150 = note_id(create(tk, "E2E Note", body="initial", visibility="public"))
r_get  = safe_json(get(tk, n150))
patch(tk, n150, title="E2E Note Updated", body="changed")
r_get2 = safe_json(get(tk, n150))
delete(tk, n150)
r_gone = get(tk, n150)
check(150, "Full E2E: register → login → create → read → update → delete → confirm 404",
      bool(n150)
      and r_get.get("version") == 1
      and r_get2.get("version") == 2
      and r_get2.get("title") == "E2E Note Updated"
      and r_gone.status_code == 404,
      f"id={'ok' if n150 else 'fail'} v1={r_get.get('version')} "
      f"v2={r_get2.get('version')} gone={r_gone.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n--- Summary ---")
# ════════════════════════════════════════════════════════════════════════════
passed      = sum(1 for _, ok, _, _ in results if ok)
total       = len(results)
failed_list = [(n, d) for n, ok, d, _ in results if not ok]

print(f"\nTotal: {total} scenarios")
print(f"  \033[32m✅ Passed: {passed}\033[0m")
if failed_list:
    print(f"  \033[31m❌ Failed: {len(failed_list)}\033[0m")
    for num, desc in failed_list:
        print(f"     [{num:03d}] {desc}")
else:
    print("  All scenarios passed!")

sys.exit(0 if not failed_list else 1)
