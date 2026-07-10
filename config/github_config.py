# config/github_config.py
"""GitHub API 专属配置"""

GITHUB_BASE_URL = "https://api.github.com"

TIMEOUT = 15

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "AI-Test-Framework/1.0"  # GitHub 强制要求，否则 403
}

# GitHub 免费额度：未认证 60次/小时，认证后 5000次/小时
RATE_LIMIT_WARNING = 50
RATE_LIMIT_CRITICAL = 55

# 测试用的知名开源作者
TEST_USER = "torvalds"           # Linus Torvalds — Linux 之父
TEST_USER2 = "tiangolo"          # FastAPI 作者

# 测试用的知名仓库
TEST_REPO_OWNER = "fastapi"
TEST_REPO_NAME = "fastapi"

# AI 搜索测试关键词
SEARCH_KEYWORDS = ["python testing", "ai agent", "machine learning"]
