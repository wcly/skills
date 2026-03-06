# 文章校验规则

本文档定义了 LLM 进行文章校验时使用的检查规则和输出格式。

---

## 一、检查项目

### 1.1 错别字检测

- 常见错别字：如 "的" 写成 "得"、"再" 写成 "在"、"那" 写成 "哪" 等
- "的地得" 误用：的地得使用不正确
- 成语错字：常见成语中的错别字
- 同音字误用：音近字混用

### 1.2 拼写错误（英文）

- 英文单词拼写错误
- 大小写错误
- 标点符号误用

### 1.3 病句检测

- 成分残缺：缺少主语、谓语、宾语等
- 语序不当：词序混乱
- 搭配不当：主谓、动宾搭配不当
- 句式杂糅：两种句式混在一起
- 语义重复：重复表达相同意思

### 1.4 逻辑错误

- 前后矛盾：上下文信息相互矛盾
- 因果倒置：原因和结果颠倒
- 条件错误：条件与结论不匹配
- 推理错误：逻辑推理不成立

### 1.5 语句不通顺

- 表达生硬：语言不自然
- 逻辑不清晰：论述跳跃或混乱
- 指代不明：指代对象不明确

### 1.6 重复检测

- 连续重复字词：连续出现相同的字或词
- 语义重复：相近意思重复表达

### 1.7 标点错误

- 顿号逗号混淆
- 句号问号误用
- 引号括号不匹配
- 省略号使用不当

---

## 二、输出格式

LLM 必须按照以下 JSON 格式输出校验结果：

```json
{
  "total_issues": <number>,
  "summary": {
    "typos": <number>,
    "spelling": <number>,
    "grammar": <number>,
    "logic": <number>,
    "style": <number>,
    "repetition": <number>,
    "punctuation": <number>
  },
  "issues": [
    {
      "type": "<type>",
      "severity": "<high|medium|low>",
      "line": <number>,
      "position": <number>,
      "original": "<原文>",
      "suggestion": "<修改建议>",
      "reason": "<错误原因说明>"
    }
  ]
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_issues` | number | 总问题数 |
| `summary` | object | 各类型问题统计 |
| `issues` | array | 问题列表 |
| `type` | string | 问题类型：typos/spelling/grammar/logic/style/repetition/punctuation |
| `severity` | string | 严重程度：high/medium/low |
| `line` | number | 出现行号 |
| `position` | number | 字符位置（从 0 开始） |
| `original` | string | 原文内容 |
| `suggestion` | string | 修改建议 |
| `reason` | string | 错误原因说明 |

---

## 三、输出规范

1. **JSON 格式**：输出必须是合法的 JSON 字符串
2. **无问题时**：`issues` 为空数组，`total_issues` 为 0
3. **行号从 1 开始**：方便用户定位
4. **中文错误类型**：
   - `typos` → 错别字
   - `spelling` → 拼写错误
   - `grammar` → 病句
   - `logic` → 逻辑错误
   - `style` → 语句不通顺
   - `repetition` → 重复
   - `punctuation` → 标点错误
5. **严重程度说明**：
   - `high`：严重影响理解或表达错误
   - `medium`：需要修改但不影响理解
   - `low`：建议优化

---

## 四、Few-shot 示例

### 示例 1：错别字检测

**输入文章：**
```
今天天气非常好，我的心情也很
好。明天我们要去公圆玩，那里
有很多花。
```

**LLM 输出：**
```json
{
  "total_issues": 2,
  "summary": {
    "typos": 2,
    "spelling": 0,
    "grammar": 0,
    "logic": 0,
    "style": 0,
    "repetition": 0,
    "punctuation": 0
  },
  "issues": [
    {
      "type": "typos",
      "severity": "high",
      "line": 1,
      "position": 12,
      "original": "的心情也很",
      "suggestion": "的心情也很好",
      "reason": "根据上下文『非常好』，此处应该是『也很好』，表示递进关系"
    },
    {
      "type": "typos",
      "severity": "high",
      "line": 2,
      "position": 9,
      "original": "公圆",
      "suggestion": "公园",
      "reason": "『公园』是正确写法，『公圆』是常见的错别字"
    }
  ]
}
```

### 示例 2：病句检测

