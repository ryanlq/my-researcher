@echo off
REM GPT-Researcher 一键启动脚本 (Windows)
REM 适用于 Windows CMD / PowerShell

setlocal enabledelayedexpansion

REM 颜色设置（仅限 Windows 10+）
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM 项目根目录
set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"

REM PID 文件
set "BACKEND_PID_FILE=%PROJECT_ROOT%.backend.pid"
set "FRONTEND_PID_FILE=%PROJECT_ROOT%.frontend.pid"

echo ========================================
echo   GPT-Researcher 一键启动脚本
echo ========================================
echo.

REM 解析命令行参数
set "COMMAND=%~1"
if "%COMMAND%"=="" set "COMMAND=start"

if /i "%COMMAND%"=="start" goto :start
if /i "%COMMAND%"=="stop" goto :stop
if /i "%COMMAND%"=="restart" goto :restart
if /i "%COMMAND%"=="status" goto :status
goto :usage

:start
    echo %INFO% 检查环境变量...

    if not exist "%PROJECT_ROOT%.env" (
        echo %ERROR% 未找到 .env 文件
        echo %WARNING% 请复制 .env.example 到 .env 并配置环境变量
        echo           copy .env.example .env
        exit /b 1
    )

    echo %SUCCESS% 环境变量检查通过
    echo.

    echo %INFO% 启动后端服务...
    cd /d "%BACKEND_DIR%"

    if not exist "venv\" (
        echo %WARNING% 创建虚拟环境...
        python -m venv venv
    )

    call venv\Scripts\activate.bat

    if not exist "venv\Lib\site-packages\fastapi" (
        echo %INFO% 安装后端依赖...
        pip install -r requirements.txt
    )

    start /B cmd /c "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo %SUCCESS% 后端启动成功
    echo       地址: http://localhost:8000
    echo.

    echo %INFO% 启动前端服务...
    cd /d "%FRONTEND_DIR%"

    if not exist "node_modules\" (
        echo %INFO% 安装前端依赖...
        if exist "pnpm-lock.yaml" (
            call pnpm install
        ) else (
            call npm install
        )
    )

    start /B cmd /c "npm run dev"
    echo %SUCCESS% 前端启动成功
    echo       地址: http://localhost:3000
    echo.

    echo ========================================
    echo   🎉 所有服务启动成功！
    echo ========================================
    echo   后端: http://localhost:8000
    echo   前端: http://localhost:3000
    echo   API 文档: http://localhost:8000/docs
    echo.
    echo 其他命令:
    echo   停止服务: start.bat stop
    echo   重启服务: start.bat restart
    echo.
    goto :end

:stop
    echo %INFO% 停止所有服务...

    REM 停止后端
    taskkill /F /IM python.exe /FI "WINDOWTITLE eq uvicorn*" 2>nul
    if %errorlevel%==0 (
        echo %SUCCESS% 后端已停止
    )

    REM 停止前端
    taskkill /F /IM node.exe /FI "WINDOWTITLE eq *next-dev*" 2>nul
    if %errorlevel%==0 (
        echo %SUCCESS% 前端已停止
    )

    echo %SUCCESS% 所有服务已停止
    goto :end

:restart
    call :stop
    timeout /t 2 /nobreak >nul
    call :start
    goto :end

:status
    echo ========================================
    echo   服务状态
    echo ========================================

    REM 检查后端
    tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq uvicorn*" 2>nul | find /I "python.exe" >nul
    if %errorlevel%==0 (
        echo 后端: 运行中
    ) else (
        echo 后端: 未运行
    )

    REM 检查前端
    tasklist /FI "IMAGENAME eq node.exe" 2>nul | find /I "node.exe" >nul
    if %errorlevel%==0 (
        echo 前端: 运行中
    ) else (
        echo 前端: 未运行
    )
    goto :end

:usage
    echo 用法: %~nx0 {start^|stop^|restart^|status}
    echo.
    echo 命令:
    echo   start   - 启动所有服务（默认）
    echo   stop    - 停止所有服务
    echo   restart - 重启所有服务
    echo   status  - 查看服务状态
    exit /b 1

:end
    endlocal
