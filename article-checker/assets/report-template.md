# 文章校验报告

> 生成时间: {{timestamp}}
> 文章字数: {{word_count}} 字

---

## 校验摘要

| 问题类型 | 数量 |
|---------|------|
| 错别字 | {{typos_count}} |
| 拼写错误 | {{spelling_count}} |
| 病句 | {{grammar_count}} |
| 逻辑错误 | {{logic_count}} |
| 语句不通顺 | {{style_count}} |
| 重复 | {{repetition_count}} |
| 标点错误 | {{punctuation_count}} |
| **总计** | **{{total_issues}}** |

---

## 问题详情

{{#each issues}}

### {{line}}:{{position}} - {{type}}

- **严重程度**: {{severity}}
- **原文**: `{{original}}`
- **建议修改**: `{{suggestion}}`
- **原因**: {{reason}}

{{/each}}

---

## 修改建议汇总

{{#each issues}}
- 行 {{line}}: `{{original}}` → `{{suggestion}}`
{{/each}}

---

## 说明

本报告由 article-checker 生成，基于 LLM 智能校验。
建议仅供参考，最终修改请结合实际情况决定。

---

## 自动修复

是否需要自动修复检测到的问题？

### 修复选项

- [ ] 修复所有问题 ({{total_issues}} 个)
- [ ] 仅修复严重问题 ({{high_count}} 个)
- [ ] 修复严重和一般问题 ({{high_medium_count}} 个)
- [ ] 自定义选择

### 自定义选择

请输入要修复的问题编号（用逗号分隔，如：1,3,5）：

---

## 修复报告

> 生成时间: {{fix_timestamp}}

### 修复摘要

| 项目 | 数量 |
|------|------|
| 已修复 | {{fixed_count}} |
| 已跳过 | {{skipped_count}} |

### 修复详情

{{#each fixed_issues}}
- 行 {{line}}: `{{original}}` → `{{fixed}}`
{{/each}}

### 跳过的问题

{{#each skipped_issues}}
- 行 {{line}}: `{{original}}` (原因: {{reason}})
{{/each}}

---

## 修复后的文章

```
{{fixed_article}}
```
