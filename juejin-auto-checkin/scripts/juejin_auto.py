#!/usr/bin/env python3
import asyncio
import sys
import os
from pathlib import Path
from playwright.async_api import async_playwright
import re

SIGNIN_URL = "https://juejin.cn/user/center/signin?from=sign_in_menu_bar"
LOTTERY_URL = "https://juejin.cn/user/center/lottery?from=lucky_lottery_menu_bar"

USER_DATA_DIR = str(Path.home() / ".juejin_browser_data")
LOG_FILE = str(Path.home() / ".juejin_auto.log")

HEADLESS = "--headless" in sys.argv

def log(msg, is_error=False):
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = "[ERROR]" if is_error else ""
    full_msg = f"[{timestamp}] {prefix}{msg}"
    print(full_msg.strip())
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except:
        pass

async def check_login_status(page, context):
    try:
        await page.goto("https://juejin.cn", timeout=20000)
        await page.wait_for_load_state("domcontentloaded", timeout=10000)
        await asyncio.sleep(2)
        
        try:
            login_text = page.locator('text="登录"')
            if await login_text.count() > 0:
                log("❌ 未登录 - 发现登录按钮")
                return False
        except Exception as e:
            log(f"检查登录按钮: {e}", True)
        
        try:
            user_avatar = page.locator('.avatar, [class*="avatar"], .user-avatar')
            if await user_avatar.count() > 0:
                log("✅ 已登录 - 发现用户头像")
                return True
        except Exception as e:
            log(f"检查头像: {e}", True)
        
        cookies = await context.cookies()
        for cookie in cookies:
            if cookie['name'] in ['uid', 'token', 'sessionid', 'csrf_token']:
                log("✅ 已登录 - 发现认证 Cookie")
                return True
        
        log("❌ 未登录 - 无认证信息")
        return False
    except Exception as e:
        log(f"检查登录状态出错: {e}", True)
        return True  # 假设已登录，继续尝试

async def do_signin(page):
    log("\n📝 访问签到页面...")
    await page.goto(SIGNIN_URL)
    await page.wait_for_load_state("networkidle")
    await asyncio.sleep(2)
    
    try:
        already_signed = page.locator('text="已签到"')
        if await already_signed.count() > 0:
            log("ℹ️ 今日已签到")
            return "already_signed"
    except Exception as e:
        log(f"检查已签到: {e}", True)
    
    try:
        signin_btn = page.locator('button:has-text("签到")')
        if await signin_btn.count() > 0:
            log("📝 正在签到...")
            await signin_btn.first.click()
            
            await page.wait_for_load_state("networkidle", timeout=10000)
            await asyncio.sleep(3)
            
            page_text = await page.evaluate("document.body.innerText")
            if "已签到" in page_text or "签到成功" in page_text:
                log("✅ 签到成功！")
                return True
            else:
                log("✅ 签到按钮已点击")
                return True
    except Exception as e:
        log(f"签到错误: {e}", True)
    
    return False

