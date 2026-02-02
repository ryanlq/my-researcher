#!/usr/bin/env python3
"""
验证 PostgreSQL 和 pgvector 扩展
"""

import sys

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def test_postgresql_connection():
    """测试 PostgreSQL 连接"""
    configs = [
        # # 配置1: 默认用户，5432端口
        # {
        #     "host": "localhost",
        #     "port": 5432,
        #     "user": "postgres",
        #     "database": "postgres"
        # },
        # 配置2: 默认用户，5433端口
        {"host": "localhost", "port": 5433, "user": "postgres", "database": "postgres"},
        # # 配置3: 当前用户
        # {
        #     "host": "localhost",
        #     "port": 5432,
        #     "user": None,  # 使用当前系统用户
        #     "database": "postgres"
        # },
        # 配置4: 当前用户，5433端口
        {"host": "localhost", "port": 5433, "user": None, "database": "postgres"},
    ]

    print("🔍 正在测试 PostgreSQL 连接...\n")

    for i, config in enumerate(configs, 1):
        try:
            print(
                f"配置 {i}: {config['host']}:{config['port']} (用户: {config['user'] or '当前用户'})"
            )

            conn = psycopg2.connect(**config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # 获取版本
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"  ✅ 连接成功!")
            print(f"  📦 {version.split(',')[0]}")

            # 检查 pgvector 扩展
            cursor.execute(
                "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
            )
            result = cursor.fetchone()

            if result:
                print(f"  🎯 pgvector 扩展已安装: v{result[1]}")

                # 测试向量功能
                try:
                    cursor.execute(
                        "SELECT '[1,2,3]'::vector <-> '[4,5,6]'::vector AS distance;"
                    )
                    distance = cursor.fetchone()[0]
                    print(f"  ✅ 向量距离计算测试成功: {distance}")
                except Exception as e:
                    print(f"  ⚠️  向量功能测试失败: {e}")

            else:
                print(f"  ⚠️  pgvector 扩展未安装")
                print(f"  💡 安装方法:")
                print(
                    f"     - Ubuntu/Debian: sudo apt-get install postgresql-16-pgvector"
                )
                print(f"     - 或在数据库中: CREATE EXTENSION vector;")

            cursor.close()
            conn.close()

            print("\n" + "=" * 60)
            return True, config

        except psycopg2.OperationalError as e:
            print(f"  ❌ 连接失败: {str(e)[:50]}")
            print()
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            print()

    print("\n❌ 无法连接到 PostgreSQL")
    print("\n💡 请检查:")
    print("   1. PostgreSQL 服务是否运行")
    print("   2. 端口是否正确 (5432 或 5433)")
    print("   3. 用户权限是否正确")
    print("   4. 是否需要密码")

    return False, None


def main():
    """主函数"""
    print("=" * 60)
    print("PostgreSQL + pgvector 验证工具")
    print("=" * 60 + "\n")

    success, config = test_postgresql_connection()

    if success:
        print("\n" + "=" * 60)
        print("✅ 验证通过！可以使用 PostgreSQL + pgvector")
        print("=" * 60)

        print("\n📝 建议的环境变量配置:")
        if config["port"] == 5433:
            print(f"""
DATABASE_URL=postgresql://{config["user"] or "your_user"}:@localhost:{config["port"]}/gpt_researcher
""")
        else:
            print(f"""
DATABASE_URL=postgresql://{config["user"] or "your_user"}:@localhost:{config["port"]}/gpt_researcher
""")

        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 验证失败，请先配置 PostgreSQL")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
