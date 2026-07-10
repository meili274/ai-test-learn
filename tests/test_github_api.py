# tests/test_github_api.py
"""GitHub API 传统测试 — 真实业务接口"""
import allure
import pytest
from config.github_config import TEST_USER, TEST_USER2, TEST_REPO_OWNER, TEST_REPO_NAME


@allure.feature("GitHub API")
@allure.story("仓库搜索")
class TestSearchRepo:
    """搜索仓库接口"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("搜索 python testing 相关仓库")
    def test_search_python_testing(self, github_api_client):
        response = github_api_client.get("/search/repositories",
                                         params={"q": "python testing", "per_page": 5})
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) > 0
        assert data["total_count"] > 0
        # 验证返回的仓库包含必要字段
        first_item = data["items"][0]
        assert "full_name" in first_item
        assert "html_url" in first_item
        assert "stargazers_count" in first_item
        assert "language" in first_item

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("搜索 ai agent 相关仓库")
    def test_search_ai_agent(self, github_api_client):
        response = github_api_client.get("/search/repositories",
                                         params={"q": "ai agent", "per_page": 5})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("搜索分页 — 每页10条")
    def test_search_pagination(self, github_api_client):
        response = github_api_client.get("/search/repositories",
                                         params={"q": "python", "per_page": 10, "page": 1})
        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        assert len(items) <= 10, f"应返回最多10条，实际返回{len(items)}条"


@allure.feature("GitHub API")
@allure.story("用户信息")
class TestUser:
    """用户信息接口"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("获取知名用户 torvalds 的信息")
    def test_get_user_torvalds(self, github_api_client):
        response = github_api_client.get(f"/users/{TEST_USER}")
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "torvalds"
        assert "id" in data
        assert "public_repos" in data
        assert "followers" in data
        assert data["followers"] > 0, "Linus 不可能没有关注者"

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("获取 FastAPI 作者 tiangolo 的信息")
    def test_get_user_tiangolo(self, github_api_client):
        response = github_api_client.get(f"/users/{TEST_USER2}")
        assert response.status_code == 200
        data = response.json()
        assert data["login"] == "tiangolo"
        assert data["public_repos"] > 0

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("获取不存在的用户 — 应返回404")
    def test_get_nonexistent_user(self, github_api_client):
        response = github_api_client.get("/users/this-user-does-not-exist-999999")
        assert response.status_code == 404


@allure.feature("GitHub API")
@allure.story("仓库详情")
class TestRepo:
    """仓库详情接口"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("获取 fastapi/fastapi 仓库详情")
    def test_get_repo_info(self, github_api_client):
        response = github_api_client.get(f"/repos/{TEST_REPO_OWNER}/{TEST_REPO_NAME}")
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "fastapi/fastapi"
        assert data["stargazers_count"] > 10000, "FastAPI 不可能少于1万 star"
        assert "language" in data
        assert "description" in data
        assert "topics" in data

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("获取仓库的编程语言统计")
    def test_get_repo_languages(self, github_api_client):
        response = github_api_client.get(f"/repos/{TEST_REPO_OWNER}/{TEST_REPO_NAME}/languages")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert "Python" in data, "FastAPI 主要语言应该是 Python"


@allure.feature("GitHub API")
@allure.story("限流检测")
class TestRateLimit:
    """Rate Limit 限流检测"""

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("检测 Rate Limit 剩余次数")
    def test_rate_limit(self, github_api_client):
        response = github_api_client.get("/rate_limit")
        assert response.status_code == 200
        data = response.json()
        core = data["resources"]["core"]
        assert core["limit"] > 0
        # 未认证模式：60次/小时
        # 认证模式：5000次/小时
        remaining = core["remaining"]
        limit = core["limit"]
        allure.attach(
            f"总配额: {limit}/小时\n剩余: {remaining}\n重置时间: {core['reset']}",
            name="Rate Limit 状态",
            attachment_type=allure.attachment_type.TEXT
        )
        # 确保还剩一些额度
        assert remaining > 0, "API 额度已用完！"
