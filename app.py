import os
import json
import logging
import random
import asyncio
import httpx
from dotenv import load_dotenv
from playwright.async_api import async_playwright, Page

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_URL = os.getenv("TARGET_URL") or os.getenv("FORUM_URL")

CSS_SELECTOR = 'div[role="article"]'

async def simulate_human_reading(page: Page):
    logger.info("Simulating human reading (scrolling)...")
    scroll_times = random.randint(2, 4)
    for _ in range(scroll_times):
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(2.0)

async def run_scraper(url: str) -> str:
    """
    Runs the Playwright scraper on-demand, injecting cookies from environmental
    variable or local cookies.json, and strictly cleaning up browser context.
    """
    logger.info(f"🚀 Starting Playwright scraper for URL: {url}")
    scraped_texts = []
    
    playwright = None
    browser = None
    context = None
    
    try:
        playwright = await async_playwright().start()
        logger.info("Launching headless Chromium browser...")
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        
        # Inject cookies
        cookies_injected = False
        
        # 1. Try to load from environmental variable (GitHub Secrets style)
        env_cookies = os.getenv("COOKIES_JSON") or os.getenv("FACEBOOK_COOKIES")
        if env_cookies:
            try:
                stripped_cookies = env_cookies.strip()
                # If it doesn't look like a standard JSON array/object, try to base64 decode it
                if not (stripped_cookies.startswith("[") or stripped_cookies.startswith("{")):
                    import base64
                    try:
                        decoded_bytes = base64.b64decode(stripped_cookies)
                        stripped_cookies = decoded_bytes.decode("utf-8")
                        logger.info("Detected and successfully decoded base64 cookies environment variable.")
                    except Exception as b64_err:
                        logger.warning(f"Could not base64 decode cookies, treating as raw: {b64_err}")
                
                cookies = json.loads(stripped_cookies)
                await context.add_cookies(cookies)
                cookies_injected = True
                logger.info("✅ Injected cookies from environment variable.")
            except Exception as e:
                logger.error(f"⚠️ Failed to parse cookies from env variable: {e}")
                
        # 2. Fall back to local cookies.json
        if not cookies_injected:
            cookies_path = "cookies.json"
            if os.path.exists(cookies_path):
                try:
                    with open(cookies_path, "r", encoding="utf-8") as f:
                        cookies = json.load(f)
                    await context.add_cookies(cookies)
                    cookies_injected = True
                    logger.info("✅ Injected cookies from local cookies.json file.")
                except Exception as e:
                    logger.error(f"⚠️ Failed to read local cookies.json: {e}")
                    
        if not cookies_injected:
            logger.warning("⚠️ No cookies injected! Scraping will proceed as an unauthenticated guest.")
            
        page = await context.new_page()
        
        logger.info(f"Navigating to {url}...")
        await page.goto(url, wait_until="domcontentloaded")
        
        # Simulate scrolling to trigger lazy-loaded posts
        await simulate_human_reading(page)
        
        post_elements = await page.locator(CSS_SELECTOR).all()
        logger.info(f"Found {len(post_elements)} post elements matching '{CSS_SELECTOR}'")
        
        # Extract text of the latest 5 posts
        for element in post_elements[:5]:
            try:
                text = await element.inner_text()
                if text.strip():
                    scraped_texts.append(text.strip())
            except Exception as e:
                logger.error(f"Error extracting text from post: {e}")
                
    except Exception as e:
        logger.error(f"Error in run_scraper: {e}")
        raise e
    finally:
        logger.info("Ensuring all Playwright resources are closed to free RAM...")
        if context:
            await context.close()
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
        logger.info("✅ Playwright resources cleaned up.")
        
    return "\n\n--- NEXT POST ---\n\n".join(scraped_texts)

async def analyze_data(text: str) -> str:
    """
    Placeholder analyze function returning a dummy string to user.
    """
    if not text.strip():
        return "لم يتم العثور على أية منشورات لتحليلها."
        
    analysis_result = (
        "📊 **تحليل مبدئي لبيانات الجروب (Event-Driven Runner)**\n\n"
        f"تم جلب منشورات بطول {len(text)} حرفاً.\n\n"
        "*(التحليل الكامل عبر الذكاء الاصطناعي DeepSeek سيتم إضافته لاحقاً)*\n\n"
        "**نص المنشورات التي تم جلبها:**\n"
    )
    posts = [p.strip() for p in text.split("--- NEXT POST ---") if p.strip()]
    for idx, post in enumerate(posts, 1):
        preview = post[:150] + "..." if len(post) > 150 else post
        analysis_result += f"🔹 **المنشور {idx}**:\n{preview}\n\n"
        
    return analysis_result

async def send_telegram_message(text: str):
    """
    Sends message to Telegram via direct HTTP POST.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    logger.info("Sending report to Telegram...")
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=30.0)
        if response.status_code == 200:
            logger.info("✅ Report sent to Telegram successfully!")
        else:
            logger.error(f"❌ Failed to send Telegram message: {response.status_code} - {response.text}")

async def main():
    if not TARGET_URL:
        logger.error("TARGET_URL environment variable is missing. Exit.")
        return
        
    # Send wake-up message
    await send_telegram_message(f"🔍 Starting scheduled analysis for: {TARGET_URL}...")
    
    try:
        scraped_text = await run_scraper(TARGET_URL)
        analysis_report = await analyze_data(scraped_text)
        await send_telegram_message(analysis_report)
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        await send_telegram_message(f"❌ Scraper run failed:\n`{str(e)}`")

if __name__ == "__main__":
    asyncio.run(main())
