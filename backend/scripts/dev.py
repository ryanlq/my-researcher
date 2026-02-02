#!/usr/bin/env python3
"""开发服务器启动脚本"""

import sys
import os
import uvicorn
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings


def main():
    """启动开发服务器"""

    print("=" * 60)
    print(f"🚀 启动 {settings.APP_NAME}")
    print("=" * 60)
    print(f"📍 版本: {settings.APP_VERSION}")
    print(f"🌐 地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API 文档: http://{settings.HOST}:{settings.PORT}/api/v1/docs")
    print(f"🔍 ReDoc: http://{settings.HOST}:{settings.PORT}/api/v1/redoc")
    print(f"💚 健康检查: http://{settings.HOST}:{settings.PORT}/health")
    print("=" * 60)
    print("\n按 Ctrl+C 停止服务器\n")

    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info",
            # WebSocket 超时配置
            websocket_ping_interval=20,      # 每20秒发送一次心跳
            websocket_ping_timeout=60,       # 心跳超时60秒
            timeout_keep_alive=300,          # Keep-alive 超时5分钟
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
