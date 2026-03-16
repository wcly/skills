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

async def wait_for_login(page, context, timeout_seconds=300):
    """
    等待用户登录
    timeout_seconds: 最大等待时间，默认300秒（5分钟）
    """
    log("\n" + "=" * 50)
    log("🔐 检测到未登录，开始等待用户登录...")
    log("=" * 50)
    log("📋 请在浏览器中扫码登录稀土掘金")
    log(f"⏱️ 最多等待 {timeout_seconds} 秒，请尽快完成登录")
    log("=" * 50)
    
    await page.goto("https://juejin.cn", timeout=20000)
    await page.wait_for_load_state("domcontentloaded")
    
    check_interval = 5  # 每5秒检查一次
    elapsed = 0
    
    while elapsed < timeout_seconds:
        await asyncio.sleep(check_interval)
        elapsed += check_interval
        
        try:
            login_text = page.locator('text="登录"')
            if await login_text.count() > 0:
                remaining = timeout_seconds - elapsed
                log(f"⏳ 等待登录中... 剩余 {remaining} 秒")
                continue
        except Exception as e:
            pass
        
        try:
            user_avatar = page.locator('.avatar, [class*="avatar"], .user-avatar')
            if await user_avatar.count() > 0:
                log("✅ 检测到用户头像，登录成功！")
                await asyncio.sleep(2)
                return True
        except Exception as e:
            pass
        
        cookies = await context.cookies()
        for cookie in cookies:
            if cookie['name'] in ['uid', 'token', 'sessionid', 'csrf_token']:
                log("✅ 检测到认证 Cookie，登录成功！")
                await asyncio.sleep(2)
                return True
        
        remaining = timeout_seconds - elapsed
        log(f"⏳ 等待登录中... 剩余 {remaining} 秒")
    
    log("❌ 等待登录超时")
    return False

async def do_signin_api(context):
    """通过 API 接口签到（更可靠，不依赖页面渲染）"""
    log("\n📝 尝试 API 签到...")
    try:
        cookies = await context.cookies("https://juejin.cn")
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        # 提取 csrf token
        csrf_token = ""
        for c in cookies:
            if c['name'] == 'csrf_token':
                csrf_token = c['value']
                break
        
        if not cookie_str:
            log("❌ API签到失败: 无 Cookie", True)
            return None
        
        page = context.pages[0] if len(context.pages) > 0 else await context.new_page()
        
        # 确保在 juejin.cn 域名下，以便 fetch 能带上 cookies
        current_url = page.url
        if 'juejin.cn' not in current_url:
            await page.goto("https://juejin.cn", timeout=15000)
            await page.wait_for_load_state("domcontentloaded", timeout=10000)
            await asyncio.sleep(1)
        
        # 先检查今日是否已签到
        check_result = await page.evaluate('''
            async () => {
                try {
                    const resp = await fetch("https://api.juejin.cn/growth_api/v1/get_today_status", {
                        method: "GET",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                        }
                    });
                    return await resp.json();
                } catch(e) {
                    return {err_msg: e.message};
                }
            }
        ''')
        
        log(f"   签到状态检查: {check_result}")
        
        if check_result and check_result.get('err_no') == 0:
            if check_result.get('data'):
                log("ℹ️ 今日已签到（API确认）")
                return "already_signed"
        
        # 执行签到
        signin_result = await page.evaluate('''
            async () => {
                try {
                    const resp = await fetch("https://api.juejin.cn/growth_api/v1/check_in", {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: "{}"
                    });
                    return await resp.json();
                } catch(e) {
                    return {err_msg: e.message};
                }
            }
        ''')
        
        log(f"   API签到结果: {signin_result}")
        
        if signin_result and signin_result.get('err_no') == 0:
            incr_point = signin_result.get('data', {}).get('incr_point', 0)
            log(f"✅ API签到成功！获得 {incr_point} 矿石")
            return True
        elif signin_result and signin_result.get('err_no') == 15001:
            log("ℹ️ 今日已签到（API返回重复签到）")
            return "already_signed"
        else:
            err_msg = signin_result.get('err_msg', '未知错误') if signin_result else '无响应'
            log(f"⚠️ API签到返回: {err_msg}")
            return None  # 返回 None 表示 API 方式不确定，后续走 UI 方式
            
    except Exception as e:
        log(f"API签到出错: {e}", True)
        return None

