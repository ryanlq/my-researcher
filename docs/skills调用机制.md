# GPT-Researcher Skills 调用机制

## 调用逻辑总结

### 1️⃣ 初始化阶段（总是创建）

```python
# 所有 GPTResearcher 实例都会创建这些基础 Skills
self.research_conductor = ResearchConductor(self)      # ✅ 总是创建
self.report_generator = ReportGenerator(self)         # ✅ 总是创建
self.context_manager = ContextManager(self)           # ✅ 总是创建
self.scraper_manager = BrowserManager(self)           # ✅ 总是创建
self.source_curator = SourceCurator(self)             # ✅ 总是创建

# DeepResearchSkill 只在特定条件下创建
self.deep_researcher = None
if report_type == ReportType.DeepResearch.value:      # ⚠️ 条件创建
    self.deep_researcher = DeepResearchSkill(self)
```

---

### 2️⃣ 执行阶段（根据模式选择）

#### 标准研究模式 (`research_report`, `resource_report`, 等)

```python
async def conduct_research():
    # 检查是否为深度研究模式
    if self.report_type == ReportType.DeepResearch.value:
        # 使用 DeepResearchSkill
        return await self.deep_researcher.run()

    # 标准模式：使用 ResearchConductor
    self.context = await self.research_conductor.conduct_research()
    return self.context
```

**调用链**:
```
用户调用 conduct_research()
    │
    ├─→ 检查 report_type
    │   │
    │   ├─→ "deep" ──────────────→ deep_researcher.run()
    │   │
    │   └─→ 其他 ────────────────→ research_conductor.conduct_research()
    │                                │
    │                                ├─→ plan_research()          # 规划
    │                                │   └─→ 生成子主题
    │                                │
    │                                ├─→ browser_manager         # 抓取网页
    │                                │
    │                                ├─→ source_curator          # 策选来源
    │                                │
    │                                └─→ context_manager         # 管理上下文
```

---

### 3️⃣ 报告生成阶段（总是使用）

```python
async def write_report():
    # 不管什么模式，总是使用 ReportGenerator
    report = await self.report_generator.write_report(
        ext_context=self.context,  # 使用收集到的上下文
        custom_prompt=custom_prompt
    )
    return report
```

---

## 完整调用流程

### 标准研究流程

```python
# 用户代码
researcher = GPTResearcher(
    query="研究问题",
    report_type="research_report"  # 标准模式
)

# 步骤 1: 初始化
✅ research_conductor  创建
✅ report_generator     创建
✅ context_manager      创建
✅ scraper_manager      创建
✅ source_curator       创建
❌ deep_researcher      不创建

# 步骤 2: 执行研究
await researcher.conduct_research()
    └─→ research_conductor.conduct_research()
        ├─→ plan_research()           # 使用 STRATEGIC_LLM
        ├─→ get_search_results()      # 使用 FAST_LLM + 检索器
        ├─→ browser_manager           # 抓取网页
        ├─→ source_curator            # 筛选来源
        └─→ context_manager           # 存储上下文

# 步骤 3: 生成报告
await researcher.write_report()
    └─→ report_generator.write_report()
        └─→ 使用 SMART_LLM 生成报告
```

### 深度研究流程

```python
# 用户代码
researcher = GPTResearcher(
    query="研究问题",
    report_type="deep"  # 深度模式
)

# 步骤 1: 初始化
✅ research_conductor  创建（但不会使用）
✅ report_generator     创建
✅ context_manager      创建
✅ scraper_manager      创建
✅ source_curator       创建
✅ deep_researcher      创建（条件满足）

# 步骤 2: 执行研究
await researcher.conduct_research()
    └─→ deep_researcher.run()
        ├─→ 生成搜索查询 (breadth=5)
        ├─→ 第 1 层：广度搜索
        │   ├─→ 使用 STRATEGIC_LLM
        │   └─→ 并发执行 (concurrency=4)
        │
        ├─→ 提取子主题 (max_subtopics=7)
        │
        ├─→ 第 2-3 层：深度研究 (depth=3)
        │   ├─→ 使用 SMART_LLM
        │   ├─→ browser_manager
        │   └─→ source_curator
        │
        └─→ context_manager

# 步骤 3: 生成报告
await researcher.write_report()
    └─→ report_generator.write_report()
        └─→ 使用 SMART_LLM 生成报告
```

---

## LLM 使用分配

| 任务 | 使用的 LLM | 模式 |
|------|-----------|------|
| **选择研究代理** | STRATEGIC_LLM | 标准模式 |
| **规划研究大纲** | STRATEGIC_LLM | 标准模式 |
| **生成搜索查询** | FAST_LLM | 深度模式 |
| **提取子主题** | SMART_LLM | 深度模式 |
| **生成报告** | SMART_LLM | 所有模式 |
| **生成结论** | SMART_LLM | 所有模式 |

---

## 关键代码片段

### 初始化判断（agent.py:168-170）

```python
self.deep_researcher: Optional[DeepResearchSkill] = None
if report_type == ReportType.DeepResearch.value:
    self.deep_researcher = DeepResearchSkill(self)
```

### 执行判断（agent.py:298-300）

```python
# Handle deep research separately
if self.report_type == ReportType.DeepResearch.value and self.deep_researcher:
    return await self._handle_deep_research(on_progress)
```

### 标准研究执行（agent.py:325）

```python
# 标准模式：使用 ResearchConductor
self.context = await self.research_conductor.conduct_research()
```

### 深度研究执行（agent.py:351）

```python
# 深度模式：使用 DeepResearchSkill
self.context = await self.deep_researcher.run(on_progress=on_progress)
```

---

## 总结

### 自动调用机制

✅ **基础 Skills** - 自动创建和使用
- ResearchConductor, ReportGenerator, ContextManager, BrowserManager, SourceCurator
- 不管什么模式都会使用

⚠️ **条件 Skills** - 根据模式决定
- DeepResearchSkill 只在 `report_type="deep"` 时创建和使用

### 模式判断

```python
if report_type == "deep":
    使用 DeepResearchSkill (多层递进)
else:
    使用 ResearchConductor (标准流程)
```

### 报告生成

```python
# 所有模式都使用 ReportGenerator
report_generator.write_report()
```

---

## 实用建议

### 选择合适的模式

**标准研究** (`research_report`)
- ✅ 适合大多数场景
- ✅ 速度快（单次搜索）
- ✅ 成本低
- 📊 3-5 个子主题

**深度研究** (`deep`)
- ✅ 需要全面分析
- ✅ 学术研究
- ⚠️ 速度慢（多层递进）
- ⚠️ 成本高
- 📊 7+ 个子主题，3 层深度
