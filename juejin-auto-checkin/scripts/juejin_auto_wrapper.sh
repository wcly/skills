#!/bin/bash
# 随机延迟后执行掘金签到，防止固定时间被服务器限制
# 触发时间固定 8:30，实际执行随机落在 8:30~9:30

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"

DELAY=$((RANDOM % 3601))  # 0~3600 秒（0~60 分钟）
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 随机延迟 ${DELAY} 秒后执行签到..." >> /Users/ut/.juejin_auto.log
sleep "$DELAY"

"$PYTHON_BIN" "$SCRIPT_DIR/juejin_auto.py" --headless
