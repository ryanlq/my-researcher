#!/bin/bash

# GPT-Researcher 一键启动脚本
# 适用于 Linux/macOS

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID 文件
BACKEND_PID_FILE="$PROJECT_ROOT/.backend.pid"
FRONTEND_PID_FILE="$PROJECT_ROOT/.frontend.pid"

# 日志文件
BACKEND_LOG="$PROJECT_ROOT/logs/backend.log"
FRONTEND_LOG="$PROJECT_ROOT/logs/frontend.log"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  GPT-Researcher 一键启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 函数：检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 函数：创建日志目录
setup_logs() {
    mkdir -p "$PROJECT_ROOT/logs"
}

# 函数：检查环境变量
# check_env() {
#     echo -e "${YELLOW}[检查]${NC} 检查环境变量..."

#     if [ ! -f "$PROJECT_ROOT/.env" ]; then
#         echo -e "${RED}[错误]${NC} 未找到 .env 文件"
#         echo -e "${YELLOW}提示:${NC} 请复制 .env.example 到 .env 并配置环境变量"
#         echo -e "  cp .env.example .env"
#         exit 1
#     fi

#     echo -e "${GREEN}[✓]${NC} 环境变量检查通过"
# }

# 函数：检查依赖
check_dependencies() {
    echo -e "${YELLOW}[检查]${NC} 检查依赖..."

    # 检查 Python
    if ! command_exists python3 && ! command_exists python; then
        echo -e "${RED}[错误]${NC} 未找到 Python，请先安装 Python 3.10+"
        exit 1
    fi

    # 检查 Node.js
    if ! command_exists node && ! command_exists nodejs; then
        echo -e "${RED}[错误]${NC} 未找到 Node.js，请先安装 Node.js 18+"
        exit 1
    fi

    # 检查 pnpm
    if ! command_exists pnpm; then
        echo -e "${YELLOW}[警告]${NC} 未找到 pnpm，尝试使用 npm..."
        if ! command_exists npm; then
            echo -e "${RED}[错误]${NC} 未找到 npm，请先安装 Node.js"
            exit 1
        fi
        USE_PNPM=false
    else
        USE_PNPM=true
    fi

    echo -e "${GREEN}[✓]${NC} 依赖检查通过"
}

# 函数：安装后端依赖
install_backend_deps() {
    echo -e "${YELLOW}[后端]${NC} 检查并安装依赖..."
    cd "$BACKEND_DIR"

    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}[后端]${NC} 创建虚拟环境..."
        python3 -m venv venv
    fi

    echo -e "${YELLOW}[后端]${NC} 激活虚拟环境并安装依赖..."
    . venv/bin/activate
    pip install -q -r requirements.txt

    echo -e "${GREEN}[✓]${NC} 后端依赖安装完成"
}

# 函数：安装前端依赖
install_frontend_deps() {
    echo -e "${YELLOW}[前端]${NC} 检查并安装依赖..."
    cd "$FRONTEND_DIR"

    if [ "$USE_PNPM" = true ]; then
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}[前端]${NC} 使用 pnpm 安装依赖..."
            pnpm install
        fi
    else
        if [ ! -d "node_modules" ]; then
            echo -e "${YELLOW}[前端]${NC} 使用 npm 安装依赖..."
            npm install
        fi
    fi

    echo -e "${GREEN}[✓]${NC} 前端依赖安装完成"
}

# 函数：启动后端
start_backend() {
    echo -e "${YELLOW}[后端]${NC} 启动后端服务..."
    setup_logs

    cd "$BACKEND_DIR"

    # 检查是否已经在运行
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}[警告]${NC} 后端已在运行 (PID: $BACKEND_PID)"
            return
        fi
    fi

    # 启动后端
    . venv/bin/activate
    nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$BACKEND_PID_FILE"

    # 等待后端启动
    sleep 3

    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} 后端启动成功 (PID: $BACKEND_PID)"
        echo -e "      日志: $BACKEND_LOG"
        echo -e "      地址: ${BLUE}http://localhost:8000${NC}"
    else
        echo -e "${RED}[错误]${NC} 后端启动失败，请查看日志: $BACKEND_LOG"
        exit 1
    fi
}

# 函数：启动前端
start_frontend() {
    echo -e "${YELLOW}[前端]${NC} 启动前端服务..."
    setup_logs

    cd "$FRONTEND_DIR"

    # 检查是否已经在运行
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}[警告]${NC} 前端已在运行 (PID: $FRONTEND_PID)"
            return
        fi
    fi

    # 启动前端
    if [ "$USE_PNPM" = true ]; then
        nohup pnpm dev > "$FRONTEND_LOG" 2>&1 &
    else
        nohup npm run dev > "$FRONTEND_LOG" 2>&1 &
    fi
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$FRONTEND_PID_FILE"

    # 等待前端启动
    sleep 3

    if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓]${NC} 前端启动成功 (PID: $FRONTEND_PID)"
        echo -e "      日志: $FRONTEND_LOG"
        echo -e "      地址: ${BLUE}http://localhost:3000${NC}"
    else
        echo -e "${RED}[错误]${NC} 前端启动失败，请查看日志: $FRONTEND_LOG"
        exit 1
    fi
}

