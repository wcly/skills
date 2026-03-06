# article-checker 设计文档

## 一、项目概述

**项目名称**：article-checker（文章校验工具）

**项目类型**：Trae IDE Skill（基于 LLM 的文章智能校验技能）

**核心功能**：用户输入文章后，LLM 按照规则文档进行校验，输出检查报告和修改建议

**目标用户**：需要文章校对的人员（写作者、编辑、学生等）

---

## 二、需求收集结果

| 需求项 | 选择 |
|--------|------|
| 使用场景 | 命令行工具（用户输入文本调用 LLM 校验） |
| 支持语言 | 中文（简体）+ 多语言（中英混排） |
| 输出格式 | 终端彩色输出 + Markdown 文件 |
| 检查项目 | 错别字、拼写错误、病句、逻辑错误、重复检测、标点错误（全部） |
| 技术方案 | LLM 智能校验（用户提供 API Key） |
| LLM 选择 | 让用户配置（不硬编码） |

---

## 三、推荐方案

**混合型方案**：核心规则 + 丰富示例（Few-shot）

- 规则文档包含核心检查规则和输出 JSON 格式说明
- 用示例引导 LLM 理解期望的输出格式
- 平衡灵活性和一致性

---

## 四、目录结构

```
article-checker/
├── SKILL.md              # Skill definition（技能入口）
├── references/           # 详细文档
│   └── rules.md          # 检查规则和输出格式定义
├── assets/               # 模板、配置文件
├── scripts/              # 辅助脚本（可选）
├── install.sh            # 跨平台安装脚本
└── README.md             # 使用说明
```

---

## 五、文件设计

### 5.1 SKILL.md

**定位**：声明式技能，定义如何调用 LLM 进行文章校验

**核心内容**：
1. 技能名称和描述
2. 触发关键词（"文章校验"、"检查文章"、"校对"等）
3. 规则文档路径（`references/rules.md`）
4. LLM 调用模板（System Prompt）
5. 输出处理说明

### 5.2 references/rules.md

**1. 检查项目**（全覆盖）
- 错别字检测：常见错别字、"的地得"误用
- 拼写错误：英文单词拼写
- 病句检测：语法不通顺、成分残缺、语序不当
- 逻辑错误：前后矛盾、因果倒置
- 语句不通顺：表达生硬、逻辑不清晰
- 重复检测：连续重复字词
- 标点错误：标点符号误用

**2. 输出格式**
- JSON 格式输出
- 包含字段：
  - `type`: 问题类型
  - `severity`: 严重程度（high/medium/low）
  - `line`: 行号
  - `position`: 位置（字符偏移）
  - `original`: 原文
  - `suggestion`: 修改建议
  - `reason`: 错误原因说明

**3. Few-shot 示例**
- 2-3 个示例展示期望的输入输出格式

### 5.3 assets/

- `report-template.md`: Markdown 报告模板

### 5.4 install.sh

- 跨平台安装脚本
- 支持 `--all` 安装所有依赖

---

## 六、LLM 调用流程

```
用户输入 → SKILL.md → 加载 references/rules.md → 构建 System Prompt → 调用 LLM → 解析输出 → 呈现报告
```

---

## 七、System Prompt 模板

```markdown
你是一个专业的文章校对专家。请仔细阅读以下文章，按照规则进行校验。

## 检查规则
[从 references/rules.md 读取]

## 输出格式
[从 references/rules.md 读取]

## 示例
[从 references/rules.md 读取]

## 待校验文章
[用户输入]
```

---

## 八、输出报告示例

```json
{
  "total_issues": 5,
  "summary": {
    "typos": 2,
    "spelling": 1,
    "grammar": 1,
    "logic": 1
  },
  "issues": [
    {
      "type": "错别字",
      "severity": "high",
      "line": 3,
      "position": 15,
      "original": "他的心情非常好",
      "suggestion": "「非常好」正确，此处无错（示例格式）",
      "reason": "示例仅展示输出格式"
    }
  ]
}
```

---

## 九、非功能需求

- **可扩展性**：规则文档可独立更新，无需修改代码
- **灵活性**：支持用户配置自己的 LLM API
- **可维护性**：规则和代码分离，便于迭代

---

## 十、后续步骤

1. 编写 SKILL.md
2. 编写 references/rules.md（含完整规则和示例）
3. 编写 assets/report-template.md
4. 编写 install.sh
5. 编写 README.md
