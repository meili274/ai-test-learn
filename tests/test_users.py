# tests/test_users.py
"""测试 Users 相关接口（Allure 增强版）"""
import allure


@allure.feature("Users API")
@allure.story("用户数据验证")
class TestUsers:
    """用户接口测试集"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("获取用户列表 — 应为10个用户")
    def test_get_users_list(self, api_client):
        """测试获取用户列表"""
        response = api_client.get("/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 10

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("获取单个用户 — ID=1")
    def test_get_single_user(self, api_client):
        """测试获取单个用户"""
        response = api_client.get("/users/1")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "email" in data

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("用户邮箱格式校验")
    def test_user_has_valid_email(self, api_client):
        """测试用户邮箱格式是否正确"""
        response = api_client.get("/users")
        users = response.json()
        bad_users = []
        for user in users:
            if "@" not in user["email"]:
                bad_users.append(user["id"])

        if bad_users:
            allure.attach(
                str(bad_users),
                name="邮箱异常的用户ID",
                attachment_type=allure.attachment_type.TEXT
            )
            assert False, f"用户 {bad_users} 的邮箱格式不正确"
