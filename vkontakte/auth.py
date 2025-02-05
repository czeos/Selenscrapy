import asyncio
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from vkontakte.logger import vk_logger
from pathlib import Path
from vk_api import VkApi, AuthError, ApiError, LoginRequired

STATE_FLD = Path(__file__).parent / 'auth_states'

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"

def save_authentication_state(login: str, password: str) -> None:
    storage_path = STATE_FLD / f'{login}_auth_state.json'
    with sync_playwright() as p:
        browser =  p.chromium.launch(headless=True)
        context =  browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1280, "height": 720},
            extra_http_headers={"X-Requested-With": "XMLHttpRequest"},
        )
        page =  context.new_page()

        page.goto("https://vkhost.github.io/")

        with context.expect_page() as new_page_info:
            page.click("button:has-text('vk.com')")
        auth_page = new_page_info.value

        auth_page.fill("input[name='email']", login)
        auth_page.fill("input[name='pass']", password)

        sign_in_button = auth_page.get_by_role("button", name="Sign in", exact=True)
        sign_in_button.wait_for(state="visible")
        sign_in_button.click()

        context.storage_state(path=storage_path)
        print(f"Authentication state saved to {storage_path}.")

        browser.close()

def authentication_with_state(login: str) -> str:
    storage_path = STATE_FLD / f'{login}_auth_state.json'
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=storage_path)
        page = context.new_page()

        page.goto("https://vkhost.github.io/")
        page.click("button:has-text('vk.com')")

        try:
            new_tab = context.wait_for_event("page", timeout=10000)
            new_tab.wait_for_selector("button.flat_button.fl_r.button_indent", timeout=5000)
            new_tab.click("button.flat_button.fl_r.button_indent")
        except TimeoutError:
            vk_logger.ERROR("Authentication: New tab or 'Allow' button did not load correctly.")
            browser.close()
            return

        try:
            new_tab.wait_for_load_state("load", timeout=5000)
            result_url = new_tab.url
            parsed_url = urlparse(result_url)
            fragment = parse_qs(parsed_url.fragment)
            token = fragment.get('access_token', [''])[0]
            return token
        except TimeoutError:
            vk_logger.ERROR("Result page did not load correctly.")
        finally:
            browser.close()
