import asyncio
import requests
import time
from playwright.async_api import async_playwright
from twocaptcha import TwoCaptcha
import random
from playwright_stealth import stealth_async
import time
from fake_useragent import UserAgent

API_KEY = 'bb8ef87d36b4959711ed4d1c0ebcd930'
solver = TwoCaptcha(API_KEY)
ua = UserAgent()
USER_AGENTS = [
    # Google Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    
    # Google Chrome on MacOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
    
    # Mozilla Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
    
    # Mozilla Firefox on MacOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0",
    
    # Apple Safari on MacOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    
    # Microsoft Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.59 Safari/537.36 Edg/91.0.864.59",
    
    # Mobile Safari on iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
    
    # Google Chrome on Android
    "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Pixel 3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
]

def get_stealth_headers():
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "upgrade-insecure-requests": "1",
        # Add more headers as needed
    }
    return headers

def read_proxies(file_path):
    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

async def random_delay():
    time.sleep(random.uniform(1, 3))

async def human_like_mouse_move(page, selector):
    element = await page.query_selector(selector)
    bounding_box = await element.bounding_box()
    x = bounding_box['x'] + bounding_box['width'] / 2
    y = bounding_box['y'] + bounding_box['height'] / 2
    for _ in range(10):
        await page.mouse.move(
            x + random.uniform(-10, 10),
            y + random.uniform(-10, 10)
        )
        await asyncio.sleep(random.uniform(0.01, 0.1))
    await page.mouse.click(x, y)

def get_mt_captcha_token(site_key, page_url):    

    attempts = 0
    max_attempts = 20

    while attempts < max_attempts:
        result = solver.mtcaptcha(sitekey=site_key, url=page_url)
        if not result['captchaId']:
            print ('Captcha unresolved')
            attempts += 1
        else: 
            captcha_id = result['captchaId']
            return captcha_id

def get_captcha_solution(captcha_id):
    url = f'http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1'
    max_attempts = 20
    attempts = 0

    while attempts < max_attempts:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 1:
                    return result.get('request')
                elif result.get('request') == 'CAPCHA_NOT_READY':
                    print('Captcha not ready, sleeping for 5 seconds...')
                    time.sleep(5)
                    attempts += 1
                else:
                    print(f'Error solving captcha: {result["request"]}')
                    return None
            else:
                print(f'Error checking captcha status: {response.status_code} - {response.text}')
                return None
        except requests.exceptions.RequestException as e:
            print(f'Request Error: {e}')
            return None

    print('Max attempts reached. Captcha solving failed.')
    return None

async def main():

    proxies = read_proxies('residental.txt')
    # Randomly select a proxy from the list
    proxy = random.choice(proxies)
    
    # Parse the proxy string
    proxy_parts = proxy.split(':')
    proxy_ip = proxy_parts[0]
    proxy_port = proxy_parts[1]
    proxy_username = proxy_parts[2]
    proxy_password = proxy_parts[3]

    site_key = 'MTPublic-tukBAQJML'
    login_url = 'https://shop.garena.my/app/100067/idlogin?next=/app/100067/buy/0'
    page_url = 'https://shop.garena.my/app/100067/idlogin?next=/app/100067/buy/0'

    user_agent = random.choice(USER_AGENTS)

    async with async_playwright() as p:
        # browser = await p.chromium.launch(headless=False)
        browser = await p.firefox.launch(headless=False, proxy={
            'server': f'{proxy_ip}:{proxy_port}',
            'username': proxy_username,
            'password': proxy_password
        }, args=[
            '--disable-blink-features=AutomationControlled'
        ])
        context = await browser.new_context(
            user_agent=user_agent,  # Random user agent
            extra_http_headers=get_stealth_headers()
        )

        page = await context.new_page()
        await stealth_async(page)

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
        await context.set_extra_http_headers({"User-Agent": user_agent})

        # Navigate to the login page
        await page.goto(login_url)

        await page.wait_for_selector('input[name="playerId"]')
        await random_delay()
        await human_like_mouse_move(page, 'input[name="playerId"]')

        # Fill in the login form
        await page.fill('input[name="playerId"]', '9109146880')
        await page.click('input[type="submit"]')

        # Wait for the MTCaptcha iframe to appear
        await page.wait_for_selector('iframe')

        # Get the MTCaptcha token
        captcha_id = get_mt_captcha_token(site_key, page_url)
        if captcha_id:
            print(f'CAPTCHA ID: {captcha_id}')
            solution = get_captcha_solution(captcha_id)
            if solution:
                print(f'Solved CAPTCHA: {solution}')

                # Inject the MTCaptcha token into the form and submit 
                iframe_element = await page.wait_for_selector('iframe') 
                frame = await iframe_element.content_frame()
                await frame.wait_for_load_state('networkidle')
                await frame.evaluate(f'token => window.captchaCallback("{solution}")', solution)
                print('Captcha solution injected successfully.')

                # Wait for navigation after solving CAPTCHA
                await page.wait_for_load_state('networkidle')
                print ('arrived!!!')
                await page.wait_for_timeout(1000)
                await page.click('input[type="submit"]')
                print ('done??')
                await page.wait_for_timeout(7000)
                print (page.url)

                if page.url == 'https://shop.garena.my/app/100067/buy/0':
                    print('Login Success!') 
                       
            else:
                print('Failed to solve CAPTCHA')
                return
        else:
            print('Failed to get CAPTCHA ID')
            return

        # Following actions
        await page.click('input[type="submit"]')
        await page.wait_for_selector('#form')
        await page.click('text="115 Diamond"')
        await page.wait_for_selector('text="Wallet"')
        await page.click('text="Wallet"')
        await page.click('#pc_div_669')
        await page.wait_for_selector('#sign-in-email')
        await page.fill('#sign-in-email', 'sandeshbc911@gmail.com')
        await page.fill('#signInPassword', '66Fh@tX4npFLAjZ')
        await page.click('#signin-email-submit-button')
        await page.wait_for_selector('input[name="security_key"]')
        await page.fill('input[name="security_key"]')
        await page.click('input[type="submit"]')
        await page.wait_for_selector('text="Back to merchant"')
        await page.click('text="Back to merchant"')
        await page.wait_for_selector('text="Congratulations!"')
        print ('Congratulations!')

        await browser.close()

# Run the bypass function
asyncio.run(main())
