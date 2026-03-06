# article-checker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 创建一个基于 LLM 的文章校验 Skill，包含规则文档和使用说明

**Architecture:** 这是一个声明式 Skill，主要包含 SKILL.md 定义文件和 references/rules.md 规则文档，无需复杂代码

**Tech Stack:** Markdown, Shell

---

## Task 1: 创建 article-checker 目录结构

**Files:**
- Create: `/Users/ut/Documents/learn/skills/article-checker/SKILL.md`
- Create: `/Users/ut/Documents/learn/skills/article-checker/references/rules.md`
- Create: `/Users/ut/Documents/learn/skills/article-checker/assets/report-template.md`
- Create: `/Users/ut/Documents/learn/skills/article-checker/install.sh`
- Create: `/Users/ut/Documents/learn/skills/article-checker/README.md`

---

### Task 1.1: 创建 SKILL.md

**Step 1: 写入 SKILL.md 文件**

```markdown
# article-checker

文章智能校验工具 - 基于 LLM 的文章校对助手

## Description

一个专业的文章校验技能，可以检测文章中的错别字、病句、拼写错误、逻辑错误、矛盾冲突、语句不通顺等问题，并提供修改建议。

## Triggers

- "文章校验"
- "检查文章"
- "校对文章"
- "文章查错"
- "proofread"
- "article check"

## How It Works

1. 用户输入待校验的文章内容
2. 技能加载 `references/rules.md` 中的检查规则
3. 构建 System Prompt 调用 LLM 进行校验
4. LLM 返回检查结果（JSON 格式）
5. 技能解析结果并呈现给用户

## Requirements

- 支持 LLM 调用的环境（OpenAI / Claude / 本地模型等）
- 用户需要自行配置 LLM API

## References

- 详细规则说明: `references/rules.md`
- 报告模板: `assets/report-template.md`
- 安装说明: `README.md`

## Usage

```
请帮我校验以下文章：
[在此输入你的文章]
```

或者使用命令：
```
/article-checker
[在此输入你的文章]
```
```

**Step 2: 确认文件创建成功**

Run: `ls -la /Users/ut/Documents/learn/skills/article-checker/`
Expected: 目录存在

---

### Task 1.2: 创建 references/rules.md

**Step 1: 写入 rules.md 文件**

创建完整的规则文档，包含：
1. 检查规则（7大类）
2. 输出 JSON 格式定义
3. Few-shot 示例（2-3个）

**Step 2: 确认文件创建成功**

Run: `ls -la /Users/ut/Documents/learn/skills/article-checker/references/`
Expected: rules.md 存在

---

### Task 1.3: 创建 assets/report-template.md

**Step 1: 写入报告模板**

创建 Markdown 格式的检查报告模板。

**Step 2: 确认文件创建成功**

Run: `ls -la /Users/ut/Documents/learn/skills/article-checker/assets/`
Expected: report-template.md 存在

---

### Task 1.4: 创建 install.sh

**Step 1: 写入安装脚本**

创建跨平台的安装脚本。

**Step 2: 确认文件创建成功**

Run: `ls -la /Users/ut/Documents/learn/skills/article-checker/`
Expected: install.sh 存在

---

### Task 1.5: 创建 README.md

**Step 1: 写入 README 文件**

创建使用说明文档。

**Step 2: 确认文件创建成功**

Run: `ls -la /Users/ut/Documents/learn/skills/article-checker/`
Expected: README.md 存在

---

## Task 2: 验证所有文件

**Step 1: 验证目录结构**

Run: `tree /Users/ut/Documents/learn/skills/article-checker/`
Expected: 显示完整目录结构

---

## Task 3: 提交到 Git（可选）

**Step 1: 提交更改**

如果需要提交到 Git：
```bash
cd /Users/ut/Documents/learn/skills/article-checker
git init
git add .
git commit -m "feat: add article-checker skill"
```