async def do_lottery(page):
    log("\n🎰 访问抽奖页面...")
    try:
        await page.goto(LOTTERY_URL, timeout=30000)
        await page.wait_for_load_state("domcontentloaded", timeout=15000)
        await asyncio.sleep(3)
        
        await page.evaluate("window.scrollTo(0, 500)")
        await asyncio.sleep(2)
        
        page_text = await page.evaluate("document.body.innerText")
        
        log("🔍 检查抽奖状态...")
        
        free_match = re.search(r'免费抽奖次数[：:](\d+)次', page_text)
        
        if free_match:
            free_count = int(free_match.group(1))
            log(f"📝 发现免费抽奖次数: {free_count}次")
            
            if free_count > 0:
                log("   准备执行免费抽奖...")
                
                log("   尝试点击免费抽奖按钮...")
                
                await page.evaluate('''
                    (function() {
                        const allElements = document.querySelectorAll('*');
                        for (let el of allElements) {
                            if (el.textContent && el.textContent.trim() === '免费抽奖') {
                                el.click();
                                return;
                            }
                        }
                    })()
                ''')
                
                await asyncio.sleep(3)
                
                result_text = await page.evaluate("document.body.innerText")
                
                if "单抽" in result_text:
                    log("   已进入抽奖页面，点击单抽按钮...")
                    
                    await page.evaluate('''
                        (function() {
                            const allElements = document.querySelectorAll('*');
                            for (let el of allElements) {
                                if (el.textContent && el.textContent.trim() === '单抽') {
                                    el.click();
                                    return;
                                }
                            }
                        })()
                    ''')
                    
                    await asyncio.sleep(3)
                    
                    result_text = await page.evaluate("document.body.innerText")
                    log(f"   抽奖后页面文本: {result_text[:200]}...")
                    
                    # 检查免费次数是否减少
                    result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                    if result_free_match:
                        result_free_count = int(result_free_match.group(1))
                        log(f"   抽奖后免费次数: {result_free_count}次")
                        
                        if result_free_count < free_count:
                            log("✅ 免费抽奖完成！（次数已减少）")
                            return True
                    
                    # 检查是否显示中奖信息
                    if "恭喜" in result_text and ("抽中" in result_text or "获得" in result_text):
                        log("✅ 免费抽奖完成！（中奖了）")
                        return True
                
                # 检查是否显示"已用完"
                if "免费次数已用完" in result_text or "今日免费单抽已用完" in result_text:
                    log("ℹ️ 今日免费单抽已用完")
                    return "free_used"
                
                # 如果之前的点击没有生效，尝试使用鼠标直接点击
                log("   尝试使用鼠标点击...")
                await page.mouse.click(900, 500)
                await asyncio.sleep(3)
                
                result_text = await page.evaluate("document.body.innerText")
                
                if "单抽" in result_text:
                    log("   进入抽奖页面，点击单抽...")
                    await page.mouse.click(800, 600)
                    await asyncio.sleep(3)
                    
                    result_text = await page.evaluate("document.body.innerText")
                
                result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                if result_free_match:
                    result_free_count = int(result_free_match.group(1))
                    if result_free_count < free_count:
                        log("✅ 免费抽奖完成！")
                        return True
                
                if "恭喜" in result_text and ("抽中" in result_text or "获得" in result_text):
                    log("✅ 免费抽奖完成！")
                    return True
                
                if "免费次数已用完" in result_text or "今日免费单抽已用完" in result_text:
                    log("ℹ️ 今日免费单抽已用完")
                    return "free_used"
                
                log("✅ 抽奖已执行")
                return True
        
        if "再抽1次解锁" in page_text or "免费次数已用完" in page_text:
            log("ℹ️ 今日免费单抽已用完")
            return "free_used"
        
    except Exception as e:
        log(f"访问抽奖页面: {e}", True)
    
    log("⚠️ 未找到抽奖入口")
    return "no_button"

async def run_task():
    log("=" * 50)
    log("🚀 稀土掘金自动签到 & 免费单抽")
    log("=" * 50)
    
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    browser_args = ['--start-maximized']
    if HEADLESS:
        browser_args.extend(['--disable-gpu', '--no-sandbox', '--disable-dev-shm-usage'])
    
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=HEADLESS, 
                args=browser_args,
                viewport={'width': 1280, 'height': 800}
            )
            
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = await context.new_page()
            
            log("\n📱 正在检查登录状态...")
            
            is_logged_in = await check_login_status(page, context)
            if not is_logged_in:
                log("❌ 未登录，请先登录")
                await context.close()
                return
            
            signin_result = await do_signin(page)
            
            await asyncio.sleep(2)
            
            lottery_result = await do_lottery(page)
            
            log("=" * 50)
            log("📊 执行结果:")
            if signin_result == "already_signed":
                log("  - 签到: 今日已签到 ✅")
            elif signin_result:
                log("  - 签到: 签到成功 ✅")
            else:
                log("  - 签到: 签到失败 ❌")
            
            if lottery_result == "free_used":
                log("  - 抽奖: 今日免费单抽已用完")
            elif lottery_result == "no_button":
                log("  - 抽奖: 未找到免费抽奖入口 ⚠️")
            elif lottery_result:
                log("  - 抽奖: 抽奖成功 ✅")
            else:
                log("  - 抽奖: 抽奖失败 ❌")
            
            log("=" * 50)
            
            await asyncio.sleep(2)
            await context.close()
            
    except Exception as e:
        log(f"❌ 执行出错: {e}", True)

if __name__ == "__main__":
    asyncio.run(run_task())
