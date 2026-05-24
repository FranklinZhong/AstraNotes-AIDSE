"""
AstraNotes — 50 User Scenario Tests
Runs against a live server at BASE_URL.
Usage: python user_scenario_tests.py
"""
import sys
import time
import random
import string
import requests

BASE_URL = "http://127.0.0.1:8001"

# 每次运行使用唯一用户名，避免 DB 残留冲突
_suffix = "".join(random.choices(string.ascii_lowercase, k=6))
ALICE = f"alice_{_suffix}"
BOB   = f"bob_{_suffix}"

# ── helpers ──────────────────────────────────────────────────────────────────

PASS = "\033[32m✅ PASS\033[0m"
FAIL = "\033[31m❌ FAIL\033[0m"
WARN = "\033[33m⚠️  WARN\033[0m"

results = []


def check(num: int, desc: str, passed: bool, detail: str = ""):
    status = PASS if passed else FAIL
    line = f"[{num:02d}] {status}  {desc}"
    if detail:
        line += f"\n       → {detail}"
    print(line)
    results.append(passed)


def register(username, password):
    r = requests.post(f"{BASE_URL}/auth/register",
                      json={"username": username, "password": password})
    return r


def login(username, password):
    r = requests.post(f"{BASE_URL}/auth/login",
                      json={"username": username, "password": password})
    return r


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

