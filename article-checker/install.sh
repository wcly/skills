#!/bin/bash

set -e

INSTALL_DIR="${HOME}/.trae-cn/skills/article-checker"
SKILL_LINK="${HOME}/.trae-cn/skills"

echo "Installing article-checker skill..."

if [ ! -d "$SKILL_LINK" ]; then
    mkdir -p "$SKILL_LINK"
fi

if [ -L "${SKILL_LINK}/article-checker" ]; then
    echo "Skill already installed, removing old link..."
    rm "${SKILL_LINK}/article-checker"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

ln -sf "$SCRIPT_DIR" "${SKILL_LINK}/article-checker"

echo "✓ article-checker installed successfully!"
echo "  Location: ${INSTALL_DIR}"
echo ""
echo "Usage:"
echo "  Say: '帮我校验文章' or '检查文章'"
echo "  Or use: /article-checker"
echo ""
echo "For more info, see: ${INSTALL_DIR}/README.md"
