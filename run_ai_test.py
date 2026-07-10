# run_ai_test.py
"""AI 测试演示脚本 — 直观展示 Mock AI 判断的效果（无需 API Key）

运行：python run_ai_test.py
作用：让你一眼看懂 AI 在测试中到底做了什么
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.ai_validator import ai_validate_response, AI_MODE


def demo():
    print("=" * 60)
    print("  🤖 AI 自动化测试判断能力演示")
    print(f"  当前模式：{AI_MODE.upper()}（切换真实 AI：改 ai_validator.py 第一行）")
    print("=" * 60)

    # ====== 场景1：正常数据 ======
    print("\n📋 场景1：正常帖子列表")
    normal_data = [
        {"id": 1, "title": "Python入门指南", "body": "这是一篇Python教程...", "userId": 1},
        {"id": 2, "title": "AI测试入门", "body": "如何用AI提升测试效率...", "userId": 2},
    ]
    passed, reason = ai_validate_response(normal_data, "返回帖子列表，包含标题和正文")
    _print_result(passed, reason)

    # ====== 场景2：缺失字段 ======
    print("\n📋 场景2：帖子缺少 body 字段（Bug！）")
    bad_data = [
        {"id": 1, "title": "Python入门指南", "userId": 1},
    ]
    passed, reason = ai_validate_response(bad_data, "返回帖子列表，包含标题和正文")
    _print_result(passed, reason)

    # ====== 场景3：空数据 ======
    print("\n📋 场景3：返回了空列表（可能是Bug）")
    empty_data = []
    passed, reason = ai_validate_response(empty_data, "返回帖子列表，不为空")
    _print_result(passed, reason)

    # ====== 场景4：邮箱校验 ======
    print("\n📋 场景4：用户邮箱格式检查")
    user_data = [
        {"id": 1, "name": "张三", "email": "zhangsan@test.com"},       # 正常
        {"id": 2, "name": "李四", "email": "bad-email"},               # 格式错误
    ]
    passed, reason = ai_validate_response(user_data, "返回用户列表，邮箱格式要合法")
    _print_result(passed, reason)

    # ====== 场景5：数量检查 ======
    print("\n📋 场景5：接口说返回10个用户，实际只返回5个")
    five_users = [
        {"id": i, "name": f"用户{i}", "email": f"user{i}@test.com"}
        for i in range(1, 6)
    ]
    passed, reason = ai_validate_response(five_users, "返回10个用户")
    _print_result(passed, reason)

    # ====== 总结 ======
    print("\n" + "=" * 60)
    print("  💡 总结")
    print("=" * 60)
    print("""
  传统测试 = 检查状态码 + 字段存在 → 浅层检查
  AI测试   = 理解数据语义 + 发现逻辑问题 → 深层保障

  Mock 模式：用规则引擎模拟 AI 判断，快速演示效果
  真实模式：接入 DeepSeek/OpenAI，让大模型真正理解数据

  面试场景：
  "我们的测试框架不仅检验接口通不通，
   还会让 AI 判断返回的数据是不是合理，
   比如邮箱格式、数据完整性、业务逻辑一致性..." 
    """)
    print("=" * 60)


def _print_result(passed, reason):
    icon = "  ✅ PASS" if passed else "  ❌ FAIL"
    print(f"{icon}")
    print(f"  📝 {reason}")


if __name__ == "__main__":
    demo()
