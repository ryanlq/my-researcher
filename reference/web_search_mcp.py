#!/usr/bin/env python3
"""
MCP Server for SearXNG Search
将 SearXNG 搜索包装成 MCP 服务器，供 gpt-researcher 使用
"""
import asyncio
import json
import sys
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import requests
from bs4 import BeautifulSoup


class SearXNGSearch:
    """SearXNG 搜索类"""

    def __init__(self, engine_url: str = "http://127.0.0.1:8888"):
        self.engine_url = engine_url

    def search(self, query: str, max_results: int = 10, lang: str = "auto") -> str:
        """
        执行搜索并返回格式化结果

        Args:
            query: 搜索查询
            max_results: 最大结果数
            lang: 语言设置

        Returns:
            JSON 格式的搜索结果字符串
        """
        params = {
            "q": query,
            "language": lang,
            "safesearch": 1,
            "format": "json"  # 使用 JSON 格式更容易解析
        }
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(
                f"{self.engine_url}/search",
                params=params,
                headers=headers,
                timeout=15
            )
            response.raise_for_status()

            # 尝试解析 JSON 格式结果
            try:
                data = response.json()
                results = data.get("results", [])

                # 格式化结果为 gpt-researcher 期望的格式
                formatted_results = []
                for result in results[:max_results]:
                    # 提取内容
                    content = result.get("content", "")
                    if not content:
                        # 如果没有内容，尝试获取 snippet
                        content = result.get("snippet", "")

                    formatted_results.append({
                        "title": result.get("title", ""),
                        "href": result.get("url", ""),
                        "body": content
                    })

                return json.dumps(formatted_results, ensure_ascii=False)

            except json.JSONDecodeError:
                # 如果不是 JSON 格式，回退到 HTML 解析
                soup = BeautifulSoup(response.text, "html.parser")
                results = soup.find_all("article", class_="result")

                formatted_results = []
                for result in results[:max_results]:
                    h3 = result.find("h3")
                    if h3:
                        link = h3.find("a")
                        if link:
                            # 获取内容
                            content_div = result.find("div", class_="content")
                            content = content_div.get_text(strip=True) if content_div else ""

                            formatted_results.append({
                                "title": link.text.strip(),
                                "href": link.get("href", ""),
                                "body": content
                            })

                return json.dumps(formatted_results, ensure_ascii=False)

        except Exception as e:
            error_result = [{
                "title": "搜索错误",
                "href": "",
                "body": f"搜索失败: {str(e)}"
            }]
            return json.dumps(error_result, ensure_ascii=False)


# 创建 MCP 服务器实例
server = Server("searxng-search")

# 初始化搜索客户端
# 可以通过环境变量 SEARXNG_URL 自定义 SearXNG 地址
import os
searxng_url = os.getenv("SEARXNG_URL", "http://127.0.0.1:8888")
search_client = SearXNGSearch(searxng_url)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="search",
            description=(
                "使用 SearXNG 搜索引擎搜索网络信息。"
                "支持多种搜索引擎聚合，提供隐私保护的搜索结果。"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询字符串"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "返回的最大结果数（默认10）",
                        "default": 10
                    },
                    "lang": {
                        "type": "string",
                        "description": "语言设置（默认auto自动检测）",
                        "default": "auto"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """执行工具调用"""
    if name == "search":
        query = arguments.get("query", "")
        max_results = arguments.get("max_results", 10)
        lang = arguments.get("lang", "auto")

        # 执行搜索
        result = search_client.search(query, max_results, lang)

        return [TextContent(type="text", text=result)]
    else:
        return [TextContent(type="text", text=f"未知工具: {name}")]


async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
