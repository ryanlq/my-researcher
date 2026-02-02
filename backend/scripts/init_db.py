#!/usr/bin/env python3
"""
数据库初始化脚本（支持 pgvector）
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings
from app.models.database import Base


def check_pgvector_extension(engine):
    """检查并创建 pgvector 扩展"""
    if not settings.DATABASE_URL.startswith("postgresql"):
        print("ℹ️  非 PostgreSQL 数据库，跳过 pgvector 检查")
        return True

    try:
        with engine.connect() as conn:
            # 检查 pgvector 扩展是否存在
            result = conn.execute(text(
                "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
            ))

            if result.fetchone():
                print("✅ pgvector 扩展已安装")
                return True
            else:
                print("⚠️  pgvector 扩展未安装")
                print("💡 安装方法:")
                print("   - Ubuntu/Debian: sudo apt-get install postgresql-16-pgvector")
                print("   - macOS: brew install pgvector")
                print("   - 或在数据库中执行: CREATE EXTENSION vector;")

                # 尝试创建扩展
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                    print("✅ pgvector 扩展创建成功")
                    return True
                except Exception as e:
                    print(f"⚠️  无法创建扩展: {e}")
                    print("💡 请手动安装 pgvector 扩展")
                    return False

    except Exception as e:
        print(f"❌ 检查 pgvector 时出错: {e}")
        return False


def init_database():
    """初始化数据库"""

    print("="*60)
    print("数据库初始化")
    print("="*60 + "\n")

    print(f"📋 数据库类型: {settings.DATABASE_URL.split(':')[0] if ':' in settings.DATABASE_URL else 'sqlite'}")
    print(f"📋 连接地址: {settings.DATABASE_URL}")
    print()

    try:
        # 创建引擎
        engine = create_engine(settings.DATABASE_URL)

        print("🔍 检查数据库连接...")
        with engine.connect() as conn:
            print("✅ 数据库连接成功")

        print()

        # 检查 pgvector 扩展
        pgvector_ok = check_pgvector_extension(engine)
        print()

        # 检查现有表
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if existing_tables:
            print(f"📊 已存在的表: {', '.join(existing_tables)}")

            # 非交互模式：默认不删除
            if len(sys.argv) > 1 and sys.argv[1] == "--force":
                print("🗑️  删除所有表 (--force 模式)...")
                Base.metadata.drop_all(bind=engine)
            else:
                print("ℹ️  保留现有表")
                print("💡 如需重新创建，请使用: python scripts/init_db.py --force")

        print()

        # 创建所有表
        print("🔨 创建数据库表...")
        Base.metadata.create_all(bind=engine)

        # 检查新创建的表
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()

        print(f"✅ 数据库初始化完成！")
        print(f"📋 数据表: {', '.join(new_tables)}")

        # 如果使用 pgvector，显示额外信息
        if pgvector_ok and settings.DATABASE_URL.startswith("postgresql"):
            print()
            print("✨ pgvector 功能可用")
            print("💡 知识库功能已启用，可以上传文档并进行语义搜索")

        print()
        print("="*60)
        print("🎉 数据库已就绪！")
        print("="*60)

        engine.dispose()

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        print("\n💡 提示:")
        print("   1. 确保已安装 PostgreSQL")
        print("   2. 确保数据库服务正在运行")
        print("   3. 检查 .env 中的 DATABASE_URL 配置")
        print("   4. 如使用 PostgreSQL，确保数据库已创建")
        print()
        print("   快速启动:")
        print("   python scripts/verify_pgvector.py")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
