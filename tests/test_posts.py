# tests/test_posts.py
"""测试 Posts 相关接口（Allure 增强版）"""
import allure


@allure.feature("Posts API")
@allure.story("帖子CRUD操作")
class TestPosts:
    """帖子接口测试集"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("获取帖子列表")
    def test_get_posts_list(self, api_client):
        """测试获取帖子列表"""
        with allure.step("发送 GET /posts 请求"):
            response = api_client.get("/posts")
        with allure.step("验证状态码为 200"):
            assert response.status_code == 200
        with allure.step("验证返回的是非空列表"):
            assert isinstance(response.json(), list)
            assert len(response.json()) > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("获取单篇帖子 — ID=1")
    def test_get_single_post(self, api_client):
        """测试获取单篇帖子"""
        response = api_client.get("/posts/1")
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "body" in data
        assert data["id"] == 1

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("创建新帖子")
    def test_create_post(self, api_client):
        """测试创建新帖子"""
        from utils.data_factory import generate_post
        with allure.step("生成随机测试数据"):
            new_post = generate_post()
            allure.attach(str(new_post), name="请求体", attachment_type=allure.attachment_type.JSON)

        with allure.step("发送 POST /posts 请求"):
            response = api_client.post("/posts", data=new_post)

        with allure.step("验证状态码为 201 且返回了 id"):
            assert response.status_code == 201
            data = response.json()
            assert "id" in data

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("更新帖子 — ID=1")
    def test_update_post(self, api_client):
        """测试更新帖子"""
        updated_data = {"title": "更新后的标题", "body": "更新后的内容", "userId": 1}
        response = api_client.put("/posts/1", data=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新后的标题"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("删除帖子 — ID=1")
    def test_delete_post(self, api_client):
        """测试删除帖子"""
        response = api_client.delete("/posts/1")
        assert response.status_code == 200
