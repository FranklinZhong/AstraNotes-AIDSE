"""
AstraNotes — 100 Extended User Scenario Tests (Scenarios 51–150)
Runs against a live server at BASE_URL.
Usage: python user_scenario_tests_2.py
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
print("\n━━━ Waiting for server ━━━")
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
alice_token = safe_json(reg(ALICE, PASS_A)).get("access_token", "")
bob_token   = safe_json(reg(BOB,   PASS_B)).get("access_token", "")
charlie_token = safe_json(reg(CHARLIE, PASS_C)).get("access_token", "")
assert alice_token and bob_token and charlie_token, "Bootstrap failed – check server"

# ════════════════════════════════════════════════════════════════════════════
print("━━━ 八、用户名/密码边界 (51~60) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 51. 用户名含数字 → 201
r = reg(f"user42_{_s}", "pass1234")
check(51, "用户名含数字 → 201", r.status_code == 201)

# 52. 用户名含下划线 → 201
r = reg(f"user_name_{_s}", "pass1234")
check(52, "用户名含下划线 → 201", r.status_code == 201)

# 53. 密码含空格 → 201（密码不应过滤空格）
r = reg(f"spacepass_{_s}", "my secret pass")
check(53, "密码含空格 → 201（允许）", r.status_code == 201)

# 54. 密码含特殊字符 → 201
r = reg(f"specpass_{_s}", "P@ss!#$%^&*()")
check(54, "密码含特殊字符 → 201", r.status_code == 201)

# 55. 空白用户名（tab）→ 422
r = reg("\t", "somepass")
check(55, "Tab 用户名 → 422", r.status_code == 422,
      f"got {r.status_code}")

# 56. 同一用户多次登录 → 每次都返回有效 token
r1 = login(ALICE, PASS_A)
r2 = login(ALICE, PASS_A)
t1 = safe_json(r1).get("access_token", "")
t2 = safe_json(r2).get("access_token", "")
check(56, "多次登录 → 每次返回 token", bool(t1) and bool(t2))

# 57. 旧 token 在新登录后仍有效（无强制失效）
r = lst(alice_token)
check(57, "旧 token 在新登录后仍有效", r.status_code == 200)

# 58. 超长用户名（100 chars）→ 201 或 422（记录行为）
long_user = "u" * 100 + _s[:4]
r = reg(long_user, "pass1234")
check(58, f"超长用户名(100char) → {r.status_code}（记录行为）",
      r.status_code in (201, 422), f"got {r.status_code}")

# 59. Token 类型字段是 "bearer"
r = login(ALICE, PASS_A)
check(59, "登录响应 token_type='bearer'",
      safe_json(r).get("token_type") == "bearer")

# 60. 超长密码（100 chars）→ 201
r = reg(f"longpwd_{_s}", "x" * 100)
check(60, "超长密码(100char) → 201", r.status_code == 201)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 九、笔记默认值与字段验证 (61~70) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 61. 新建笔记 author_id = 注册用户名
r = create(alice_token, "Field Check Note", visibility="public")
nid = note_id(r)
check(61, "新建笔记 author_id 等于用户名",
      safe_json(r).get("author_id") == ALICE,
      f"author_id={safe_json(r).get('author_id')}")

# 62. 新建笔记 version = 1
check(62, "新建笔记 version = 1",
      safe_json(r).get("version") == 1,
      f"version={safe_json(r).get('version')}")

# 63. 新建笔记含 created_at 和 updated_at
data = safe_json(r)
check(63, "新建笔记含 created_at 和 updated_at",
      bool(data.get("created_at")) and bool(data.get("updated_at")))

# 64. 更新笔记后 version 递增
r2 = patch(alice_token, nid, title="Field Check Note v2")
check(64, "PATCH 后 version 递增 (1→2)",
      safe_json(r2).get("version") == 2,
      f"version={safe_json(r2).get('version')}")

# 65. 多次 PATCH 版本持续递增
r3 = patch(alice_token, nid, body="updated body")
check(65, "第二次 PATCH version = 3",
      safe_json(r3).get("version") == 3)

# 66. 不指定 visibility → 默认 "public"（NoteCreate 默认值）
r = create(alice_token, "Default Visibility Note")
check(66, "不指定 visibility → 默认 'public'",
      safe_json(r).get("visibility") == "public",
      f"visibility={safe_json(r).get('visibility')}")
nid_default = note_id(r)

# 67. 显式指定 visibility='private' → 存储正确
r = create(alice_token, "Explicit Private Note", visibility="private")
check(67, "显式 visibility='private' → 存储正确",
      safe_json(r).get("visibility") == "private")

# 68. 无效 visibility 值 → 422
r = create(alice_token, "Bad Visibility", visibility="secret")
check(68, "无效 visibility 值 → 422",
      r.status_code == 422, f"got {r.status_code}")

# 69. 笔记响应含全部必要字段
r = create(alice_token, "Full Fields Note", body="body text",
           tags=["t1"], visibility="public")
d = safe_json(r)
required = {"id", "title", "body", "tags", "visibility",
            "author_id", "created_at", "updated_at", "version"}
check(69, "创建响应含全部必要字段",
      required.issubset(d.keys()),
      f"missing={required - d.keys()}")

# 70. 列表响应含 'notes' 数组和 'total' 整数
r = lst(alice_token)
d = safe_json(r)
check(70, "列表响应含 'notes' 数组 和 'total' 整数",
      isinstance(d.get("notes"), list) and isinstance(d.get("total"), int),
      f"notes={type(d.get('notes')).__name__} total={type(d.get('total')).__name__}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十、Tag 操作 (71~82) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 71. 创建无 tags 的笔记 → tags=[]
r = create(alice_token, "No Tags Note")
check(71, "无 tags 创建 → tags=[]",
      safe_json(r).get("tags") == [],
      f"tags={safe_json(r).get('tags')}")

# 72. 创建单个 tag → 正确存储
r = create(alice_token, "One Tag Note", tags=["Python"])
check(72, "单 tag 创建 → tags=['Python']",
      safe_json(r).get("tags") == ["Python"])
nid_one_tag = note_id(r)

# 73. 创建多个 tags → 全部存储
r = create(alice_token, "Multi Tag Note", tags=["Python", "AI", "FastAPI"])
check(73, "多 tag 创建 → 全部存储",
      set(safe_json(r).get("tags", [])) == {"Python", "AI", "FastAPI"})
nid_multi = note_id(r)

# 74. PATCH 添加 tags（从无到有）
nid_tag_up = note_id(create(alice_token, "Add Tag Note"))
r = patch(alice_token, nid_tag_up, tags=["NewTag"])
check(74, "PATCH 添加 tags（无→有）",
      safe_json(r).get("tags") == ["NewTag"])

# 75. PATCH 清空 tags（有→[]）
r = patch(alice_token, nid_tag_up, tags=[])
check(75, "PATCH 清空 tags（有→[]）",
      safe_json(r).get("tags") == [])

# 76. 过滤两个 tag（交集）→ 只返回同时含两个 tag 的笔记
nid_both = note_id(create(alice_token, "Both Tags", tags=["AI", "FastAPI"]))
nid_only_ai = note_id(create(alice_token, "Only AI", tags=["AI"]))
r = lst(alice_token, tags=["AI", "FastAPI"])
ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(76, "两 tag 过滤（交集）→ 含两 tag 的笔记出现，单 tag 的不出现",
      nid_both in ids and nid_only_ai not in ids,
      f"matched={len(ids)}")

# 77. 单 tag 过滤：返回多用户的公开笔记（只含该单 tag 即可匹配 AND 逻辑）
bob_tagged = note_id(create(bob_token, "Bob AI Note", tags=["AI"], visibility="public"))
r = lst(alice_token, tags=["AI"])
ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(77, "单 tag 过滤返回其他用户的公开笔记（AND 逻辑，含该 tag 即可）",
      bob_tagged in ids)

# 78. 含连字符的 tag → 201
r = create(alice_token, "Hyphen Tag", tags=["my-tag", "v1.0"])
check(78, "含连字符/点 tag → 201",
      r.status_code == 201 and "my-tag" in safe_json(r).get("tags", []))

# 79. 含空格的 tag → 201（存储原样）
r = create(alice_token, "Space Tag", tags=["my note", "machine learning"])
check(79, "含空格 tag → 201，存储原样",
      r.status_code == 201 and "my note" in safe_json(r).get("tags", []))

# 80. PATCH tags 后 GET 返回更新后的 tags
nid_tag_check = note_id(create(alice_token, "Tag Check Note", tags=["old"]))
patch(alice_token, nid_tag_check, tags=["new1", "new2"])
r = get(alice_token, nid_tag_check)
check(80, "PATCH tags 后 GET 验证 tags 已更新",
      set(safe_json(r).get("tags", [])) == {"new1", "new2"})

# 81. 加 tag 后过滤 → 出现；清空后过滤 → 消失
patch(alice_token, nid_tag_check, tags=["filter_me"])
r1 = lst(alice_token, tags=["filter_me"])
patch(alice_token, nid_tag_check, tags=[])
r2 = lst(alice_token, tags=["filter_me"])
ids1 = [n["id"] for n in safe_json(r1).get("notes", [])]
ids2 = [n["id"] for n in safe_json(r2).get("notes", [])]
check(81, "加 tag→过滤出现；清空 tag→过滤消失",
      nid_tag_check in ids1 and nid_tag_check not in ids2)

# 82. Tag 过滤对私有笔记同样尊重隐私
priv_tagged = note_id(create(alice_token, "Private Tagged", tags=["secret"], visibility="private"))
r = lst(bob_token, tags=["secret"])
ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(82, "私有笔记含 tag → Bob 过滤看不到",
      priv_tagged not in ids)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十一、内容边界（长度/特殊字符/Unicode）(83~92) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 83. 超长标题（500 chars）→ 201
long_title = "A" * 500
r = create(alice_token, long_title)
check(83, "超长标题(500chars) → 201",
      r.status_code == 201 and safe_json(r).get("title") == long_title)

# 84. 超长 body（10000 chars）→ 201
long_body = "B" * 10000
r = create(alice_token, "Long Body Note", body=long_body)
check(84, "超长 body(10000chars) → 201，内容完整保存",
      r.status_code == 201 and safe_json(r).get("body") == long_body)
nid_long_body = note_id(r)

# 85. 中文标题 → 201
r = create(alice_token, "我的笔记：Python学习")
check(85, "中文标题 → 201，内容正确",
      r.status_code == 201 and safe_json(r).get("title") == "我的笔记：Python学习")

# 86. 中文 body → 201
r = create(alice_token, "Chinese Body", body="今天学习了人工智能和深度学习，非常有收获。")
check(86, "中文 body → 201，内容完整",
      r.status_code == 201 and "人工智能" in safe_json(r).get("body", ""))

# 87. 标题含特殊字符（!, @, #, $）→ 201
r = create(alice_token, "Note! @Special #Tag $100")
check(87, "特殊字符标题 → 201",
      r.status_code == 201)

# 88. body 含换行符 → 201，保留换行
r = create(alice_token, "Multiline Body", body="Line 1\nLine 2\nLine 3")
check(88, "body 含换行符 → 201，换行保留",
      r.status_code == 201 and "\n" in safe_json(r).get("body", ""))

# 89. body 含 HTML → 201，存储原样（不转义/不过滤）
html = "<script>alert('xss')</script><b>bold</b>"
r = create(alice_token, "HTML Body", body=html)
check(89, "body 含 HTML/JS → 201，原样存储（API 不过滤）",
      r.status_code == 201 and safe_json(r).get("body") == html)

# 90. PATCH body 改为空字符串 → 200
nid_body_clear = note_id(create(alice_token, "Will Clear Body", body="some content"))
r = patch(alice_token, nid_body_clear, body="")
check(90, "PATCH body 改为空字符串 → 200（body 可选）",
      r.status_code == 200 and safe_json(r).get("body") == "")

# 91. 标题含制表符（中间）→ 201（不含纯空白，应通过）
r = create(alice_token, "Tab\tIn\tMiddle")
check(91, "标题含制表符（非纯空白，非行首尾）→ 201",
      r.status_code == 201)

# 92. emoji 标题 → 201
r = create(alice_token, "📝 My Notes 🚀")
check(92, "Emoji 标题 → 201",
      r.status_code == 201 and "📝" in safe_json(r).get("title", ""))

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十二、三用户隔离（Alice/Bob/Charlie）(93~105) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 93. Alice 私有笔记：Bob 和 Charlie 都看不到（列表）
a_priv = note_id(create(alice_token, "Alice Super Secret", visibility="private"))
bob_list   = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
char_list  = [n["id"] for n in safe_json(lst(charlie_token)).get("notes", [])]
check(93, "Alice 私有笔记：Bob 列表看不到",   a_priv not in bob_list)
check(94, "Alice 私有笔记：Charlie 列表看不到", a_priv not in char_list)

# 95. Alice 公开笔记：Bob 和 Charlie 都能看到（列表）
a_pub = note_id(create(alice_token, "Alice Public For All", visibility="public"))
bob_list2  = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
char_list2 = [n["id"] for n in safe_json(lst(charlie_token)).get("notes", [])]
check(95, "Alice 公开笔记：Bob 列表可见",    a_pub in bob_list2)
check(96, "Alice 公开笔记：Charlie 列表可见", a_pub in char_list2)

# 97. Charlie 获取 Alice 私有笔记 by ID → 403
r = get(charlie_token, a_priv)
check(97, "Charlie 获取 Alice 私有笔记 by ID → 403", r.status_code == 403)

# 98. Charlie 获取 Alice 公开笔记 by ID → 200
r = get(charlie_token, a_pub)
check(98, "Charlie 获取 Alice 公开笔记 by ID → 200", r.status_code == 200)

# 99. Bob 不能删除 Alice 的公开笔记 → 403
r = delete(bob_token, a_pub)
check(99, "Bob 删除 Alice 公开笔记 → 403", r.status_code == 403)

# 100. Charlie 不能修改 Bob 的笔记 → 403
b_pub = note_id(create(bob_token, "Bob Public Note", visibility="public"))
r = patch(charlie_token, b_pub, title="Hacked by Charlie")
check(100, "Charlie 修改 Bob 笔记 → 403", r.status_code == 403)

# 101. 三用户各建一条同名笔记 → 各自独立（不同 ID）
ids_same = []
for tok in [alice_token, bob_token, charlie_token]:
    ids_same.append(note_id(create(tok, "Same Title Note", visibility="public")))
check(101, "三用户同名笔记 → 三个不同 ID（互不干扰）",
      len(set(ids_same)) == 3, f"ids={ids_same}")

# 102. Alice 删除自己的笔记 → Bob/Charlie 列表更新
a_del = note_id(create(alice_token, "Will Be Deleted", visibility="public"))
before_bob = len(safe_json(lst(bob_token)).get("notes", []))
delete(alice_token, a_del)
after_bob = len(safe_json(lst(bob_token)).get("notes", []))
check(102, "Alice 删除公开笔记 → Bob 列表减少",
      after_bob == before_bob - 1,
      f"before={before_bob} after={after_bob}")

# 103. Alice 修改公开笔记 → Bob GET by ID 看到最新内容
a_upd = note_id(create(alice_token, "Original Title", visibility="public"))
patch(alice_token, a_upd, title="Updated Title")
r = get(bob_token, a_upd)
check(103, "Alice 改笔记标题 → Bob by ID 看到更新",
      safe_json(r).get("title") == "Updated Title")

# 104. Alice 将公开笔记改私有 → Bob 立刻不可见（列表 + by ID）
patch(alice_token, a_upd, visibility="private")
b_ids = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
r_get = get(bob_token, a_upd)
check(104, "笔记私有化 → Bob 列表消失 且 by ID → 403",
      a_upd not in b_ids and r_get.status_code == 403,
      f"list={'hidden' if a_upd not in b_ids else 'exposed'} get={r_get.status_code}")

# 105. Alice 再将笔记改回公开 → Bob 立刻可见
patch(alice_token, a_upd, visibility="public")
b_ids2 = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])]
check(105, "笔记重新公开 → Bob 列表恢复可见",
      a_upd in b_ids2)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十三、状态一致性 (106~117) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 106. 创建后立刻可 by ID 获取
r_c = create(alice_token, "Immediate Get Note")
nid_imm = note_id(r_c)
r_g = get(alice_token, nid_imm)
check(106, "创建后立刻 by ID 可获取",
      r_g.status_code == 200 and safe_json(r_g).get("id") == nid_imm)

# 107. 更新后列表中标题已更新
patch(alice_token, nid_imm, title="Updated Immediate")
titles = [n["title"] for n in safe_json(lst(alice_token)).get("notes", [])]
check(107, "PATCH 后列表中标题已更新",
      "Updated Immediate" in titles)

# 108. 删除后立刻从列表消失
nid_gone = note_id(create(alice_token, "Will Vanish"))
delete(alice_token, nid_gone)
ids_after = [n["id"] for n in safe_json(lst(alice_token)).get("notes", [])]
check(108, "删除后立刻从列表消失", nid_gone not in ids_after)

# 109. 创建 5 条笔记 → total 正确
before = safe_json(lst(alice_token)).get("total", 0)
new_ids = [note_id(create(alice_token, f"Batch Note {i}")) for i in range(5)]
after = safe_json(lst(alice_token)).get("total", 0)
check(109, "创建 5 条笔记 → total 增加 5",
      after == before + 5, f"before={before} after={after}")

# 110. 删除 3 条 → total 减少 3
for nid in new_ids[:3]:
    delete(alice_token, nid)
final = safe_json(lst(alice_token)).get("total", 0)
check(110, "删除 3 条 → total 减少 3",
      final == after - 3, f"expected={after-3} got={final}")

# 111. created_at 在 PATCH 后不变
nid_ts = note_id(create(alice_token, "Timestamp Note"))
r_before = safe_json(get(alice_token, nid_ts))
time.sleep(1)
patch(alice_token, nid_ts, title="Timestamp Note v2")
r_after = safe_json(get(alice_token, nid_ts))
check(111, "PATCH 后 created_at 不变",
      r_before.get("created_at") == r_after.get("created_at"),
      f"before={r_before.get('created_at')} after={r_after.get('created_at')}")

# 112. updated_at 在 PATCH 后变化（或相同秒内相同 — 接受两种）
check(112, "PATCH 后 updated_at 已记录（字段存在且非空）",
      bool(r_after.get("updated_at")))

# 113. 空 PATCH（不含任何字段）→ 200，笔记内容不变
nid_nop = note_id(create(alice_token, "No-op Patch Note", body="original"))
r = patch(alice_token, nid_nop)
check(113, "空 PATCH（无字段）→ 200，内容不变",
      r.status_code == 200 and safe_json(r).get("body") == "original")

# 114. 同一字段多次 PATCH → 最终值正确
nid_rep = note_id(create(alice_token, "Repeat Patch"))
patch(alice_token, nid_rep, title="v1")
patch(alice_token, nid_rep, title="v2")
r = patch(alice_token, nid_rep, title="v3")
check(114, "多次 PATCH title → 最终值为最后一次",
      safe_json(r).get("title") == "v3")

# 115. 创建笔记 → 获取 → PATCH → 再获取 → version 正确
nid_ver = note_id(create(alice_token, "Version Track"))
r_v1 = safe_json(get(alice_token, nid_ver))
patch(alice_token, nid_ver, title="Version Track v2")
r_v2 = safe_json(get(alice_token, nid_ver))
check(115, "创建(v=1) → PATCH → GET v=2",
      r_v1.get("version") == 1 and r_v2.get("version") == 2)

# 116. PATCH visibility 为相同值 → 200，无报错
nid_same_vis = note_id(create(alice_token, "Same Vis Note", visibility="public"))
r = patch(alice_token, nid_same_vis, visibility="public")
check(116, "PATCH visibility 为相同值 → 200（幂等）", r.status_code == 200)

# 117. 多用户各自独立 total（不互相影响列表计数）
alice_total = safe_json(lst(alice_token)).get("total", -1)
bob_total   = safe_json(lst(bob_token)).get("total", -1)
create(charlie_token, "Charlie Private", visibility="private")
alice_total2 = safe_json(lst(alice_token)).get("total", -1)
bob_total2   = safe_json(lst(bob_token)).get("total", -1)
check(117, "Charlie 建私有笔记 → Alice/Bob 的 total 不变",
      alice_total == alice_total2 and bob_total == bob_total2,
      f"alice:{alice_total}→{alice_total2} bob:{bob_total}→{bob_total2}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十四、安全与边界输入 (118~132) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 118. note_id 为全零 UUID → 404（不崩溃）
r = get(alice_token, "00000000-0000-0000-0000-000000000000")
check(118, "全零 UUID note_id → 404", r.status_code == 404)

# 119. note_id 类似 SQL 注入 → 404（安全）
r = get(alice_token, "'; DROP TABLE notes; --")
check(119, "SQL 注入式 note_id → 404（安全处理）",
      r.status_code == 404, f"got {r.status_code}")

# 120. note_id 为空字符串（路径不匹配）→ 405 或 404
r = requests.get(f"{BASE_URL}/notes/ ", headers=hdr(alice_token))
check(120, "note_id 含空格路径 → 非 500（不崩溃）",
      r.status_code != 500, f"got {r.status_code}")

# 121. PATCH 请求含未知字段 → 200（忽略未知字段）
nid_extra = note_id(create(alice_token, "Extra Fields"))
r = requests.patch(f"{BASE_URL}/notes/{nid_extra}",
                   json={"title": "OK", "unknown_field": "ignored"},
                   headers=hdr(alice_token))
check(121, "PATCH 含未知字段 → 200（Pydantic 忽略多余字段）",
      r.status_code == 200)

# 122. PATCH visibility 为无效值 → 422
r = patch(alice_token, nid_extra, visibility="classified")
check(122, "PATCH visibility 无效值 → 422",
      r.status_code == 422, f"got {r.status_code}")

# 123. Authorization header 格式错误（无 Bearer 前缀）→ 401
r = requests.get(f"{BASE_URL}/notes/",
                 headers={"Authorization": alice_token})
check(123, "Authorization 无 'Bearer' 前缀 → 401",
      r.status_code == 401, f"got {r.status_code}")

# 124. Authorization 值为 "Bearer "（token 为空）→ 401
r = requests.get(f"{BASE_URL}/notes/",
                 headers={"Authorization": "Bearer "})
check(124, "Bearer 后无 token → 401", r.status_code == 401, f"got {r.status_code}")

# 125. POST /notes 不含 title 字段 → 422
r = requests.post(f"{BASE_URL}/notes/",
                  json={"body": "no title here"},
                  headers=hdr(alice_token))
check(125, "创建笔记不含 title 字段 → 422", r.status_code == 422)

# 126. POST /notes 含 null title → 422
r = requests.post(f"{BASE_URL}/notes/",
                  json={"title": None, "body": "test"},
                  headers=hdr(alice_token))
check(126, "创建笔记 title=null → 422", r.status_code == 422, f"got {r.status_code}")

# 127. 错误响应含 "detail" 字段（422）
r = create(alice_token, "")
check(127, "422 错误响应含 'detail' 字段",
      "detail" in safe_json(r), f"keys={list(safe_json(r).keys())}")

# 128. 错误响应含 "detail" 字段（404）
r = get(alice_token, "00000000-0000-0000-0000-000000000001")
check(128, "404 错误响应含 'detail' 字段",
      "detail" in safe_json(r))

# 129. 错误响应含 "detail" 字段（403）
r = get(bob_token, a_priv)
check(129, "403 错误响应含 'detail' 字段",
      "detail" in safe_json(r))

# 130. DELETE 请求含 body（应被忽略）→ 204
nid_del_body = note_id(create(alice_token, "Delete With Body"))
r = requests.delete(f"{BASE_URL}/notes/{nid_del_body}",
                    json={"confirm": True}, headers=hdr(alice_token))
check(130, "DELETE 请求含 body → 204（body 被忽略）", r.status_code == 204)

# 131. 注册后的 token 可直接使用（无需再 login）
r_reg = reg(f"direct_{_s}", "pass1234")
direct_token = safe_json(r_reg).get("access_token", "")
r = lst(direct_token)
check(131, "注册响应的 token 可直接用于后续请求",
      r.status_code == 200)

# 132. 错误的 HTTP 方法 → 405（Method Not Allowed）
r = requests.put(f"{BASE_URL}/notes/", headers=hdr(alice_token))
check(132, "PUT /notes/（不支持的方法）→ 405",
      r.status_code == 405, f"got {r.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十五、健康检查与端点可用性 (133~137) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 133. GET /health 无 token → 200
r = requests.get(f"{BASE_URL}/health")
check(133, "GET /health 无 token → 200（公开端点）", r.status_code == 200)

# 134. GET /health 含 service 字段
check(134, "GET /health 响应含 'service' 字段",
      "service" in safe_json(r))

# 135. GET /docs 可访问（FastAPI 自动文档）
r = requests.get(f"{BASE_URL}/docs")
check(135, "GET /docs → 200（Swagger UI 可访问）", r.status_code == 200)

# 136. GET /openapi.json 可访问
r = requests.get(f"{BASE_URL}/openapi.json")
check(136, "GET /openapi.json → 200（API schema 可访问）", r.status_code == 200)

# 137. openapi.json 含 /notes 路径定义
d = safe_json(r)
check(137, "openapi.json 含 /notes/ 路径定义",
      "/notes/" in d.get("paths", {}))

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 十六、批量操作与极端场景 (138~150) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 138. 快速连续创建 10 条笔记 → 全部成功
ids_bulk = []
for i in range(10):
    r = create(alice_token, f"Bulk Note {i}", visibility="public")
    ids_bulk.append(note_id(r))
check(138, "快速连续创建 10 条笔记 → 全部成功",
      len([x for x in ids_bulk if x]) == 10)

# 139. 创建 10 条后 total 包含全部
total_now = safe_json(lst(alice_token)).get("total", 0)
check(139, "列表 total 包含批量创建的 10 条",
      total_now >= 10, f"total={total_now}")

# 140. 删除全部 bulk 笔记 → 全部消失
for nid in ids_bulk:
    if nid: delete(alice_token, nid)
ids_after = [n["id"] for n in safe_json(lst(alice_token)).get("notes", [])]
check(140, "删除 10 条 bulk 笔记 → 全部从列表消失",
      all(nid not in ids_after for nid in ids_bulk if nid))

# 141. Alice 创建 → Bob 读 → Alice 删 → Bob 再读 → 404
shared = note_id(create(alice_token, "Shared Then Gone", visibility="public"))
get(bob_token, shared)          # Bob 能读
delete(alice_token, shared)     # Alice 删
r = get(bob_token, shared)      # Bob 再读
check(141, "Alice 删除后 Bob 再 GET → 404",
      r.status_code == 404)

# 142. Bob 尝试 PATCH + DELETE Alice 笔记（已删）→ 404 / 403（顺序无关）
nid_x = note_id(create(alice_token, "Cross Delete", visibility="public"))
delete(alice_token, nid_x)
r_p = patch(bob_token, nid_x, title="Can't patch deleted")
r_d = delete(bob_token, nid_x)
check(142, "已删笔记 Bob PATCH → 404",
      r_p.status_code == 404, f"got {r_p.status_code}")
check(143, "已删笔记 Bob DELETE → 404",
      r_d.status_code == 404, f"got {r_d.status_code}")

# 144. 用户 A 的 token 无法操作用户 B 的私有笔记（链式验证）
b_priv2 = note_id(create(bob_token, "Bob Deep Private", visibility="private"))
checks = [
    get(alice_token, b_priv2).status_code == 403,
    patch(alice_token, b_priv2, title="x").status_code == 403,
    delete(alice_token, b_priv2).status_code == 403,
]
check(144, "Alice 对 Bob 私有笔记：GET/PATCH/DELETE 全部 403",
      all(checks), f"results={checks}")

# 145. 同一用户不同 session（两个 token）操作同一笔记 → 一致
t_a1 = safe_json(login(ALICE, PASS_A)).get("access_token", "")
t_a2 = safe_json(login(ALICE, PASS_A)).get("access_token", "")
nid_multi_tok = note_id(create(t_a1, "Multi Session Note"))
r = patch(t_a2, nid_multi_tok, title="Patched by session 2")
check(145, "同用户不同 session token 操作同一笔记 → 200",
      r.status_code == 200 and safe_json(r).get("title") == "Patched by session 2")

# 146. 混合 public/private：Alice 5 pub + 5 priv → Bob 看 5，Alice 看 10
pub_ids  = [note_id(create(alice_token, f"Pub {i}", visibility="public"))  for i in range(5)]
priv_ids = [note_id(create(alice_token, f"Priv {i}", visibility="private")) for i in range(5)]
alice_sees = safe_json(lst(alice_token)).get("total", 0)
bob_new_pub = [n["id"] for n in safe_json(lst(bob_token)).get("notes", [])
               if n["id"] in pub_ids]
check(146, "Alice 建 5pub+5priv → Bob 只看到新 5 条 pub",
      len(bob_new_pub) == 5, f"bob_sees_new_pub={len(bob_new_pub)}")

# 147. Tag 过滤结合隐私：Alice 私有含 tag → Bob 过滤看不到
priv_tag = note_id(create(alice_token, "Private With Tag",
                          tags=["invisible"], visibility="private"))
r = lst(bob_token, tags=["invisible"])
bob_tagged_ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(147, "私有笔记含 tag → Bob 过滤看不到",
      priv_tag not in bob_tagged_ids)

# 148. 更新笔记 body 为超长内容后 GET 保持完整
nid_long = note_id(create(alice_token, "Long Body After Patch"))
huge = "X" * 5000
patch(alice_token, nid_long, body=huge)
r = get(alice_token, nid_long)
check(148, "PATCH body 为 5000 chars → GET 返回完整内容",
      safe_json(r).get("body") == huge)

# 149. 注册用户名大小写：'Alice_Test' 和 'alice_test' 是否不同（取决于实现）
r1 = reg(f"CaseSens_{_s}", "pass1")
r2 = reg(f"casesens_{_s}", "pass2")
both_201 = r1.status_code == 201 and r2.status_code == 201
one_400  = r1.status_code == 201 and r2.status_code == 400
check(149, "用户名大小写：两者都 201（区分大小写）或 后者 400（不区分）",
      both_201 or one_400,
      f"upper={r1.status_code} lower={r2.status_code}")

# 150. 完整端到端：注册→登录→创建→读取→修改→删除→确认
u150 = f"e2e_{_s}"
tk = safe_json(reg(u150, "e2epass")).get("access_token", "")
tk = safe_json(login(u150, "e2epass")).get("access_token", tk)
n150 = note_id(create(tk, "E2E Note", body="initial", visibility="public"))
r_get = safe_json(get(tk, n150))
patch(tk, n150, title="E2E Note Updated", body="changed")
r_get2 = safe_json(get(tk, n150))
delete(tk, n150)
r_gone = get(tk, n150)
check(150, "完整 E2E：注册→登录→创建→读取→修改→删除→确认消失",
      bool(n150)
      and r_get.get("version") == 1
      and r_get2.get("version") == 2
      and r_get2.get("title") == "E2E Note Updated"
      and r_gone.status_code == 404,
      f"id={'ok' if n150 else 'fail'} v1={r_get.get('version')} "
      f"v2={r_get2.get('version')} gone={r_gone.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 汇总 ━━━")
# ════════════════════════════════════════════════════════════════════════════
passed = sum(1 for _, ok, _, _ in results if ok)
total  = len(results)
failed_list = [(n, d) for n, ok, d, _ in results if not ok]

print(f"\n总计：{total} 个场景")
print(f"  \033[32m✅ 通过：{passed}\033[0m")
if failed_list:
    print(f"  \033[31m❌ 失败：{len(failed_list)}\033[0m")
    for num, desc in failed_list:
        print(f"     [{num:03d}] {desc}")
else:
    print("  🎉 全部通过！")

sys.exit(0 if not failed_list else 1)
