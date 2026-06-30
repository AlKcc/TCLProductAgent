@echo off
REM ============================================
REM TCL智能产品咨询助手 - Windows启动脚本
REM ============================================

echo =========================================
echo   TCL智能产品咨询助手
echo =========================================
echo.

REM ------------------------------
REM 检查Python环境
REM ------------------------------
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.12或更高版本
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM ------------------------------
REM 检查依赖包
REM ------------------------------
echo 检查依赖包...
python -c "import langchain, zhipuai, chromadb, gradio" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 依赖包已安装
) else (
    echo ❌ 依赖包未安装，正在安装...
    pip install -r requirements.txt
    if %errorlevel% equ 0 (
        echo ✅ 依赖包安装成功
    ) else (
        echo ❌ 依赖包安装失败，请手动执行:
        echo    pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM ------------------------------
REM 检查环境变量配置
REM ------------------------------
echo.
echo 检查环境配置...

if exist .env (
    echo ✅ 环境变量文件存在
) else (
    echo ❌ 错误: .env文件不存在
    echo.
    echo 请按以下步骤配置:
    echo 1. copy .env.example .env
    echo 2. 编辑.env文件，配置API密钥和模型参数
    pause
    exit /b 1
)

REM ------------------------------
REM 创建必要的目录
REM ------------------------------
echo.
echo 创建数据目录...
if not exist logs mkdir logs
if not exist data\vectorstore mkdir data\vectorstore
echo ✅ 目录准备完成

REM ------------------------------
REM 打印启动信息
REM ------------------------------
echo.
echo =========================================
echo 启动应用...
echo =========================================
echo.
echo 📡 访问地址: http://localhost:7860
echo ⏹️  按 Ctrl+C 停止服务
echo.
echo 🔍 使用提示:
echo    - 产品查询: TCL电视保修政策是什么？
echo    - 产品推荐: 推荐一款5000元左右的电视
echo    - 产品对比: Q10L和T7H哪个好？
echo    - 故障排查: 电视开机没反应怎么办？
echo    - 问候寒暄: 你好
echo.

REM ------------------------------
REM 启动应用
REM ------------------------------
python src\app.py

pause