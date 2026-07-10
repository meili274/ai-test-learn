@echo off
chcp 65001 >nul
echo ============================================
echo   Allure 测试报告一键运行
echo ============================================
echo.

:: ========================================
:: 配置你的 DeepSeek API Key
:: 方式1：设置为系统环境变量（推荐）
:: 方式2：在下面填入（不提交到 Git）
:: ========================================
if defined DEEPSEEK_API_KEY (
    echo [环境] 使用系统环境变量 DEEPSEEK_API_KEY
) else (
    echo [环境] 使用本地配置的 API Key
    set DEEPSEEK_API_KEY=sk-your-key-here
)
set AI_MODE=real

echo [1/3] 运行全部测试（生成 Allure 数据）...
call D:\anacond3\python.exe -m pytest tests/ -v --tb=short --alluredir=reports/allure-results --clean-alluredir
if %errorlevel% neq 0 (
    echo [警告] 部分测试失败，但仍然生成报告
)

echo.
echo [2/3] 生成 Allure HTML 报告...
if exist "reports\allure-report" rmdir /s /q "reports\allure-report"
D:\allure-2.13.4\bin\allure generate reports/allure-results -o reports/allure-report --clean
if %errorlevel% neq 0 (
    echo [错误] Allure 报告生成失败！
    pause
    exit /b 1
)

echo.
echo [3/3] 打开 Allure 报告...
start "" "reports\allure-report\index.html"

echo.
echo ============================================
echo   报告已打开！
echo   如果浏览器没弹出，手动打开：
echo   reports\allure-report\index.html
echo ============================================
pause