print("\n━━━ Waiting for server ━━━")
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
print("━━━ 一、用户注册与认证 (1~10) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 1. Alice 正常注册
r = register(ALICE, "securepass123")
alice_token = safe_json(r).get("access_token", "") if r.status_code == 201 else ""
check(1, f"Alice({ALICE}) 注册 → 201 + access_token", r.status_code == 201 and bool(alice_token))

# 2. Bob 正常注册
r = register(BOB, "bobpass456")
bob_token = safe_json(r).get("access_token", "") if r.status_code == 201 else ""
check(2, f"Bob({BOB}) 注册 → 201 + access_token", r.status_code == 201 and bool(bob_token))

# 3. 重复注册同一用户名 → 400
r = register(ALICE, "anotherpass")
check(3, "重复用户名注册 → 400 Bad Request", r.status_code == 400,
      safe_json(r).get("detail", ""))

# 4. Alice 用正确密码登录 → 200 + token
r = login(ALICE, "securepass123")
alice_token2 = safe_json(r).get("access_token", "") if r.status_code == 200 else ""
check(4, "Alice 正确密码登录 → 200 + token", r.status_code == 200 and bool(alice_token2))
alice_token = alice_token2  # 使用最新 token

# 5. Alice 用错误密码登录 → 401
r = login(ALICE, "wrongpassword")
check(5, "错误密码登录 → 401 Unauthorized", r.status_code == 401,
      safe_json(r).get("detail", ""))

# 6. 不存在的用户登录 → 401
r = login("ghost_user_xyz", "anypass")
check(6, "不存在用户登录 → 401 Unauthorized", r.status_code == 401,
      safe_json(r).get("detail", ""))

# 7. 无 token 访问 /notes/ → 401
r = requests.get(f"{BASE_URL}/notes/")
check(7, "无 token 访问 /notes/ → 401", r.status_code == 401,
      f"got {r.status_code}")

# 8. 无效 token 访问 /notes/ → 401
r = requests.get(f"{BASE_URL}/notes/",
                 headers={"Authorization": "Bearer invalid.jwt.token"})
check(8, "无效 token 访问 /notes/ → 401", r.status_code == 401,
      f"got {r.status_code}")

# 9. 空用户名注册 → 422 Validation Error
r = register("", "somepass")
check(9, "空用户名注册 → 422 Validation Error", r.status_code == 422,
      f"got {r.status_code}")

# 10. 空密码注册 → 422 Validation Error
r = register("newuser", "")
check(10, "空密码注册 → 422 Validation Error", r.status_code == 422,
      f"got {r.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 二、创建笔记 (11~18) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 11. Alice 创建公开笔记
r = create_note(alice_token, "Alice Public Note", "Hello world", "public")
alice_pub_id = r.json().get("id", "") if r.status_code == 201 else ""
check(11, "Alice 创建公开笔记 → 201", r.status_code == 201 and bool(alice_pub_id),
      f"id={alice_pub_id}")

# 12. Alice 创建私有笔记
r = create_note(alice_token, "Alice Private Note", "Secret content", "private")
alice_priv_id = r.json().get("id", "") if r.status_code == 201 else ""
check(12, "Alice 创建私有笔记 → 201", r.status_code == 201 and bool(alice_priv_id),
      f"id={alice_priv_id}")

# 13. Alice 创建带 tags 的笔记
r = create_note(alice_token, "Alice Tagged Note", "Python content",
                "public", tags=["Python", "AI"])
alice_tagged_id = r.json().get("id", "") if r.status_code == 201 else ""
check(13, "Alice 创建带 tags 笔记 → 201，tags=[Python, AI]",
      r.status_code == 201 and bool(alice_tagged_id),
      f"tags={r.json().get('tags', [])}")

# 14. Bob 创建公开笔记
r = create_note(bob_token, "Bob Public Note", "Bob says hello", "public")
bob_pub_id = r.json().get("id", "") if r.status_code == 201 else ""
check(14, "Bob 创建公开笔记 → 201", r.status_code == 201 and bool(bob_pub_id))

# 15. Bob 创建私有笔记
r = create_note(bob_token, "Bob Private Note", "Bob secret", "private")
bob_priv_id = r.json().get("id", "") if r.status_code == 201 else ""
check(15, "Bob 创建私有笔记 → 201", r.status_code == 201 and bool(bob_priv_id))

# 16. 空标题创建笔记 → 422
r = create_note(alice_token, "", "body content")
check(16, "空标题创建笔记 → 422", r.status_code == 422,
      f"got {r.status_code}")

# 17. 纯空白标题创建笔记 → 422/400（whitespace 验证）
r = create_note(alice_token, "   ", "body content")
check(17, "纯空白标题创建笔记 → 422/400（whitespace 拦截）",
      r.status_code in (400, 422),
      f"got {r.status_code}: {r.json()}")

# 18. body 为空（None）→ 应该成功（body 是可选的）
r = create_note(alice_token, "Note Without Body")
check(18, "body 为空（可选字段）→ 201 成功", r.status_code == 201,
      f"got {r.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 三、列表查询（list） (19~26) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 19. Alice 列出笔记：能看到自己的全部 + Bob 的公开笔记
r = list_notes(alice_token)
alice_list = safe_json(r).get("notes", []) if r.status_code == 200 else []
alice_ids_in_list = [n["id"] for n in alice_list]
check(19, "Alice 列表：能看到自己的公开+私有笔记",
      alice_pub_id in alice_ids_in_list and alice_priv_id in alice_ids_in_list,
      f"total={safe_json(r).get('total',0)}")

# 20. Alice 列表：能看到 Bob 的公开笔记
check(20, "Alice 列表：能看到 Bob 的公开笔记",
      bob_pub_id in alice_ids_in_list,
      f"bob_pub_id={'✅' if bob_pub_id in alice_ids_in_list else '❌'}")

# 21. Alice 列表：看不到 Bob 的私有笔记
check(21, "Alice 列表：看不到 Bob 的私有笔记",
      bob_priv_id not in alice_ids_in_list,
      f"bob_priv_id={'隐藏✅' if bob_priv_id not in alice_ids_in_list else '泄露❌'}")

# 22. Bob 列表：看不到 Alice 的私有笔记
r = list_notes(bob_token)
bob_list = r.json().get("notes", []) if r.status_code == 200 else []
bob_ids_in_list = [n["id"] for n in bob_list]
check(22, "Bob 列表：看不到 Alice 的私有笔记",
      alice_priv_id not in bob_ids_in_list,
      f"alice_priv_id={'隐藏✅' if alice_priv_id not in bob_ids_in_list else '泄露❌'}")

# 23. 按 tag 过滤：只返回含 "Python" 的笔记
r = list_notes(alice_token, tags=["Python"])
tagged_ids = [n["id"] for n in r.json().get("notes", [])]
check(23, "Tag 过滤 [Python]：只返回含该 tag 的笔记",
      alice_tagged_id in tagged_ids and bob_pub_id not in tagged_ids,
      f"matched={len(tagged_ids)} note(s)")

# 24. 过滤不存在的 tag → 返回空列表
r = list_notes(alice_token, tags=["NonExistentTag99"])
check(24, "过滤不存在 tag → 返回空列表",
      r.json().get("total", -1) == 0,
      f"total={r.json().get('total')}")

# 25. Tag 区分大小写："python"（小写）≠ "Python"
r = list_notes(alice_token, tags=["python"])
check(25, "Tag 大小写敏感：'python' 不匹配 'Python'",
      alice_tagged_id not in [n["id"] for n in r.json().get("notes", [])],
      f"matched={r.json().get('total',0)}")

# 26. 未认证用户访问 /notes/ → 401
r = requests.get(f"{BASE_URL}/notes/")
check(26, "未认证访问 /notes/ → 401", r.status_code == 401)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 四、按 ID 获取笔记 (27~32) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 27. Alice 获取自己的公开笔记 → 200
r = get_note(alice_token, alice_pub_id)
check(27, "Alice 获取自己公开笔记 by ID → 200",
      r.status_code == 200 and r.json().get("id") == alice_pub_id)

# 28. Alice 获取自己的私有笔记 → 200
r = get_note(alice_token, alice_priv_id)
check(28, "Alice 获取自己私有笔记 by ID → 200",
      r.status_code == 200 and r.json().get("id") == alice_priv_id)

# 29. Bob 获取 Alice 的公开笔记 by ID → 200
r = get_note(bob_token, alice_pub_id)
check(29, "Bob 获取 Alice 公开笔记 by ID → 200", r.status_code == 200)

# 30. Bob 获取 Alice 的私有笔记 by ID → 403
r = get_note(bob_token, alice_priv_id)
check(30, "Bob 获取 Alice 私有笔记 by ID → 403 Access Denied",
      r.status_code == 403, r.json().get("detail", ""))

# 31. 获取不存在的笔记 ID → 404
r = get_note(alice_token, "00000000-0000-0000-0000-000000000000")
check(31, "获取不存在的 note_id → 404", r.status_code == 404)

# 32. 无 token 获取笔记 → 401
r = requests.get(f"{BASE_URL}/notes/{alice_pub_id}")
check(32, "无 token 获取 note by ID → 401", r.status_code == 401)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 五、更新笔记 (33~39) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 33. Alice 更新自己笔记的标题 → 200
r = update_note(alice_token, alice_pub_id, title="Alice Public Note (Updated)")
check(33, "Alice 更新自己笔记标题 → 200",
      r.status_code == 200 and "Updated" in r.json().get("title", ""),
      f"new title: {r.json().get('title','')}")

# 34. Alice 更新自己笔记的 body → 200
r = update_note(alice_token, alice_pub_id, body="Updated body content")
check(34, "Alice 更新自己笔记 body → 200",
      r.status_code == 200 and r.json().get("body") == "Updated body content")

# 35. Alice 将公开笔记改为私有 → 200
r = update_note(alice_token, alice_pub_id, visibility="private")
check(35, "Alice 将公开笔记改为私有 → 200",
      r.status_code == 200 and r.json().get("visibility") == "private")

# 36. Alice 将私有笔记改回公开 → 200
r = update_note(alice_token, alice_pub_id, visibility="public")
check(36, "Alice 将私有笔记改回公开 → 200",
      r.status_code == 200 and r.json().get("visibility") == "public")

# 37. Bob 尝试修改 Alice 的笔记 → 403
r = update_note(bob_token, alice_pub_id, title="Hacked!")
check(37, "Bob 尝试修改 Alice 的笔记 → 403 Access Denied",
      r.status_code == 403, r.json().get("detail", ""))

# 38. 更新为纯空白标题 → 422/400
r = update_note(alice_token, alice_pub_id, title="   ")
check(38, "更新为纯空白标题 → 422/400（whitespace 拦截）",
      r.status_code in (400, 422),
      f"got {r.status_code}")

# 39. 更新不存在的笔记 → 404
r = update_note(alice_token, "00000000-0000-0000-0000-000000000000", title="Ghost")
check(39, "更新不存在的 note → 404", r.status_code == 404)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 六、删除笔记 (40~45) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 先创建一个临时笔记供删除用
r = create_note(alice_token, "Alice Temp Note To Delete", "will be deleted")
alice_del_id = r.json().get("id", "") if r.status_code == 201 else ""

# 40. Bob 尝试删除 Alice 的笔记 → 403
r = delete_note(bob_token, alice_del_id)
check(40, "Bob 尝试删除 Alice 的笔记 → 403", r.status_code == 403)

# 41. Alice 删除自己的笔记 → 204
r = delete_note(alice_token, alice_del_id)
check(41, "Alice 删除自己的笔记 → 204 No Content", r.status_code == 204)

# 42. 验证已删除的笔记不可访问 → 404
r = get_note(alice_token, alice_del_id)
check(42, "已删除笔记 GET → 404（确认消失）", r.status_code == 404)

# 43. 再次删除同一笔记 → 404
r = delete_note(alice_token, alice_del_id)
check(43, "重复删除 → 404 Not Found", r.status_code == 404)

# 44. Alice 删除自己的私有笔记 → 204
r = create_note(alice_token, "Alice Private To Delete", "secret", "private")
del_priv_id = r.json().get("id", "") if r.status_code == 201 else ""
r = delete_note(alice_token, del_priv_id)
check(44, "Alice 删除自己私有笔记 → 204", r.status_code == 204)

# 45. Bob 删除自己的笔记 → 204
r = create_note(bob_token, "Bob Note To Delete", "bye")
bob_del_id = r.json().get("id", "") if r.status_code == 201 else ""
r = delete_note(bob_token, bob_del_id)
check(45, "Bob 删除自己的笔记 → 204", r.status_code == 204)

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 七、隐私隔离与可见性切换 (46~50) ━━━")
# ════════════════════════════════════════════════════════════════════════════

# 46. Alice 把笔记改为私有 → Bob 的列表中消失
r = update_note(alice_token, alice_pub_id, visibility="private")
r2 = list_notes(bob_token)
bob_ids = [n["id"] for n in safe_json(r2).get("notes", [])]
check(46, "Alice 笔记改私有后 → 从 Bob 列表消失",
      r.status_code == 200 and alice_pub_id not in bob_ids,
      f"update={r.status_code} list={r2.status_code} 隐藏={'✅' if alice_pub_id not in bob_ids else '❌'}")

# 47. Alice 把笔记改为私有 → Bob by ID 获取 → 403
r = get_note(bob_token, alice_pub_id)
check(47, "Alice 笔记私有后 → Bob by ID 获取 → 403",
      r.status_code == 403, f"got {r.status_code}")

# 48. Alice 把笔记改回公开 → Bob 列表重新出现
r = update_note(alice_token, alice_pub_id, visibility="public")
r2 = list_notes(bob_token)
bob_ids = [n["id"] for n in safe_json(r2).get("notes", [])]
check(48, "Alice 笔记改回公开后 → 重新出现在 Bob 列表",
      r.status_code == 200 and alice_pub_id in bob_ids,
      f"update={r.status_code} list={r2.status_code} 可见={'✅' if alice_pub_id in bob_ids else '❌'}")

# 49. Alice 始终能看到自己的私有笔记（在自己列表中）
r = list_notes(alice_token)
alice_ids = [n["id"] for n in safe_json(r).get("notes", [])]
check(49, "Alice 始终能看到自己的私有笔记（列表中）",
      alice_priv_id in alice_ids,
      f"私有笔记{'可见✅' if alice_priv_id in alice_ids else '消失❌'}")

# 50. Bob 的私有笔记始终对 Alice 不可见（列表 + by ID 双重验证）
r1 = list_notes(alice_token)
alice_ids = [n["id"] for n in safe_json(r1).get("notes", [])]
r2 = get_note(alice_token, bob_priv_id)
check(50, "Bob 私有笔记：Alice 列表不可见 且 by ID → 403",
      bob_priv_id not in alice_ids and r2.status_code == 403,
      f"列表隐藏={'✅' if bob_priv_id not in alice_ids else '❌'}  ID访问={r2.status_code}")

# ════════════════════════════════════════════════════════════════════════════
print("\n━━━ 汇总 ━━━")
# ════════════════════════════════════════════════════════════════════════════
passed = sum(results)
total = len(results)
failed = total - passed
print(f"\n总计：{total} 个场景")
print(f"  \033[32m✅ 通过：{passed}\033[0m")
if failed:
    print(f"  \033[31m❌ 失败：{failed}\033[0m")
else:
    print("  🎉 全部通过！")

# 列出失败的序号
failed_nums = [i + 1 for i, r in enumerate(results) if not r]
if failed_nums:
    print(f"\n失败场景编号：{failed_nums}")

sys.exit(0 if failed == 0 else 1)