# 函数：停止服务
stop_services() {
    echo -e "${YELLOW}[停止]${NC} 停止所有服务..."

    # 停止后端
    if [ -f "$BACKEND_PID_FILE" ]; then
        BACKEND_PID=$(cat "$BACKEND_PID_FILE")
        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            kill $BACKEND_PID
            echo -e "${GREEN}[✓]${NC} 后端已停止"
        fi
        rm -f "$BACKEND_PID_FILE"
    fi

    # 停止前端
    if [ -f "$FRONTEND_PID_FILE" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
        if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
            kill $FRONTEND_PID
            echo -e "${GREEN}[✓]${NC} 前端已停止"
        fi
        rm -f "$FRONTEND_PID_FILE"
    fi
}

# 函数：查看日志
show_logs() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  选择要查看的日志${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo "1) 后端日志"
    echo "2) 前端日志"
    echo "3) 退出"
    echo ""
    read -p "请选择 [1-3]: " choice

    case $choice in
        1)
            if [ -f "$BACKEND_LOG" ]; then
                tail -f "$BACKEND_LOG"
            else
                echo -e "${RED}[错误]${NC} 后端日志文件不存在"
            fi
            ;;
        2)
            if [ -f "$FRONTEND_LOG" ]; then
                tail -f "$FRONTEND_LOG"
            else
                echo -e "${RED}[错误]${NC} 前端日志文件不存在"
            fi
            ;;
        3)
            exit 0
            ;;
        *)
            echo -e "${RED}[错误]${NC} 无效选择"
            exit 1
            ;;
    esac
}

# 主函数
main() {
    # 解析命令行参数
    case "${1:-start}" in
        start)
            # check_env
            check_dependencies
            install_backend_deps
            install_frontend_deps
            start_backend
            start_frontend

            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}  🎉 所有服务启动成功！${NC}"
            echo -e "${GREEN}========================================${NC}"
            echo -e "  后端: ${BLUE}http://localhost:8000${NC}"
            echo -e "  前端: ${BLUE}http://localhost:3000${NC}"
            echo -e "  API 文档: ${BLUE}http://localhost:8000/docs${NC}"
            echo ""
            echo -e "${YELLOW}其他命令:${NC}"
            echo -e "  停止服务: ${GREEN}./start.sh stop${NC}"
            echo -e "  重启服务: ${GREEN}./start.sh restart${NC}"
            echo -e "  查看日志: ${GREEN}./start.sh logs${NC}"
            echo ""
            ;;

        stop)
            stop_services
            ;;

        restart)
            stop_services
            sleep 2
            check_env
            check_dependencies
            start_backend
            start_frontend
            echo -e "${GREEN}[✓]${NC} 服务已重启"
            ;;

        logs)
            show_logs
            ;;

        status)
            echo -e "${BLUE}========================================${NC}"
            echo -e "${BLUE}  服务状态${NC}"
            echo -e "${BLUE}========================================${NC}"

            # 检查后端
            if [ -f "$BACKEND_PID_FILE" ]; then
                BACKEND_PID=$(cat "$BACKEND_PID_FILE")
                if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                    echo -e "后端: ${GREEN}运行中${NC} (PID: $BACKEND_PID)"
                else
                    echo -e "后端: ${RED}已停止${NC}"
                fi
            else
                echo -e "后端: ${RED}未运行${NC}"
            fi

            # 检查前端
            if [ -f "$FRONTEND_PID_FILE" ]; then
                FRONTEND_PID=$(cat "$FRONTEND_PID_FILE")
                if ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
                    echo -e "前端: ${GREEN}运行中${NC} (PID: $FRONTEND_PID)"
                else
                    echo -e "前端: ${RED}已停止${NC}"
                fi
            else
                echo -e "前端: ${RED}未运行${NC}"
            fi
            ;;

        *)
            echo "用法: $0 {start|stop|restart|logs|status}"
            echo ""
            echo "命令:"
            echo "  start   - 启动所有服务（默认）"
            echo "  stop    - 停止所有服务"
            echo "  restart - 重启所有服务"
            echo "  logs    - 查看日志"
            echo "  status  - 查看服务状态"
            exit 1
            ;;
    esac
}

# 捕获 Ctrl+C 信号
trap stop_services INT TERM

# 执行主函数
main "$@"
