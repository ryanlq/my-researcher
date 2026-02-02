# GPT-Researcher 多代理架构解析

## 架构概述

GPT-Researcher **不是传统意义上的多代理系统**（如 AutoGen、CrewAI），而是采用**模块化 Skill（技能）架构**，每个 Skill 作为一个专门的"代理"负责特定任务，由主协调器统一管理。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      GPTResearcher                          │
│                      (主协调器)                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ 统一调度
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Researcher   │  │    Writer    │  │  DeepResearch│
│  Skill       │  │    Skill     │  │  Skill       │
│              │  │              │  │              │
│ - 规划研究    │  │ - 生成报告    │  │ - 深度分析    │
│ - 执行搜索    │  │ - 格式化      │  │ - 多层递进    │
│ - 数据收集    │  │ - 结论总结    │  │ - 广度扩展    │
└──────────────┘  └──────────────┘  └──────────────┘
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────────┐
        │         辅助 Skills (Support)            │
        ├──────────────────────────────────────────┤
        │  ContextManager  - 上下文管理            │
        │  BrowserManager   - 浏览器控制            │
        │  SourceCurator    - 来源策展              │
        └──────────────────────────────────────────┘
```

## 核心 Skills 组件

### 1. ResearchConductor (研究指挥官)
**文件**: `skills/researcher.py`

**职责**:
- 📋 规划研究策略
- 🔍 执行搜索查询
- 📊 收集研究数据
- 🎯 协调研究流程

**关键方法**:
```python
async def plan_research(query)      # 规划研究大纲
async def conduct_research()         # 执行研究任务
async def _get_context_by_web_search() # 网络搜索上下文
```

---

### 2. ReportGenerator (报告生成器)
**文件**: `skills/writer.py`

**职责**:
- ✍️ 撰写研究报告
- 📐 格式化内容
- 🎨 应用语气和风格
- 📝 生成结论

**关键方法**:
```python
async def write_report()              # 生成主报告
async def write_introduction()        # 写引言
async def write_conclusion()          # 写结论
```

---

### 3. DeepResearchSkill (深度研究)
**文件**: `skills/deep_research.py`

**职责**:
- 🔄 多层递进研究
- 🌐 广度扩展查询
- 🧠 综合分析
- ⚡ 并发执行

**参数**:
- `breadth`: 每层查询数量 (默认 4)
- `depth`: 研究深度层数 (默认 2)
- `concurrency`: 并发数 (默认 2)

**工作流程**:
```
主查询
  ├─→ 生成 5 个初始查询
  │    ├─→ 搜索 + 收集数据
  │    └─→ 提取 7 个子主题
  │
  ├─→ 对每个子主题深度研究 (3 层)
  │    ├─→ 第 1 层: 基础信息
  │    ├─→ 第 2 层: 深入分析
  │    └─→ 第 3 层: 综合推理
  │
  └─→ 综合所有数据生成报告
```

---

### 4. ContextManager (上下文管理器)
**文件**: `skills/context_manager.py`

**职责**:
- 💾 存储研究上下文
- 🔗 关联相关内容
- 📚 管理知识库
- 🔄 更新上下文

---

### 5. BrowserManager (浏览器管理器)
**文件**: `skills/browser.py`

**职责**:
- 🌐 控制浏览器
- 📄 抓取网页内容
- 🖼️ 提取图片
- 🔐 处理反爬

---

### 6. SourceCurator (来源策展人)
**文件**: `skills/curator.py`

**职责**:
- ✅ 筛选高质量来源
- 🎯 内容去重
- 📊 相关性排序
- 🔍 信任度评估

---

## 工作流程

### 标准研究流程 (research_report)

```
用户查询
   │
   ├─→ ResearchConductor.plan_research()
   │    ├─→ 初始搜索了解主题
   │    └─→ 生成研究大纲和子主题
   │
   ├─→ ResearchConductor.conduct_research()
   │    ├─→ 对每个子主题执行搜索
   │    ├─→ BrowserManager 抓取网页内容
   │    ├─→ SourceCurator 筛选和排序来源
   │    └─→ ContextManager 存储上下文
   │
   └─→ ReportGenerator.write_report()
        ├─→ 分析研究数据
        ├─→ 撰写各部分内容
        └─→ 生成最终报告
```

### 深度研究流程 (deep)

```
用户查询
   │
   ├─→ DeepResearchSkill
   │    ├─→ 第 1 层 (广度)
   │    │    ├─→ 生成 5 个查询
   │    │    └─→ 并发搜索
   │    │
   │    ├─→ 第 2 层 (深度)
   │    │    ├─→ 提取 7 个子主题
   │    │    └─→ 对每个子主题深入研究
   │    │
   │    └─→ 第 3 层 (综合)
   │         ├─→ 交叉验证信息
   │         └─→ 综合分析推理
   │
   └─→ ReportGenerator.write_report()
        └─→ 生成深度研究报告
```

---

## 与传统多代理系统的区别

| 特性 | GPT-Researcher | AutoGen / CrewAI |
|------|----------------|------------------|
| **架构** | 模块化 Skills | 独立 Agents |
| **通信** | 直接方法调用 | 消息传递 |
| **协调** | 主协调器 | 代理间协商 |
| **状态** | 共享状态 | 分布式状态 |
| **复杂度** | 低 | 高 |
| **可控性** | 高 | 中 |

---

## 优势

✅ **简单高效** - 不需要复杂的代理通信
✅ **易于调试** - 每个技能职责明确
✅ **性能优化** - 可针对每个技能独立优化
✅ **灵活扩展** - 可以轻松添加新技能

---

## 配置示例

### 使用深度研究模式

```python
researcher = GPTResearcher(
    query="你的研究问题",
    report_type="deep",  # 启用深度研究
    max_subtopics=7,
)

# 配置深度研究参数
# .env 文件:
DEEP_RESEARCH_BREADTH=5   # 广度
DEEP_RESEARCH_DEPTH=3     # 深度
DEEP_RESEARCH_CONCURRENCY=4  # 并发
```

### 混合使用不同技能

```python
# 标准研究: 只使用 ResearchConductor + ReportGenerator
report_type = "research_report"

# 深度研究: 使用 DeepResearchSkill + ReportGenerator
report_type = "deep"

# 资源报告: 只收集资源，不深度分析
report_type = "resource_report"
```

---

## 总结

GPT-Researcher 的"多代理"实际上是一种**技能编排架构**：
- 每个 Skill 就像一个专门领域的"专家代理"
- 由主协调器统一调度和协作
- 通过直接方法调用而非消息传递
- 适合研究型任务，强调可控性和效率

如果你需要真正的多代理系统（代理间自主协商），可以考虑：
- **AutoGen** - 微软的多代理框架
- **CrewAI** - 代理协作框架
- **LangGraph** - 状态图多代理
