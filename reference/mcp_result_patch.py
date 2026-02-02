"""
MCP 结果处理补丁

修复 gpt-researcher 对 MCP 工具返回值的解析问题
"""

def patch_mcp_research():
    """Patch MCPResearchSkill to properly handle MCP tool results"""

    # Import the module
    from gpt_researcher.mcp import research

    # Save the original method
    original_process_tool_result = research.MCPResearchSkill._process_tool_result

    # Define the patched method
    def patched_process_tool_result(self, tool_name: str, result) -> list:
        """Process tool result into search result format (patched version)"""
        import json
        import logging

        search_results = []

        try:
            # Helper: Try to parse JSON from text content
            def try_parse_json(text):
                try:
                    return json.loads(text)
                except:
                    return None

            # Handle MCP TextContent format: {'type': 'text', 'text': '...', 'id': '...'}
            if isinstance(result, dict) and result.get('type') == 'text':
                text_content = result.get('text', '')
                # Try to parse as JSON array of search results
                parsed = try_parse_json(text_content)
                if parsed and isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict):
                            search_results.append({
                                "title": item.get("title", f"Result from {tool_name}"),
                                "href": item.get("href", item.get("url", f"mcp://{tool_name}")),
                                "body": item.get("body", item.get("content", str(item)))
                            })
                    if search_results:
                        logging.getLogger(__name__).info(f"Patched method: Parsed {len(search_results)} results from MCP TextContent JSON")
                        return search_results
                # If not JSON, treat as single text result
                search_results.append({
                    "title": f"Result from {tool_name}",
                    "href": f"mcp://{tool_name}",
                    "body": text_content
                })
                return search_results

            # Handle list of TextContent objects
            if isinstance(result, list):
                for item in result:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        text_content = item.get('text', '')
                        parsed = try_parse_json(text_content)
                        if parsed and isinstance(parsed, list):
                            for sub_item in parsed:
                                if isinstance(sub_item, dict):
                                    search_results.append({
                                        "title": sub_item.get("title", f"Result from {tool_name}"),
                                        "href": sub_item.get("href", sub_item.get("url", f"mcp://{tool_name}")),
                                        "body": sub_item.get("body", sub_item.get("content", str(sub_item)))
                                    })
                        else:
                            search_results.append({
                                "title": f"Result from {tool_name}",
                                "href": f"mcp://{tool_name}",
                                "body": text_content
                            })
                if search_results:
                    logging.getLogger(__name__).info(f"Patched method: Parsed {len(search_results)} results from MCP list")
                    return search_results

            # Use original processing for other cases
            return original_process_tool_result(self, tool_name, result)

        except Exception as e:
            logging.getLogger(__name__).error(f"Error in patched _process_tool_result: {e}", exc_info=True)
            # Fallback to original method
            return original_process_tool_result(self, tool_name, result)

    # Apply the patch
    research.MCPResearchSkill._process_tool_result = patched_process_tool_result

    print("✅ MCP result processing patch applied successfully")

    return True

# Auto-apply on import
_patch_applied = False

def _apply_patch_once():
    global _patch_applied
    if not _patch_applied:
        try:
            patch_mcp_research()
            _patch_applied = True
        except Exception as e:
            print(f"⚠️  Failed to apply MCP patch: {e}")

_apply_patch_once()
