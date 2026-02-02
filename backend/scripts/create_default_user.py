#!/usr/bin/env python3
"""
创建默认用户
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import create_engine, text
from app.core.config import settings

def create_default_user():
    """创建默认用户"""
    try:
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # 检查用户是否已存在
            result = conn.execute(text("SELECT id FROM users WHERE id = 1"))
            if result.fetchone():
                print("ℹ️  默认用户 (ID=1) 已存在")
                return

            # 生成简单的哈希密码（使用 bcrypt 生成器）
            import bcrypt
            password = b"password123"
            hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')

            conn.execute(text("""
                INSERT INTO users (id, email, hashed_password, full_name, is_active, is_premium)
                VALUES (1, 'admin@example.com', :password, 'Admin User', 1, 0)
            """), {"password": hashed})

            conn.commit()

            print("✅ 默认用户创建成功！")
            print("   邮箱: admin@example.com")
            print("   密码: password123")

        engine.dispose()

    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_default_user()