**输入文章：**
```
通过这次学习，使我得到了很
大的进步。通过这次活动，体现
了同学们的团结精神。
```

**LLM 输出：**
```json
{
  "total_issues": 2,
  "summary": {
    "typos": 0,
    "spelling": 0,
    "grammar": 2,
    "logic": 0,
    "style": 0,
    "repetition": 0,
    "punctuation": 0
  },
  "issues": [
    {
      "type": "grammar",
      "severity": "high",
      "line": 1,
      "position": 0,
      "original": "通过这次学习，使我得到了很大的进步",
      "suggestion": "这次学习使我得到了很大的进步",
      "reason": "成分残缺，『通过...使...』造成主语缺失，应删除『通过』或『使』"
    },
    {
      "type": "grammar",
      "severity": "high",
      "line": 2,
      "position": 0,
      "original": "通过这次活动，体现了同学们的团结精神",
      "suggestion": "这次活动体现了同学们的团结精神",
      "reason": "成分残缺，『通过...体现了...』造成主语缺失，应删除『通过』"
    }
  ]
}
```

### 示例 3：逻辑错误

**输入文章：**
```
因为今天下雨了，所以明天一
定会晴天。既然他已经失败了，
说明他不够努力。
```

**LLM 输出：**
```json
{
  "total_issues": 2,
  "summary": {
    "typos": 0,
    "spelling": 0,
    "grammar": 0,
    "logic": 2,
    "style": 0,
    "repetition": 0,
    "punctuation": 0
  },
  "issues": [
    {
      "type": "logic",
      "severity": "medium",
      "line": 1,
      "position": 0,
      "original": "因为今天下雨了，所以明天一定会晴天",
      "suggestion": "因为今天下雨了，所以明天可能是阴天",
      "reason": "因果倒置，下雨与晴天没有必然因果关系，明天可能是阴天"
    },
    {
      "type": "logic",
      "severity": "medium",
      "line": 2,
      "position": 0,
      "original": "既然他已经失败了，说明他不够努力",
      "suggestion": "他已经失败了，可能是因为他不够努力",
      "reason": "逻辑错误，失败不一定意味着不够努力，可能有其他原因"
    }
  ]
}
```

---

## 五、注意事项

1. **逐行分析**：仔细检查每一行，包括标题、段落、列表等
2. **结合上下文**：判断错误时要结合上下文语境
3. **中英混排**：注意英文单词在中文文章中的拼写
4. **专业术语**：对于领域专用术语，谨慎判断是否错误
5. **如果无法判断**：可以标记为 `style` 类型并说明需要人工确认

---

## 六、自动修复功能

当用户选择自动修复时，LLM 需要根据用户选择的修复范围，输出修复后的文章内容。

### 6.1 修复范围选项

- `all`：修复所有问题
- `high`：仅修复严重程度为 high 的问题
- `high+medium`：修复严重程度为 high 和 medium 的问题
- `custom`：用户自定义选择修复哪些问题（需要提供具体的问题索引列表）

### 6.2 修复输出格式

```json
{
  "fixed": true,
  "fixed_count": <number>,
  "fixed_issues": [
    {
      "line": <number>,
      "position": <number>,
      "original": "<原文>",
      "fixed": "<修复后内容>"
    }
  ],
  "skipped_issues": [
    {
      "line": <number>,
      "position": <number>,
      "original": "<原文>",
      "reason": "<跳过原因>"
    }
  ],
  "fixed_article": "<修复后的完整文章>"
}
```

### 6.3 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `fixed` | boolean | 是否成功修复 |
| `fixed_count` | number | 修复的问题数量 |
| `fixed_issues` | array | 已修复的问题列表 |
| `skipped_issues` | array | 跳过的（未修复的）问题列表 |
| `fixed_article` | string | 修复后的完整文章内容 |

### 6.4 修复原则

1. **精确替换**：仅替换需要修复的部分，保留其他内容不变
2. **保持格式**：保留原文的段落格式、换行、缩进等
3. **上下文一致**：修复时考虑上下文语境，确保语义连贯
4. **标记修复**：在输出中明确说明修复了哪些内容
5. **安全替换**：使用字符串替换而非重新生成整个文章，确保内容一致性
