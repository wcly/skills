# article-checker

基于 LLM 的文章智能校验工具

## 简介

article-checker 是一个 Trae IDE 技能，可以智能校验文章中的各种问题，包括错别字、病句、拼写错误、逻辑错误等，并提供修改建议。

## 功能特性

- ✅ 错别字检测
- ✅ 拼写错误检测（英文）
- ✅ 病句检测
- ✅ 逻辑错误检测
- ✅ 语句不通顺检测
- ✅ 重复字词检测
- ✅ 标点错误检测

## 安装

### 方式一：运行安装脚本

```bash
cd /path/to/article-checker
./install.sh
```

### 方式二：手动链接

```bash
mkdir -p ~/.trae-cn/skills
ln -sf /path/to/article-checker ~/.trae-cn/skills/article-checker
```

## 使用方法

### 触发方式

在 Trae IDE 中，直接对 AI 说：

```
请帮我校验以下文章：
[你的文章内容]
```

或者使用命令：

```
/article-checker
[你的文章内容]
```

### 校验结果

技能会调用 LLM 按照规则对文章进行校验，并以 JSON 格式返回结果。

## 文件结构

```
article-checker/
├── SKILL.md              # 技能定义
├── references/
│   └── rules.md          # 检查规则和输出格式
├── assets/
│   └── report-template.md # 报告模板
├── install.sh            # 安装脚本
└── README.md             # 本文件
```

## 配置 LLM

此技能需要调用 LLM 进行校验，你需要：

1. 配置你的 LLM API（OpenAI / Claude / 本地模型等）
2. 确保环境可以访问 LLM 服务

具体配置请参考你的 LLM 提供商的文档。

## 输出示例

```json
{
  "total_issues": 3,
  "summary": {
    "typos": 2,
    "spelling": 0,
    "grammar": 1,
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
      "position": 10,
      "original": "心情也很好",
      "suggestion": "心情也很好",
      "reason": "此处应该是『也很好』"
    }
  ]
}
```

## 自定义规则

如需自定义检查规则，请编辑 `references/rules.md` 文件。

## 许可证

MIT License
