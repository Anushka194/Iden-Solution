# ====================================================
# Product Data Extraction Script
# ====================================================
# This script performs the following steps:
# 1. Session management (reuses authentication if available)
# 2. Authentication (login if no session exists)
# 3. Navigation through dashboard menus
# 4. Data extraction from the product table with pagination
# 5. Exporting the extracted data to JSON
# ====================================================

import os
import json
import asyncio
from playwright.async_api import async_playwright


# 1. Main workflow - Session Management
async def main():
    SESSION_FILE = "session.json"
    session_available = os.path.exists(SESSION_FILE)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)  # Visible mode for debugging
        if session_available:
            # Load previous authentication state
            context = await browser.new_context(storage_state=SESSION_FILE)
        else:
            # Start a fresh session
            context = await browser.new_context()

        page = await context.new_page()

        # 2. Authentication (if needed)
        if not session_available:
            await page.goto("YOUR_LOGIN_URL_HERE")

            await page.locator("#username_field_id").fill("YOUR_USERNAME")
            await page.locator("#password_field_id").fill("YOUR_PASSWORD")
            await page.locator("#login_button_id").click()

            # Confirm login success by waiting for a known dashboard element
            await page.locator("#dashboard_element_id").wait_for()

            # Save session state for future runs
            await context.storage_state(path=SESSION_FILE)


        # 3. Navigation to Product Table
        await page.locator("text=Open Dashboard Menu").click()
        await page.locator("text=Data Tools").click()
        await page.locator("text=Inventory Options").click()
        await page.locator("text=Open Products Drawer").click()

        # Ensure the table is fully loaded
        await page.locator("#product_table_id").wait_for()


        # 4. Data Extraction
        collected_products = []

        while True:
            rows = await page.locator("tr.product_row_class").all()

            for row in rows:
                name = await row.locator(".product_name_class").inner_text()
                price = await row.locator(".product_price_class").inner_text()

                product_record = {
                    "name": name.strip(),
                    "price": price.strip()
                }
                collected_products.append(product_record)

            # Check for pagination
            next_button = page.locator("#next_page_button_id")
            if await next_button.is_enabled():
                await next_button.click()
                await page.wait_for_selector("#product_table_id")
            else:
                break

        # 4. Export Data to JSON
        with open("products.json", "w", encoding="utf-8") as file_handle:
            json.dump(collected_products, file_handle, indent=4)

        print(f"Data export completed. {len(collected_products)} records saved to products.json.")


# Script Entry Point
if __name__ == "__main__":
    asyncio.run(main())
