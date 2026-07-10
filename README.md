# AI 自动化测试框架

> 不止判断「接口通不通」，更让 AI 判断「数据合不合理」

## 项目简介

这是一个面向 **AI 自动化测试开发** 的完整实战项目，将传统 API 测试与深度学习语义判断结合。项目支持两大被测对象：

| 被测对象 | 说明 |
|---------|------|
| **JSONPlaceholder** | 公开 RESTful API，覆盖 CRUD 全流程 |
| **GitHub API** | 真实业务接口，测搜索/用户/仓库 |

## 核心亮点

```
传统测试：assert status_code == 200        → 浅层检查
AI测试：  让 DeepSeek 理解返回数据        → 深层语义判断
```

- **双模式 AI 判断**：Mock 规则引擎 + 真实 DeepSeek，零代码切换
- **Allure 高级报告**：Feature/Story/Severity 分组，失败自动附 JSON
- **GitHub Actions CI/CD**：每次推送自动跑测试，报告发布到 GitHub Pages
- **安全设计**：API Key 通过环境变量注入，`.gitignore` 防泄露

## 技术栈

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.12+ |
| 测试框架 | pytest 8.x |
| HTTP 客户端 | requests |
| 测试数据 | Faker（中文数据） |
| AI 模型 | DeepSeek（deepseek-chat） |
| 报告 | Allure 2.x + pytest-html |
| CI/CD | GitHub Actions |

## 目录结构

```
ai_api_test_framework/
├── config/
│   ├── config.py            # JSONPlaceholder 配置
│   └── github_config.py     # GitHub API 配置
├── api/
│   └── api_client.py        # 通用 HTTP 客户端（GET/POST/PUT/DELETE）
├── utils/
│   ├── ai_validator.py      # AI 判断引擎（Mock + 真实双模式）
│   └── data_factory.py      # Faker 自动生成测试数据
├── tests/
│   ├── test_posts.py        # 帖子接口 — 传统测试（5个）
│   ├── test_users.py        # 用户接口 — 传统测试（3个）
│   ├── test_posts_ai.py     # 帖子接口 — AI增强测试（8个）
│   ├── test_github_api.py   # GitHub API — 传统测试（9个）
│   └── test_github_ai.py    # GitHub API — AI增强测试（7个）
├── reports/                 # 测试报告输出目录
├── .github/workflows/
│   └── test.yml             # CI/CD 自动测试流水线
├── conftest.py              # pytest 全局配置 + Allure Hook
├── pytest.ini               # pytest 参数配置
├── run_ai_test.py           # AI 判断能力演示脚本
├── run_allure_report.bat    # 一键生成 Allure 报告
└── requirements.txt         # Python 依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key（可选）

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-your-key-here"

# Linux / macOS
export DEEPSEEK_API_KEY="sk-your-key-here"
```

> 不配置 Key 也能跑——AI 判断会自动降级为 Mock 模式

### 3. 运行测试

```bash
# 全量测试
pytest tests/ -v

# 只跑 AI 增强测试
pytest tests/test_posts_ai.py tests/test_github_ai.py -v

# 生成 Allure 报告（Windows）
run_allure_report.bat

# 生成 Allure 报告（macOS/Linux）
pytest tests/ --alluredir=reports/allure-results --clean-alluredir
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report
```

### 4. 看 AI 判断演示

```bash
python run_ai_test.py
```

## AI 判断能力演示

`run_ai_test.py` 构造 5 种场景，直观展示 AI 能发现哪些传统测试发现不了的问题：

| 场景 | 传统测试 | AI 测试 |
|------|---------|---------|
| 正常数据 | ✅ status_code=200 | ✅ 字段完整、数据合理 |
| 缺少字段 | ✅ status_code=200（漏过了！） | ❌ 缺少 body 字段 |
| 空列表 | ✅ status_code=200（漏过了！） | ❌ 返回空列表 |
| 非法邮箱 | ✅ status_code=200（漏过了！） | ❌ 邮箱格式不合法 |
| 数量不匹配 | ✅ 没检查数量 | ❌ 预期10个实际5个 |

## CI/CD

项目配置了 GitHub Actions 自动测试流水线：

```yaml
触发条件：
  - push 到 main 分支
  - Pull Request 到 main 分支
  - 每天凌晨 2:00 自动运行

流程：
  检出代码 → 安装依赖 → 安装 Allure CLI
  → 运行全量测试 → 生成 Allure 报告 → 上传报告
```

### 配置 GitHub Secrets

在仓库 Settings → Secrets and variables → Actions 中添加：

| Secret 名称 | 说明 |
|------------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 |

## 测试结果

全量 **32 个测试用例**，覆盖：

- JSONPlaceholder：16 个（传统 8 + AI增强 8）
- GitHub API：16 个（传统 9 + AI增强 7）

## 面试展示建议

1. **跑 `python run_ai_test.py`** — 30 秒展示 AI 测试价值
2. **打开 Allure 报告** — 展示 Feature/Story 分组 + 失败自动附件
3. **展示 GitHub Actions** — 证明你懂 CI/CD 工程化
4. **讲 AI 判断原理** — Mock 规则引擎 vs 真实大模型，Mock 能发现 80% 问题，真实 AI 覆盖剩余 20%

## License

MIT
