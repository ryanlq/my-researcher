"""
GPT Researcher 深度研究主程序
使用深度研究模式进行更深入、更全面的研究
"""

import asyncio
import os

from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 先导入补丁（必须在 GPTResearcher 之前）
import mcp_result_patch

# 再导入 GPTResearcher
from gpt_researcher import GPTResearcher


async def deep_research(
    query: str,
    custom_prompt: str = None,
    max_subtopics: int = 7,
    tone: str = "Analytical"
):
    """
    执行深度研究任务

    Args:
        query: 研究查询/问题
        custom_prompt: 自定义报告生成提示（可选）
        max_subtopics: 最大子主题数量（默认7）
        tone: 报告语气（Analytical-分析性, Critical-批判性, 等）
    """
    # MCP 搜索配置 - 使用 SearXNG
    mcp_configs = [
        {
            "name": "searxng-search",
            "command": "python",
            "args": ["web_search_mcp.py"],
            "env": {
                "SEARXNG_URL": "http://127.0.0.1:8888"
            }
        }
    ]

    # 创建研究器 - 使用深度研究模式
    researcher = GPTResearcher(
        query=query,
        report_type="deep",  # 关键：使用深度研究模式
        report_format="markdown",
        tone=tone,
        source_urls=None,
        mcp_configs=mcp_configs,
        mcp_strategy="deep",  # 对每个子查询都使用 MCP
        max_subtopics=max_subtopics,  # 增加子主题数量
        verbose=True
    )

    print(f"🔬 启动深度研究: {query}")
    print(f"📊 研究配置:")
    print(f"  - 模式: 深度研究 (deep)")
    print(f"  - 最大子主题: {max_subtopics}")
    print(f"  - 语气: {tone}")
    print(f"  - MCP 策略: deep (对每个子查询都使用 MCP)")
    print()

    # 步骤 1: 进行深度研究（多层搜索和收集信息）
    print("🔍 开始深度研究...")
    await researcher.conduct_research()

    # 获取研究统计信息
    research_context = researcher.get_research_context()
    research_costs = researcher.get_costs()
    research_images = researcher.get_research_images()
    research_sources = researcher.get_research_sources()

    print(f"\n📊 深度研究统计:")
    print(f"  - 来源数量: {len(research_sources)}")
    print(f"  - 图片数量: {len(research_images)}")
    print(f"  - 研究成本: ${research_costs:.6f}")
    print(f"  - 上下文长度: {len(research_context)} 字符")

    # 步骤 2: 生成深度研究报告
    print(f"\n📝 生成深度研究报告...")

    if custom_prompt:
        report = await researcher.write_report(custom_prompt=custom_prompt)
    else:
        # 默认使用深度研究的标准提示
        report = await researcher.write_report()

    # 保存报告
    safe_filename = query.lower().replace(" ", "_").replace("/", "_")[:50]
    output_file = f"deep_research_{safe_filename}.md"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n✅ 深度研究完成！")
    print(f"📄 报告已保存到: {output_file}")
    print(f"💰 总成本: ${research_costs:.6f}")

    return report, {
        "costs": research_costs,
        "sources_count": len(research_sources),
        "images_count": len(research_images)
    }


async def main():
    """主函数"""

    # 深度研究查询
    query = "2025年网络小说中的爽点机制"

    # 可选的自定义提示 - 用于特定格式的报告
    custom_prompt = None
    # custom_prompt = """
    # 请基于深度研究的结果，撰写一份全面的分析报告，包含以下部分：
    # 1. 执行摘要 - 核心发现和结论
    # 2. 背景分析 - 网络小说爽点的起源和发展
    # 3. 机制剖析 - 不同类型爽点的运作原理
    # 4. 案例研究 - 具体作品中的爽点应用
    # 5. 趋势分析 - 2025年的新发展
    # 6. 结论与展望
    #
    # 使用学术性、分析性的语言风格，每个部分都要引用具体的研究来源。
    # """

    # 执行深度研究
    await deep_research(
        query=query,
        custom_prompt=custom_prompt,
        max_subtopics=7,  # 子主题数量
        tone="Analytical"  # 分析性语气
    )


if __name__ == "__main__":
    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  警告: 未设置 OPENAI_API_KEY 环境变量")
        print("请在 .env 文件中配置你的 API 密钥")
        exit(1)

    # 检查 SearXNG 服务
    import requests
    try:
        response = requests.get("http://127.0.0.1:8888/search", params={"q": "test"}, timeout=2)
        if response.status_code != 200:
            print("⚠️  警告: SearXNG 服务响应异常")
    except:
        print("⚠️  警告: 无法连接到 SearXNG 服务 (http://127.0.0.1:8888)")
        print("深度研究将受到影响...")

    # 运行深度研究
    asyncio.run(main())
