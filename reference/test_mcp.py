"""
测试 MCP 服务器是否正常工作
"""
import asyncio
import subprocess
import json

async def test_mcp_server():
    """测试 MCP 服务器"""
    print("启动 MCP 服务器...")

    # 启动 MCP 服务器进程
    proc = subprocess.Popen(
        ["python", "web_search_mcp.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        # 等待服务器启动
        await asyncio.sleep(2)

        # 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }

        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # 读取响应
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print(f"初始化响应: {json.dumps(response, indent=2, ensure_ascii=False)}")

        # 发送 tools/list 请求
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        proc.stdin.write(json.dumps(tools_request) + "\n")
        proc.stdin.flush()

        # 读取响应
        response_line = proc.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            print(f"\n可用工具: {json.dumps(response, indent=2, ensure_ascii=False)}")

    finally:
        proc.terminate()
        await asyncio.sleep(1)
        if proc.poll() is None:
            proc.kill()

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
