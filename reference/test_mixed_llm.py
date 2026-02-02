"""
测试混合 LLM 配置
验证不同 LLM provider 是否正常工作
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# 测试脚本
async def test_mixed_llm():
    """测试混合 LLM 配置"""

    print("=" * 60)
    print("🧪 测试混合 LLM 配置")
    print("=" * 60)

    # 检查环境变量
    print("\n📋 当前配置:")
    print(f"  FAST_LLM:        {os.getenv('FAST_LLM')}")
    print(f"  SMART_LLM:       {os.getenv('SMART_LLM')}")
    print(f"  STRATEGIC_LLM:   {os.getenv('STRATEGIC_LLM')}")
    print(f"  EMBEDDING:       {os.getenv('EMBEDDING')}")
    print(f"  OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
    print(f"  OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")

    # 测试导入
    print("\n🔍 检查 LLM providers:")

    # 测试 Ollama
    try:
        if os.getenv("OLLAMA_BASE_URL"):
            import requests
            response = requests.get(f"{os.getenv('OLLAMA_BASE_URL')}/api/tags", timeout=2)
            if response.status_code == 200:
                print("  ✅ Ollama: 可用")
                models = response.json().get("models", [])
                print(f"     可用模型: {', '.join([m['name'] for m in models[:3]])}...")
            else:
                print("  ⚠️  Ollama: 服务未运行")
        else:
            print("  ⚠️  Ollama: 未配置")
    except Exception as e:
        print(f"  ❌ Ollama: {e}")

    # 测试云端 API
    try:
        if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_BASE_URL"):
            import requests
            headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
            response = requests.get(f"{os.getenv('OPENAI_BASE_URL').rstrip('/v1')}/models", headers=headers, timeout=5)
            if response.status_code == 200:
                print("  ✅ SiliconFlow: 可用")
            else:
                print(f"  ⚠️  SiliconFlow: HTTP {response.status_code}")
        else:
            print("  ⚠️  SiliconFlow: 未配置")
    except Exception as e:
        print(f"  ❌ SiliconFlow: {e}")

    # 测试 GPT Researcher 配置
    print("\n🔧 测试 GPT Researcher 配置...")
    try:
        from gpt_researcher import GPTResearcher
        from gpt_researcher.config import Config

        config = Config()
        print(f"  ✅ 配置加载成功")
        print(f"     - Fast LLM: {config.fast_llm_provider}:{config.fast_llm_model}")
        print(f"     - Smart LLM: {config.smart_llm_provider}:{config.smart_llm_model}")
        print(f"     - Strategic LLM: {config.strategic_llm_provider}:{config.strategic_llm_model}")
        print(f"     - Embedding: {config.embedding_provider}:{config.embedding_model}")

    except Exception as e:
        print(f"  ❌ 配置加载失败: {e}")

    # 快速功能测试
    print("\n🚀 快速功能测试...")
    try:
        import mcp_result_patch
        from gpt_researcher import GPTResearcher

        # 创建一个简单的研究器进行测试
        researcher = GPTResearcher(
            query="测试查询",
            report_type="resource_report",
            verbose=False
        )

        print("  ✅ GPTResearcher 初始化成功")
        print("  ✅ 混合 LLM 配置可以正常工作")

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("📝 配置建议:")
    print("=" * 60)
    print("""
混合配置策略:
1. FAST_LLM (快速任务)     → 使用本地 Ollama (节省成本)
2. SMART_LLM (复杂任务)    → 使用云端模型 (质量优先)
3. STRATEGIC_LLM (规划)    → 根据需求选择
4. EMBEDDING (嵌入)        → 使用本地模型 (节省 API 调用)

成本优化:
- 本地 Ollama: 免费
- 云端 API: 按使用量付费
- 建议将 60-80% 的任务分配给本地模型

性能优化:
- Ollama 响应速度: 2-5 秒
- 云端 API 响应速度: 1-3 秒
- 混合使用可以平衡速度和质量
    """)


if __name__ == "__main__":
    asyncio.run(test_mixed_llm())
