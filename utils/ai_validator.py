# utils/ai_validator.py
"""AI 判断 API 测试结果 —— Mock 模式 + 真实 AI 双模式

切换方式：
  1. 申请 DeepSeek API Key（https://platform.deepseek.com）
  2. 把下方 AI_MODE 改成 "real"
  3. 填入 API_KEY
  4. 代码不用改，自动切换
"""
import json
import re
from openai import OpenAI

# ============ 配置区 ============
import os

AI_MODE = os.getenv("AI_MODE", "real")   # "mock" 模拟  |  "real" 真正调用 AI

# 真实 AI 配置
# API Key 从环境变量读取（安全最佳实践，避免硬编码泄露到 Git）
API_KEY = os.getenv("DEEPSEEK_API_KEY", "")  # 部署到 CI 时设置 GitHub Secrets
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com")

# ================================


def _init_client():
    """初始化 AI 客户端（只在 real 模式下初始化）"""
    if AI_MODE != "real":
        return None
    if not API_KEY:
        print("[AI] ⚠ 未配置 API_KEY，降级为 Mock 模式")
        return None
    try:
        return OpenAI(api_key=API_KEY, base_url=AI_BASE_URL)
    except Exception as e:
        print(f"[AI] ⚠ 初始化失败：{e}，降级为 Mock 模式")
        return None


_ai_client = _init_client()


# ======== Mock AI 判断逻辑 ========

def _mock_validate(response_json, expected_description):
    """模拟 AI 判断 —— 用规则引擎代替，效果足够演示 AI 的价值"""

    desc = expected_description
    issues = []

    # --- 处理非 JSON 数据 ---
    if isinstance(response_json, str):
        try:
            response_json = json.loads(response_json)
        except json.JSONDecodeError:
            return False, "FAIL：接口返回的不是合法的 JSON 数据"

    if not isinstance(response_json, (dict, list)):
        return False, f"FAIL：返回数据类型异常（期望 dict/list，实际 {type(response_json).__name__}）"

    # --- 1. 检查是否为列表 ---
    if "列表" in desc or "数组" in desc or "list" in desc.lower():
        if not isinstance(response_json, list):
            return False, f"FAIL：预期返回列表，实际返回 {type(response_json).__name__}"

        if "不为空" in desc or len(response_json) == 0:
            if len(response_json) == 0:
                issues.append(f"返回了空列表，预期有数据")

        # 检查每个元素是否包含指定字段
        field_checks = _extract_fields(desc)
        if response_json and isinstance(response_json[0], dict):
            missing = [f for f in field_checks if f not in response_json[0]]
            if missing:
                issues.append(f"列表中缺少字段：{', '.join(missing)}")

    # --- 2. 检查单个对象 ---
    elif isinstance(response_json, dict) and not isinstance(response_json, list):
        if "对象" in desc or "单" in desc or "id" in desc.lower():
            field_checks = _extract_fields(desc)
            missing = [f for f in field_checks if f not in response_json]
            if missing:
                issues.append(f"对象中缺少字段：{', '.join(missing)}")

    # --- 3. 检查邮箱格式 ---
    if "邮箱" in desc or "email" in desc.lower():
        if isinstance(response_json, list):
            bad_emails = []
            for i, item in enumerate(response_json):
                email = item.get("email", "")
                if email and not _is_valid_email(email):
                    bad_emails.append(f"[{i}] {email}")
            if bad_emails:
                issues.append(f"邮箱格式不合法：{'; '.join(bad_emails[:3])}")
        elif isinstance(response_json, dict):
            email = response_json.get("email", "")
            if email and not _is_valid_email(email):
                issues.append(f"邮箱格式不合法：{email}")

    # --- 4. 检查标题/内容非空 ---
    for keyword, field in [("标题", "title"), ("内容", "body"), ("名称", "name"),
                            ("title", "title"), ("body", "body"), ("name", "name")]:
        if keyword in desc.lower() and isinstance(response_json, dict) and field in response_json:
            if not response_json[field]:
                issues.append(f"字段 '{field}' 为空")
            elif isinstance(response_json[field], str) and len(response_json[field]) < 2:
                issues.append(f"字段 '{field}' 内容过短（'{response_json[field]}'），疑似异常")

    # --- 5. 检查状态码 / 创建操作 ---
    if "创建" in desc or "create" in desc.lower():
        if isinstance(response_json, dict) and "id" not in response_json:
            issues.append("创建操作未返回 id 字段")

    if "删除" in desc or "delete" in desc.lower():
        if isinstance(response_json, dict) and not response_json:
            issues.append("删除操作返回了空对象，这是正常的（模拟接口）")

    if "更新" in desc or "修改" in desc or "update" in desc.lower():
        if isinstance(response_json, dict):
            # 检查是否有数据变化
            if len(response_json) < 2:
                issues.append("更新后返回的数据字段偏少，可能需要检查")

    # --- 6. 数据量检查 ---
    count_match = re.search(r'(\d+)\s*(个|条|users|条数据)', desc)
    if count_match and isinstance(response_json, list):
        expected_count = int(count_match.group(1))
        actual_count = len(response_json)
        if actual_count != expected_count:
            issues.append(f"返回数量不符：预期 {expected_count}，实际 {actual_count}")

    # --- 汇总结果 ---
    if issues:
        return False, "FAIL：" + "；".join(issues)
    else:
        return True, "PASS：Mock AI 判断 — 返回数据结构与内容符合预期描述"


