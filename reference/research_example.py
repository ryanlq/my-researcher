"""
GPT Researcher 使用示例

展示如何：
1. 配置自定义 OpenAI 兼容接口
2. 使用 MCP search 工具进行研究
"""

import asyncio
import os
from gpt_researcher import GPTResearcher


# ============================================
# 方法 1: 使用环境变量配置自定义 OpenAI 兼容接口
# ============================================

def example_with_custom_openai():
    """通过环境变量配置自定义 OpenAI 兼容接口"""

    # 设置自定义 OpenAI 兼容接口
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_BASE_URL"] = "https://your-custom-endpoint.com/v1"  # 自定义端点

    # 配置 LLM 模型
    os.environ["FAST_LLM"] = "openai:gpt-4o-mini"  # 或自定义模型名
    os.environ["SMART_LLM"] = "openai:gpt-4o"

    # 运行研究
    researcher = GPTResearcher(
        query="What are the latest developments in AI?",
        report_type="research_report",
    )

    report = asyncio.run(researcher.conduct_research())
    print(report)


# ============================================
# 方法 2: 通过配置文件配置
# ============================================

def example_with_config_file():
    """通过 JSON 配置文件配置"""

    # 创建配置文件 config.json
    config_content = """{
        "FAST_LLM": "openai:gpt-4o-mini",
        "SMART_LLM": "openai:gpt-4o",
        "EMBEDDING": "openai:text-embedding-3-small",
        "RETRIEVER": "tavily",
        "TEMPERATURE": 0.4
    }"""

    with open("config.json", "w") as f:
        f.write(config_content)

    # 设置环境变量（也可以在配置文件中指定）
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_BASE_URL"] = "https://your-custom-endpoint.com/v1"

    # 使用配置文件
    researcher = GPTResearcher(
        query="Latest developments in AI",
        config_path="config.json"
    )

    report = asyncio.run(researcher.conduct_research())
    print(report)


# ============================================
# 方法 3: 使用 MCP Search 工具
# ============================================

async def example_with_mcp_search():
    """使用 MCP search 工具进行研究"""

    # MCP 服务器配置
    mcp_configs = [
        {
            # 方式 1: 使用 stdio 连接本地 MCP 服务器
            "name": "searxng",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-searxng"],
            "env": {
                "SEARXNG_QUERY_URL": "https://your-searxng-instance.com/search"
            }
        },
        {
            # 方式 2: 使用 WebSocket 连接远程 MCP 服务器
            "name": "remote-search",
            "connection_url": "wss://your-mcp-server.com/ws",
            "connection_type": "websocket",
            "connection_token": "your-auth-token"  # 如果需要认证
        },
        {
            # 方式 3: 使用 HTTP 连接
            "name": "http-search",
            "connection_url": "https://your-mcp-server.com/mcp",
            "connection_type": "streamable_http"
        }
    ]

    # 使用 MCP 配置创建研究器
    researcher = GPTResearcher(
        query="What are the latest trends in renewable energy?",
        report_type="research_report",
        mcp_configs=mcp_configs,
        mcp_strategy="fast",  # 可选: "fast", "deep", "disabled"
        verbose=True
    )

    report = await researcher.conduct_research()
    print(report)


# ============================================
# 方法 4: 结合自定义 OpenAI 和 MCP Search
# ============================================

async def example_combined():
    """结合自定义 OpenAI 兼容接口和 MCP search 工具"""

    # 配置自定义 OpenAI 兼容接口
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    os.environ["OPENAI_BASE_URL"] = "https://your-custom-endpoint.com/v1"
    os.environ["FAST_LLM"] = "openai:gpt-4o-mini"
    os.environ["SMART_LLM"] = "openai:gpt-4o"

    # 配置 MCP search 工具（例如 searxng）
    mcp_configs = [
        {
            "name": "searxng",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-searxng"],
            "env": {
                "SEARXNG_QUERY_URL": "https://your-searxng-instance.com/search"
            }
        }
    ]

    # 创建研究器
    researcher = GPTResearcher(
        query="Latest breakthroughs in quantum computing",
        report_type="research_report",
        mcp_configs=mcp_configs,
        mcp_strategy="fast",
        verbose=True
    )

    # 执行研究
    report = await researcher.conduct_research()

    # 保存报告
    with open("research_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("Research completed! Report saved to research_report.md")
    return report


# ============================================
# 方法 5: 使用其他 OpenAI 兼容提供商示例
# ============================================

def example_ollama():
    """使用 Ollama 本地模型"""
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"
    os.environ["FAST_LLM"] = "ollama:llama3.2"
    os.environ["SMART_LLM"] = "ollama:llama3.2"

    researcher = GPTResearcher(query="Research topic here")
    report = asyncio.run(researcher.conduct_research())
    print(report)


def example_deepseek():
    """使用 DeepSeek API"""
    os.environ["DEEPSEEK_API_KEY"] = "your-deepseek-api-key"
    os.environ["FAST_LLM"] = "deepseek:deepseek-chat"
    os.environ["SMART_LLM"] = "deepseek:deepseek-reasoner"

    researcher = GPTResearcher(query="Research topic here")
    report = asyncio.run(researcher.conduct_research())
    print(report)


# ============================================
# 主函数
# ============================================

if __name__ == "__main__":
    # 选择要运行的示例
    import sys

    if len(sys.argv) > 1:
        example = sys.argv[1]
        if example == "custom_openai":
            example_with_custom_openai()
        elif example == "config_file":
            example_with_config_file()
        elif example == "mcp_search":
            asyncio.run(example_with_mcp_search())
        elif example == "combined":
            asyncio.run(example_combined())
        elif example == "ollama":
            example_ollama()
        elif example == "deepseek":
            example_deepseek()
        else:
            print(f"Unknown example: {example}")
    else:
        print("GPT Researcher 使用示例")
        print("=" * 50)
        print("\n运行方式:")
        print("  python research_example.py custom_openai    # 使用自定义 OpenAI 兼容接口")
        print("  python research_example.py config_file      # 使用配置文件")
        print("  python research_example.py mcp_search       # 使用 MCP search 工具")
        print("  python research_example.py combined         # 结合使用")
        print("  python research_example.py ollama           # 使用 Ollama")
        print("  python research_example.py deepseek         # 使用 DeepSeek")
