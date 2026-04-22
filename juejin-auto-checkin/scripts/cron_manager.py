#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
DEFAULT_SCRIPT_PATH = str(SCRIPTS_DIR / "juejin_auto.py")
DEFAULT_WRAPPER_PATH = str(SCRIPTS_DIR / "juejin_auto_wrapper.sh")
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / "com.juejin.autosignin.plist"

AVAILABLE_SCRIPTS = {
    "1": {
        "name": "稀土掘金自动签到",
        "path": DEFAULT_SCRIPT_PATH,
        "wrapper_path": DEFAULT_WRAPPER_PATH,
        "desc": "自动签到 + 免费抽奖"
    }
}

def list_scripts():
    print("\n�� 可用的定时脚本:")
    print("=" * 50)
    for key, script in AVAILABLE_SCRIPTS.items():
        print(f"  {key}. {script['name']}")
        print(f"     {script['desc']}")
    print("=" * 50)

def check_cron():
    if not PLIST_PATH.exists():
        return None
    with open(PLIST_PATH, "r") as f:
        content = f.read()
    if "Hour" not in content:
        return None
    import re
    hour_match = re.search(r'<key>Hour</key>\s*<integer>(\d+)</integer>', content)
    minute_match = re.search(r'<key>Minute</key>\s*<integer>(\d+)</integer>', content)
    if hour_match and minute_match:
        script_match = re.search(r'<string>(/.*?\.(?:py|sh))</string>', content)
        configured_path = script_match.group(1) if script_match else "未知"
        script_name = configured_path
        for key, s in AVAILABLE_SCRIPTS.items():
            if configured_path in [s['path'], s.get('wrapper_path')]:
                script_name = s['name']
                break
        return f"{int(hour_match.group(1)):02d}:{int(minute_match.group(1)):02d}", script_name
    return None

def set_cron(hour, minute, script_path):
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    selected_script = None
    for script in AVAILABLE_SCRIPTS.values():
        if script_path in [script["path"], script.get("wrapper_path")]:
            selected_script = script
            break

    if selected_script and selected_script.get("wrapper_path"):
        program_arguments = f"""
    <array>
        <string>/bin/bash</string>
        <string>{selected_script['wrapper_path']}</string>
    </array>""".rstrip()
    else:
        program_arguments = f"""
    <array>
        <string>python3</string>
        <string>{script_path}</string>
        <string>--headless</string>
    </array>""".rstrip()
    
    plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.juejin.autosignin</string>
    <key>ProgramArguments</key>
{program_arguments}
    <key>StartCalendarInterval</key>
    <array>
        <dict>
            <key>Hour</key>
            <integer>{hour}</integer>
            <key>Minute</key>
            <integer>{minute}</integer>
        </dict>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StandardOutPath</key>
    <string>{Path.home()}/.juejin_auto.log</string>
    <key>StandardErrorPath</key>
    <string>{Path.home()}/.juejin_auto.error.log</string>
</dict>
</plist>'''
    
    with open(PLIST_PATH, "w") as f:
        f.write(plist_content)
    
    script_name = "未知"
    for key, s in AVAILABLE_SCRIPTS.items():
        if s['path'] == script_path:
            script_name = s['name']
            break
    
    print(f"✅ 定时任务已设置:")
    print(f"   脚本: {script_name}")
    print(f"   时间: 每天 {hour:02d}:{minute:02d}")
    return True

def delete_cron():
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
        print("✅ 定时任务已删除")
    else:
        print("ℹ️ 没有设置定时任务")
    return True

def run_script(script_path):
    print(f"\n🚀 正在执行脚本...")
    result = subprocess.run(["python3", script_path], check=False)
    if result.returncode == 0:
        print("✅ 执行完成")
    else:
        print(f"❌ 执行失败，返回码: {result.returncode}")
    return result.returncode == 0

def interactive_setup():
    list_scripts()
    
    print("\n请选择要定时执行的脚本编号: ", end="")
    choice = input().strip()
    
    if choice not in AVAILABLE_SCRIPTS:
        print("❌ 无效选择")
        return
    
    script = AVAILABLE_SCRIPTS[choice]
    
    print(f"\n已选择: {script['name']}")
    print("请输入执行时间 (小时 分钟, 如 9 24): ", end="")
    time_input = input().strip()
    
    try:
        parts = time_input.split()
        if len(parts) != 2:
            print("❌ 格式错误，请输入: 小时 分钟")
            return
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            print("❌ 时间范围错误")
            return
    except:
        print("❌ 请输入数字")
        return
    
    set_cron(hour, minute, script['path'])
    
    print("\n是否立即执行一次? (y/n): ", end="")
    if input().strip().lower() == 'y':
        run_script(script['path'])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--check":
            result = check_cron()
            if result:
                print(f"⏰ 已设置定时任务:")
                print(f"   脚本: {result[1]}")
                print(f"   时间: 每天 {result[0]}")
            else:
                print("❌ 未设置定时任务")
        
        elif cmd == "--set" and len(sys.argv) >= 4:
            try:
                hour = int(sys.argv[2])
                minute = int(sys.argv[3])
                script_path = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_SCRIPT_PATH
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    set_cron(hour, minute, script_path)
                else:
                    print("❌ 时间格式错误")
            except:
                print("❌ 使用: --set <小时> <分钟> [脚本路径]")
        
        elif cmd == "--delete":
            delete_cron()
        
        elif cmd == "--run":
            script_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_SCRIPT_PATH
            run_script(script_path)
        
        elif cmd == "--interactive":
            interactive_setup()
        
        else:
            print("""
📋 定时任务管理:
  --check              检查定时任务
  --set <小时> <分钟> [脚本]  设置定时任务
  --delete             删除定时任务
  --run [脚本]        执行脚本
  --interactive        交互式设置
            """)
    else:
        result = check_cron()
        if result:
            print(f"⏰ 已设置定时任务: {result[1]} 每天 {result[0]}")
        else:
            print("❌ 未设置定时任务")
            print("\n运行 --interactive 交互式设置")