def _extract_fields(text):
    """从描述中提取期望的字段名"""
    fields = set()
    # 从引号中提取英文字段名（re.ASCII 排除中文）
    quoted = re.findall(r'["\'](\w+)["\']', text)
    fields.update(q for q in quoted if q.isascii())

    # 中英文常见字段
    common_fields = {
        "id": "id", "标题": "title", "内容": "body", "正文": "body",
        "邮箱": "email", "名字": "name", "用户名": "username", "电话": "phone",
        "网站": "website", "用户id": "userId", "帖子id": "postId"
    }
    for cn, en in common_fields.items():
        if cn in text:
            fields.add(en)

    return list(fields)


def _is_valid_email(email):
    """简单邮箱校验"""
    return bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email))


# ======== 统一入口 ========

def ai_validate_response(response_json, expected_description):
    """
    让 AI 判断接口返回结果是否符合预期（自动选择 Mock / 真实 AI）

    :param response_json: 接口返回的 JSON 数据 (dict/list)
    :param expected_description: 用中文描述预期结果，如 "返回帖子列表，每篇需有 title 和 body"
    :return: (是否通过, AI 判断说明)
    """
    if AI_MODE == "real" and _ai_client is not None:
        return _call_real_ai(response_json, expected_description)
    else:
        return _mock_validate(response_json, expected_description)


def _call_real_ai(response_json, expected_description):
    """调用真实 AI 判断（DeepSeek / OpenAI）"""
    prompt = f"""你是一个 API 测试工程师，请严格判断以下接口返回是否符合预期。

接口返回数据：
{json.dumps(response_json, ensure_ascii=False, indent=2)}

预期描述：
{expected_description}

要求：
- 只回答一行：PASS：符合预期 或 FAIL：不符合预期，原因是...
- 不要额外解释，不要换行
"""

    try:
        result = _ai_client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        answer = result.choices[0].message.content.strip()
        is_pass = answer.startswith("PASS")
        return is_pass, answer
    except Exception as e:
        # 真实 AI 挂了，自动降级 Mock
        print(f"[AI] 真实 AI 调用失败：{e}，自动降级为 Mock 判断")
        return _mock_validate(response_json, expected_description)


# ======== 调试入口 ========

if __name__ == "__main__":
    # 快速验证 Mock 判断逻辑
    print("=" * 50)
    print(f"当前模式：{AI_MODE.upper()}")
    print("=" * 50)

    # 测试用例
    test_cases = [
        (
            [{"id": 1, "title": "测试标题", "body": "测试内容"}],
            "返回帖子列表，包含标题和内容，不为空"
        ),
        (
            {"id": 1, "name": "张三", "email": "bad-email"},
            "返回用户对象，需要 name 和 email"
        ),
        (
            [{"id": 1, "name": "张三", "email": "zhang@test.com"}],
            "返回10个用户"
        ),
    ]

    for resp, desc in test_cases:
        passed, reason = ai_validate_response(resp, desc)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status} | {desc}")
        print(f"   → {reason}")
