# api/api_client.py
"""封装 HTTP 请求方法"""
import requests
from config.config import BASE_URL, TIMEOUT, HEADERS


class ApiClient:
    """通用 API 客户端"""

    def __init__(self, base_url=None, headers=None, timeout=None):
        self.base_url = base_url or BASE_URL
        self.headers = headers or HEADERS
        self.timeout = timeout or TIMEOUT

    def get(self, endpoint, params=None):
        """发送 GET 请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
        return response

    def post(self, endpoint, data=None):
        """发送 POST 请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, json=data, headers=self.headers, timeout=self.timeout)
        return response

    def put(self, endpoint, data=None):
        """发送 PUT 请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, json=data, headers=self.headers, timeout=self.timeout)
        return response

    def delete(self, endpoint):
        """发送 DELETE 请求"""
        url = f"{self.base_url}{endpoint}"
        response = requests.delete(url, headers=self.headers, timeout=self.timeout)
        return response
