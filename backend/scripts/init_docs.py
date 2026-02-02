#!/usr/bin/env python3
"""
初始化文档存储目录
"""

import os
from pathlib import Path

def init_document_dirs():
    """创建文档存储目录结构"""

    # 项目根目录
    project_root = Path(__file__).parent.parent
    backend_root = project_root / "backend"

    # 定义需要创建的目录
    dirs_to_create = [
        backend_root / "data" / "documents",  # 本地文档存储
        backend_root / "uploads",              # 临时上传目录
        backend_root / "data" / "temp",        # 临时处理目录
    ]

    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

    # 创建 .gitkeep 文件，确保空目录也能被git跟踪
    gitkeep_dirs = [
        backend_root / "data" / "documents",
        backend_root / "uploads",
    ]

    for dir_path in gitkeep_dirs:
        gitkeep_file = dir_path / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()
            print(f"✅ 创建 .gitkeep: {gitkeep_file}")

    print("\n✅ 文档存储目录初始化完成！")
    print(f"📁 文档存储路径: {backend_root / 'data' / 'documents'}")
    print(f"📁 上传临时路径: {backend_root / 'uploads'}")

if __name__ == "__main__":
    init_document_dirs()
