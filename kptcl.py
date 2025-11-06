# kptcl.py
import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Try to use undetected_chromedriver (stealth). If not available, fall back to normal selenium+webdriver_manager.
try:
    import undetected_chromedriver as uc
    UC_AVAILABLE = True
except Exception:
    UC_AVAILABLE = False

# Fallback imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WM_AVAILABLE = True
except Exception:
    WM_AVAILABLE = False


def make_driver():
    """Return a configured Chrome webdriver instance (undetected if available)."""
    options_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--window-size=1920,1080",
        "--disable-blink-features=AutomationControlled",
        "--ignore-certificate-errors",
    ]

    # Common options
    if UC_AVAILABLE:
        options = uc.ChromeOptions()
        # NOTE: some versions of Chrome/uc may not fully support headless=new; if issues, remove headless.
        options.add_argument("--headless=new")
        for a in options_args:
            options.add_argument(a)
        # optional: set a realistic user-agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
        # Create undetected driver
        driver = uc.Chrome(options=options)
        return driver
    else:
        # Standard Selenium path (webdriver_manager required)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        for a in options_args:
            options.add_argument(a)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        if WM_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        else:
            # If webdriver_manager not installed, try default PATH chromedriver
            driver = webdriver.Chrome(options=options)
            return driver


def run_kptcl_automation():
    BASE_LOGIN_URL = "https://sis.kptcl.net/SIS/pages/loginSelectionPage.sis"

    username = os.getenv("KPTCL_USERNAME")
    password = os.getenv("KPTCL_PASSWORD")
    if not username or not password:
        print("❌ Missing environment variables KPTCL_USERNAME / KPTCL_PASSWORD.")
        return

    driver = None
    try:
        driver = make_driver()
        print("✅ Browser started.")

        wait = WebDriverWait(driver, 25)

        # Open login selection page
        print("➡️ Opening login page...")
        driver.get(BASE_LOGIN_URL)
        print("Current URL:", driver.current_url)

        # Click the zone (Bagalakote Zone)
        print("➡️ Selecting 'Bagalakote Zone' ...")
        try:
            zone_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[normalize-space()='Bagalakote Zone']"))
            )
            zone_btn.click()
        except Exception:
            zone_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Bagalkote')]"))
            )
            zone_btn.click()
        time.sleep(2)



        # Fill username and password
        print("➡️ Entering credentials ...")
        wait.until(EC.presence_of_element_located((By.ID, "j_username"))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.ID, "j_password"))).send_keys(password)

        # Click Login
        print("➡️ Clicking Login ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']"))).click()
        time.sleep(2)

        # After login — deal with Back / OK dialogs (as in Selenium script)
        try:
            # If a 'Back' button appears
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Back']")),).click()
            time.sleep(1)
            # Click OK if shown
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='OK']"))).click()
            time.sleep(1)
        except Exception:
            # Not critical; continue
            pass

        # Navigate to maintenance tab
        print("➡️ Opening Maintenance tab ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#form:tabview:maintenance']"))).click()
        time.sleep(1)

        # Click the specific button (ID may vary)
        try:
            wait.until(EC.element_to_be_clickable((By.ID, "form:tabview:j_idt95"))).click()
            time.sleep(1)
        except Exception:
            # If ID changed, try clicking by link text or other locator
            print("⚠️ Could not click element by ID form:tabview:j_idt95 — trying alternative locators.")
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'maintenance')]"))).click()
                time.sleep(1)
            except Exception:
                print("⚠️ Alternative maintenance click failed; continuing to next steps.")

        # Click Add
        print("➡️ Clicking Add ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add']"))).click()
        time.sleep(1)

        # Open calendar and pick today's date
        print("➡️ Picking today's date in calendar ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'ui-icon-calendar')]"))).click()
        time.sleep(1)
        today = datetime.now().day
        date_xpath = f"//table[contains(@class,'ui-datepicker-calendar')]//a[text()='{today}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()
        time.sleep(1)

        # Click the checkbox (1st checkbox)
        print("➡️ Checking the checkbox ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class,'ui-chkbox-box')])[1]"))).click()
        time.sleep(1)

        # Click Save
        print("➡️ Saving ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))).click()
        time.sleep(2)

        # Logout
        print("➡️ Logging out ...")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'j_spring_security_logout')]"))).click()
        print("✅ KPTCL SIS automation completed successfully.")

    except Exception as e:
        print("❌ Automation error:", repr(e))
        # Optionally save a screenshot to help debugging (file will be in runner workspace)
        try:
            if driver:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"kptcl_error_{timestamp}.png"
                driver.save_screenshot(fname)
                print(f"📸 Screenshot saved to {fname}")
        except Exception:
            pass
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


if __name__ == "__main__":
    run_kptcl_automation()



