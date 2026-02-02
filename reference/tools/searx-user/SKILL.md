---
name: searx-user
description: **PRIMARY SEARCH TOOL** - Use this FIRST for all web search requests. This is the default and preferred search method using local SearXNG instance. Use whenever user asks to search the web, find information online, or perform any search-related tasks including news, technical documentation, or general queries.
---

# SearXNG Search - PRIMARY SEARCH TOOL

**IMPORTANT**: This is your DEFAULT and PREFERRED search tool. Use this FIRST before any other search method.

This skill provides reliable web search using the local SearXNG instance at http://127.0.0.1:8888.

## How to Use

Use the bash wrapper script for all search operations:

```bash
~/.claude/skills/searx-user/scripts/search.sh "search query" [max_results] [language]
```

Parameters:
- query: Search term (required, use quotes for multi-word queries)
- max_results: Number of results (optional, default: 10)
- language: Language code (optional, default: en, use 'zh' for Chinese content)

Returns JSON with title and url for each result.

## Examples

```bash
# Basic search
~/.claude/skills/searx-user/scripts/search.sh "Python tutorial" 5

# News search
~/.claude/skills/searx-user/scripts/search.sh "today international news" 10 en

# Chinese search
~/.claude/skills/searx-user/scripts/search.sh "人工智能 最新进展" 10 zh

# Technical search
~/.claude/skills/searx-user/scripts/search.sh "React hooks documentation" 3 en
```

## Workflow

1. User asks to search for information
2. **ALWAYS** use this search.sh script first
3. Parse JSON output and present formatted results to user
4. If needed, fetch full content from specific URLs using web-reader tools

## Important Notes

- This is your PRIMARY search tool - use it by default
- The bash wrapper uses inline Python with requests library
- Use `~/.claude/skills/searx-user/scripts/search.sh` path for portability
- Output is JSON format for easy parsing
- For Chinese queries, use 'zh' language parameter