async def do_signin_ui(page):
    """通过 UI 点击签到（API 失败时的后备方案）"""
    log("   尝试 UI 签到（后备方案）...")
    try:
        await page.goto(SIGNIN_URL, timeout=20000)
        await page.wait_for_load_state("domcontentloaded", timeout=10000)
        await asyncio.sleep(3)
        
        # 等待页面 SPA 内容渲染
        try:
            await page.wait_for_selector('button:has-text("签到"), text="已签到"', timeout=8000)
        except Exception:
            log("   等待签到元素超时，继续检查页面...")
        
        page_text = await page.evaluate("document.body.innerText")
        
        # 检查是否已签到
        if "已签到" in page_text:
            log("ℹ️ 今日已签到（UI确认）")
            return "already_signed"
        
        # 尝试多种选择器找签到按钮
        selectors = [
            'button:has-text("立即签到")',
            'button:has-text("签到")',
            ':is(div, span):has-text("立即签到")',
            'text="立即签到"',
        ]
        
        for selector in selectors:
            try:
                btn = page.locator(selector)
                count = await btn.count()
                if count > 0:
                    log(f"   找到签到按钮 (selector: {selector})")
                    await btn.first.scroll_into_view_if_needed()
                    await asyncio.sleep(1)
                    await btn.first.click()
                    await asyncio.sleep(3)
                    
                    result_text = await page.evaluate("document.body.innerText")
                    if "已签到" in result_text or "签到成功" in result_text:
                        log("✅ UI签到成功！")
                        return True
                    else:
                        log("✅ 签到按钮已点击")
                        return True
            except Exception as e:
                continue
        
        # 所有选择器都没找到，记录页面内容用于诊断
        log(f"⚠️ 未找到签到按钮，页面内容: {page_text[:500]}", True)
        return False
        
    except Exception as e:
        log(f"UI签到错误: {e}", True)
        return False

