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
