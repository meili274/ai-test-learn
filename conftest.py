# conftest.py
"""pytest 全局夹具 + Allure 高级特性"""
import json
import os
import pytest
import allure
from api.api_client import ApiClient
from config.config import BASE_URL
from config.github_config import GITHUB_BASE_URL, HEADERS as GITHUB_HEADERS
from datetime import datetime

# 模块级变量：记录最后一次 API 响应
_last_response = None


# ======== 基础夹具 ========

@pytest.fixture(scope="session")
def api_client():
    """整个测试会话共用一个客户端"""
    client = ApiClient()
    if not hasattr(client, "_allure_wrapped"):
        _wrap_with_allure(client)
        client._allure_wrapped = True
    return client


@pytest.fixture(scope="session")
def github_api_client():
    """GitHub API 专用客户端（不同的 Base URL + User-Agent）"""
    client = ApiClient(base_url=GITHUB_BASE_URL, headers=GITHUB_HEADERS)
    if not hasattr(client, "_allure_wrapped"):
        _wrap_with_allure(client)
        client._allure_wrapped = True
    return client


def _wrap_with_allure(client):
    """给 ApiClient 的方法包裹 Allure 步骤记录"""
    for method_name in ["get", "post", "put", "delete"]:
        original = getattr(client, method_name)

        def make_wrapper(name, orig):
            def wrapper(endpoint, *args, **kwargs):
                with allure.step(f"{name.upper()} {endpoint}"):
                    response = orig(endpoint, *args, **kwargs)
                    global _last_response
                    _last_response = response
                    return response
            return wrapper

        setattr(client, method_name, make_wrapper(method_name, original))


# ======== Allure 环境信息 ========

def pytest_configure(config):
    """测试开始前，写入 Allure 环境信息"""
    os.makedirs("reports/allure-results", exist_ok=True)

    with open("reports/allure-results/environment.properties", "w", encoding="utf-8") as f:
        f.write(f"BaseURL={BASE_URL}\n")
        f.write(f"Python=3.12.4\n")
        f.write(f"Framework=pytest + Allure\n")
        f.write(f"AI=DeepSeek-chat\n")
        f.write(f"Time={datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


# ======== Allure 失败时自动附加接口响应 ========

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        with allure.step("失败详情"):
            global _last_response
            resp = _last_response
            if resp:
                try:
                    body = json.dumps(resp.json(), ensure_ascii=False, indent=2)
                    allure.attach(body, name=f"接口返回 (HTTP {resp.status_code})",
                                  attachment_type=allure.attachment_type.JSON)
                except:
                    allure.attach(resp.text[:2000], name=f"接口返回 (HTTP {resp.status_code})",
                                  attachment_type=allure.attachment_type.TEXT)