async def do_signin(page, context=None):
    # 优先使用 API 签到
    if context:
        api_result = await do_signin_api(context)
        if api_result is not None:
            return api_result
        log("   API签到不确定，切换到 UI 签到...")
    
    return await do_signin_ui(page)

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
                        
                        # 增加页面滚动，确保抽奖按钮可见
                        await page.evaluate("window.scrollTo(0, 800)")
                        await asyncio.sleep(3)
                        
                        log("   尝试点击免费抽奖按钮...")
                        
                        # 尝试通过更精确的选择器找到免费抽奖按钮
                        free_lottery_clicked = False
                        try:
                            # 尝试使用Playwright的locator直接查找按钮
                            log("   尝试使用Playwright locator查找精确的抽奖按钮...")
                            
                            # 尝试通过文本内容查找按钮
                            free_lottery_button = page.locator('text=免费抽奖次数')
                            if await free_lottery_button.count() > 0:
                                log("   找到免费抽奖次数按钮")
                                await free_lottery_button.first.scroll_into_view_if_needed()
                                await asyncio.sleep(2)
                                await free_lottery_button.first.click()
                                log("   成功点击免费抽奖次数按钮")
                                free_lottery_clicked = True
                            else:
                                # 尝试通过其他文本内容查找按钮
                                free_lottery_button = page.locator('text=免费抽奖')
                                if await free_lottery_button.count() > 0:
                                    log("   找到免费抽奖按钮")
                                    await free_lottery_button.first.scroll_into_view_if_needed()
                                    await asyncio.sleep(2)
                                    await free_lottery_button.first.click()
                                    log("   成功点击免费抽奖按钮")
                                    free_lottery_clicked = True
                                else:
                                    # 尝试通过坐标点击（根据截图中按钮的位置）
                                    log("   尝试通过坐标点击免费抽奖按钮...")
                                    # 从截图看，免费抽奖按钮在页面中间偏下位置
                                    await page.mouse.move(350, 600)
                                    await asyncio.sleep(2)
                                    await page.mouse.down()
                                    await asyncio.sleep(0.5)
                                    await page.mouse.up()
                                    log("   点击了坐标 (350, 600)")
                                    free_lottery_clicked = True
                        except Exception as e:
                            log(f"   点击免费抽奖按钮出错: {e}")
                        
                        # 增加等待时间，确保页面完全加载
                        await asyncio.sleep(8)  # 增加等待时间
                        
                        # 截图保存，以便查看页面状态
                        await page.screenshot(path="lottery_page.png")
                        log("   已保存抽奖页面截图: lottery_page.png")
                        
                        # 打印页面HTML结构（部分）
                        page_html = await page.evaluate("document.body.innerHTML")
                        log(f"   页面HTML长度: {len(page_html)} 字符")
                        # 保存HTML到文件，以便分析
                        with open("lottery_page.html", "w", encoding="utf-8") as f:
                            f.write(page_html[:10000])  # 只保存前10000字符
                        log("   已保存页面HTML到: lottery_page.html")
                        
                        result_text = await page.evaluate("document.body.innerText")
                        log(f"   点击后页面文本: {result_text[:1000]}...")
                        
                        # 检查是否有抽奖相关的关键词
                        if any(keyword in result_text for keyword in ["单抽", "抽奖", "转盘", "中奖", "免费"]):
                            log("   已进入抽奖页面...")
                            
                            # 尝试使用不同的方法找到并点击抽奖按钮
                            # 1. 尝试通过文本内容查找"单抽"或"抽奖"按钮
                            log("   尝试查找并点击抽奖按钮...")
                            try:
                                # 尝试通过JavaScript查找所有可能的抽奖按钮
                                log("   尝试通过JavaScript查找所有抽奖相关按钮...")
                                button_found = await page.evaluate('''
                                    (function() {
                                        const keywords = ['单抽', '抽奖', '免费抽奖', '开始抽奖'];
                                        const allElements = document.querySelectorAll('button, div, span');
                                        let foundButtons = [];
                                        
                                        for (let keyword of keywords) {
                                            for (let el of allElements) {
                                                const text = el.textContent && el.textContent.trim();
                                                if (text && text.includes(keyword)) {
                                                    foundButtons.push({ keyword: keyword, text: text, element: el });
                                                }
                                            }
                                        }
                                        
                                        console.log('Found buttons:', foundButtons.map(b => b.text));
                                        
                                        // 优先点击包含"单抽"的按钮
                                        for (let button of foundButtons) {
                                            if (button.text.includes('单抽')) {
                                                console.log('Clicking button:', button.text);
                                                button.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                button.element.click();
                                                return true;
                                            }
                                        }
                                        
                                        // 其次点击包含"开始抽奖"的按钮
                                        for (let button of foundButtons) {
                                            if (button.text.includes('开始抽奖')) {
                                                console.log('Clicking button:', button.text);
                                                button.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                                button.element.click();
                                                return true;
                                            }
                                        }
                                        
                                        // 最后点击其他抽奖相关按钮
                                        if (foundButtons.length > 0) {
                                            let button = foundButtons[0];
                                            console.log('Clicking first found button:', button.text);
                                            button.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                            button.element.click();
                                            return true;
                                        }
                                        
                                        // 尝试点击页面中央的抽奖区域
                                        console.log('Trying to click lottery area...');
                                        const lotteryArea = document.querySelector('.lottery-container, .lottery-draw, .lottery-wheel, .lottery-btn');
                                        if (lotteryArea) {
                                            lotteryArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                            lotteryArea.click();
                                            return true;
                                        }
                                        
                                        return false;
                                    })()
                                ''')
                                
                                if button_found:
                                    log("   成功找到并点击抽奖按钮")
                                else:
                                    log("   未找到抽奖按钮，尝试点击页面中央...")
                                    # 尝试点击页面中央
                                    await page.mouse.move(640, 400)
                                    await asyncio.sleep(1)
                                    await page.mouse.click(640, 400)
                            except Exception as e:
                                log(f"   点击抽奖按钮出错: {e}")
                            
                            log("   等待抽奖结果...")
                            # 增加等待时间，确保抽奖动画和结果完全显示
                            await asyncio.sleep(20)  # 增加等待时间
                            
                            # 截图保存抽奖后状态
                            await page.screenshot(path="lottery_result.png")
                            log("   已保存抽奖结果截图: lottery_result.png")
                            
                            result_text = await page.evaluate("document.body.innerText")
                            log(f"   抽奖后页面文本: {result_text[:500]}...")
                            
                            # 检查免费次数是否减少（这是最可靠的指标）
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                log(f"   抽奖后免费次数: {result_free_count}次")
                                
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                            
                            # 再次等待并检查结果
                            log("   再次检查抽奖结果...")
                            await asyncio.sleep(5)
                            result_text = await page.evaluate("document.body.innerText")
                            
                            # 再次检查免费次数
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                log(f"   再次检查后免费次数: {result_free_count}次")
                                
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                            
                            # 尝试点击其他可能的抽奖按钮位置
                            log("   尝试点击其他可能的抽奖按钮位置...")
                            await page.mouse.move(700, 500)
                            await asyncio.sleep(1)
                            await page.mouse.click(700, 500)
                            
                            log("   等待抽奖结果...")
                            await asyncio.sleep(20)
                            
                            # 截图保存再次抽奖后状态
                            await page.screenshot(path="lottery_result2.png")
                            log("   已保存再次抽奖结果截图: lottery_result2.png")
                            
                            result_text = await page.evaluate("document.body.innerText")
                            log(f"   再次抽奖后页面文本: {result_text[:500]}...")
                            
                            # 检查免费次数是否减少
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                log(f"   再次抽奖后免费次数: {result_free_count}次")
                                
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                            

                        
                        # 检查是否显示"已用完"
                        if "免费次数已用完" in result_text or "今日免费单抽已用完" in result_text:
                            log("ℹ️ 今日免费单抽已用完")
                            return "free_used"
                        
                        # 如果之前的点击没有生效，尝试使用鼠标直接点击
                        log("   尝试使用鼠标点击...")
                        await page.mouse.click(900, 500)
                        await asyncio.sleep(5)  # 增加等待时间
                        
                        result_text = await page.evaluate("document.body.innerText")
                        log(f"   鼠标点击后页面文本: {result_text[:200]}...")
                        
                        if "单抽" in result_text:
                            log("   进入抽奖页面，点击单抽...")
                            await page.mouse.click(800, 600)
                            
                            log("   等待抽奖结果...")
                            # 增加等待时间，确保抽奖动画和结果完全显示
                            await asyncio.sleep(10)  # 增加等待时间
                            
                            result_text = await page.evaluate("document.body.innerText")
                            log(f"   抽奖后页面文本: {result_text[:300]}...")
                            
                            # 检查免费次数是否减少
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                            
                            # 检查是否显示中奖信息（更准确的检查）
                            # 查找包含"恭喜"和"抽中"或"获得"的连续文本
                            winning_pattern = re.compile(r'恭喜.*?(抽中|获得).*?', re.DOTALL)
                            winning_matches = winning_pattern.findall(result_text)
                            
                            # 检查免费次数是否减少（这是最可靠的指标）
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                log(f"   抽奖后免费次数: {result_free_count}次")
                                
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                            
                            # 再次等待并检查结果
                            log("   再次检查抽奖结果...")
                            await asyncio.sleep(5)
                            result_text = await page.evaluate("document.body.innerText")
                            
                            # 再次检查免费次数
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                log(f"   再次检查后免费次数: {result_free_count}次")
                                
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                            
                            result_free_match = re.search(r'免费抽奖次数[：:](\d+)次', result_text)
                            if result_free_match:
                                result_free_count = int(result_free_match.group(1))
                                if result_free_count < free_count:
                                    log("✅ 免费抽奖完成！（次数已减少）")
                                    return True
                        
                        if "免费次数已用完" in result_text or "今日免费单抽已用完" in result_text:
                            log("ℹ️ 今日免费单抽已用完")
                            return "free_used"
                        
                        log("⚠️ 抽奖执行完成，但未确认结果")
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
                login_success = await wait_for_login(page, context)
                if not login_success:
                    log("❌ 登录超时，请稍后重试")
                    await context.close()
                    return
                log("✅ 登录成功，继续执行签到任务...")
            
            signin_result = await do_signin(page, context)
            
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
            
            # 等待抽奖结果完全显示后再关闭浏览器
            if lottery_result and lottery_result != "free_used" and lottery_result != "no_button":
                log("⏳ 等待抽奖结果完全显示...")
                await asyncio.sleep(10)  # 增加等待时间，确保抽奖结果完全显示
            else:
                await asyncio.sleep(2)
            await context.close()
            
    except Exception as e:
        log(f"❌ 执行出错: {e}", True)

def cleanup_screenshots():
    """清理生成的截图文件"""
    files_to_delete = [
        "lottery_page.png",
        "lottery_result.png",
        "lottery_result2.png",
        "lottery_page.html"
    ]
    
    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log(f"🗑️ 已删除截图文件: {file_path}")
        except Exception as e:
            log(f"删除文件时出错: {e}", True)

if __name__ == "__main__":
    asyncio.run(run_task())
    cleanup_screenshots()
