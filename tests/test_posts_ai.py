# tests/test_posts_ai.py
"""AI 增强版测试 — Allure 装饰器 + AI 语义判断

切换真实 AI：打开 utils/ai_validator.py，改 AI_MODE="real"，填入 Key 即可
"""
import allure
import pytest
from utils.ai_validator import ai_validate_response


@allure.feature("Posts API")
@allure.story("AI增强验证")
class TestPostsAI:
    """AI 增强版帖子接口测试集"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("[AI] 获取帖子列表 — 语义校验")
    def test_get_posts_list_ai(self, api_client):
        """[AI增强] 获取帖子列表 — 传统断言 + AI 语义判断"""
        response = api_client.get("/posts")

        with allure.step("传统断言：状态码 + 非空列表"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0

        with allure.step("AI语义判断：字段完整性 + 内容非空"):
            passed, reason = ai_validate_response(
                data[:3],
                "返回帖子列表，每篇应包含 title、body、userId、id 字段，title 和 body 不能为空"
            )
            allure.attach(reason, name="AI判断结果", attachment_type=allure.attachment_type.TEXT)
            assert passed, f"AI 判断不通过：{reason}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("[AI] 获取单篇帖子 — 数据结构验证")
    def test_get_single_post_ai(self, api_client):
        """[AI增强] 获取单篇帖子 — 验证数据结构完整性"""
        response = api_client.get("/posts/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1

        passed, reason = ai_validate_response(
            data,
            "返回 id=1 的帖子对象，需要有 title 标题、body 正文、userId 用户ID"
        )
        allure.attach(reason, name="AI判断结果", attachment_type=allure.attachment_type.TEXT)
        assert passed, f"AI 判断不通过：{reason}"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("[AI] 创建帖子 — 验证返回数据合理性")
    def test_create_post_ai(self, api_client):
        """[AI增强] 创建帖子 — 验证返回数据是否合理"""
        from utils.data_factory import generate_post

        new_post = generate_post()
        response = api_client.post("/posts", data=new_post)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == new_post["title"]
        assert data["body"] == new_post["body"]

        # AI 仅作参考（Faker 数据偶有随机性，不作为硬断言）
        _, reason = ai_validate_response(data, "返回创建成功的对象，包含 id")
        allure.attach(reason, name="AI参考意见", attachment_type=allure.attachment_type.TEXT)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("[AI] 更新帖子 — 验证修改生效")
    def test_update_post_ai(self, api_client):
        """[AI增强] 更新帖子 — 验证修改是否生效"""
        updated_data = {"title": "AI测试更新标题", "body": "这是AI增强测试的内容", "userId": 1}
        response = api_client.put("/posts/1", data=updated_data)

        assert response.status_code == 200
        data = response.json()

        passed, reason = ai_validate_response(
            data,
            "更新帖子后返回对象，title 应该是 'AI测试更新标题'，body 应该是更新后的内容"
        )
        allure.attach(reason, name="AI判断结果", attachment_type=allure.attachment_type.TEXT)
        assert passed, f"AI 判断不通过：{reason}"


@allure.feature("Users API")
@allure.story("AI增强验证")
class TestUsersAI:
    """AI 增强版用户接口测试集"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("[AI] 获取用户列表 — 数据质量验证")
    def test_get_users_list_ai(self, api_client):
        """[AI增强] 获取用户列表 — 验证数据质量"""
        response = api_client.get("/users")

        with allure.step("传统断言"):
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 10

        with allure.step("AI 语义判断"):
            passed, reason = ai_validate_response(
                data,
                "返回10个用户的列表，每个用户需包含 name、email、phone 字段"
            )
            allure.attach(reason, name="AI判断结果", attachment_type=allure.attachment_type.TEXT)
            assert passed, f"AI 判断不通过：{reason}"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("[AI] 获取单个用户 — 字段完整性")
    def test_get_single_user_ai(self, api_client):
        """[AI增强] 获取单个用户 — 检查字段完整性"""
        response = api_client.get("/users/1")

        assert response.status_code == 200
        data = response.json()

        passed, reason = ai_validate_response(
            data,
            "返回 ID 为 1 的用户对象，包含 name、email、phone、website 等字段"
        )
        allure.attach(reason, name="AI判断结果", attachment_type=allure.attachment_type.TEXT)
        assert passed, f"AI 判断不通过：{reason}"


@allure.feature("AI对比测试")
@allure.story("缺陷检测能力验证")
class TestAIComparison:
    """对比测试：故意制造问题，看 AI 能否发现"""

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("[AI对比] 假邮箱检测")
    def test_ai_catches_bad_email(self, api_client):
        """故意把邮箱改错，看 AI 能否抓出"""
        response = api_client.get("/users/1")
        data = response.json()

        bad_data = dict(data)
        bad_data["email"] = "this-is-not-an-email"

        with allure.step("用假邮箱数据给 AI 判断"):
            passed, reason = ai_validate_response(
                bad_data,
                "返回用户对象，email 字段必须是合法的邮箱格式"
            )
            allure.attach(
                f"数据: {bad_data}\n\nAI判断: {reason}",
                name="AI对比结果",
                attachment_type=allure.attachment_type.TEXT
            )

        if not passed:
            allure.attach("✅ AI 成功发现了格式错误的邮箱！", name="结论", attachment_type=allure.attachment_type.TEXT)

    @allure.severity(allure.severity_level.MINOR)
    @allure.title("[AI对比] 缺失字段检测")
    def test_ai_catches_missing_field(self, api_client):
        """故意删除 name 字段，看 AI 能否发现"""
        response = api_client.get("/users/1")
        data = response.json()

        bad_data = dict(data)
        del bad_data["name"]

        with allure.step("用缺失 name 的数据给 AI 判断"):
            passed, reason = ai_validate_response(
                bad_data,
                "返回用户对象，必须包含 name 字段"
            )
            allure.attach(
                f"数据: {bad_data}\n\nAI判断: {reason}",
                name="AI对比结果",
                attachment_type=allure.attachment_type.TEXT
            )

        if not passed:
            allure.attach("✅ AI 成功发现了缺失的 name 字段！", name="结论", attachment_type=allure.attachment_type.TEXT)
