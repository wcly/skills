import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

USER_DATA_DIR = str(Path.home() / ".juejin_browser_data")

async def main():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False, 
            args=['--start-maximized'],
            viewport={'width': 1280, 'height': 800}
        )
        
        page = await context.new_page()
        
        await page.goto("https://juejin.cn/user/center/lottery?from=lucky_lottery_menu_bar")
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)
        
        html = await page.content()
        with open("/tmp/lottery_page.html", "w") as f:
            f.write(html)
        
        print("页面已保存到 /tmp/lottery_page.html")
        
        buttons = await page.locator("button").all()
        print(f"\n找到 {len(buttons)} 个按钮:")
        for i, btn in enumerate(buttons):
            text = await btn.text_content()
            print(f"  {i+1}. {text[:50] if text else 'No text'}")
        
        await asyncio.sleep(5)
        await context.close()

asyncio.run(main())
