import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, sys

def runkptclautomation():

    print("Launching stealth browser...")

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")

    # IMPORTANT: DO NOT USE HEADLESS
    driver = uc.Chrome(options=options)

    try:
        print("Opening KPTCL SIS login page...")
        driver.get("https://sis.kptcl.com/")   # or your correct link

        time.sleep(5)

        print("Page Title:", driver.title)

        if "403" in driver.title.lower():
            print("❌ 403 Forbidden — IP blocked / datacenter blocked")
            return

        if "chromium" in driver.page_source or "BSD-style" in driver.page_source:
            print("❌ Chrome Security Interstitial — SSL/HSTS/WAF block")
            return

        # WAIT FOR LOGIN FORM
        wait = WebDriverWait(driver, 30)
        wait.until(EC.presence_of_element_located((By.ID, "username")))

        print("Login page loaded successfully.")

        # Fill login
        driver.find_element(By.ID, "username").send_keys("YOUR_USER")
        driver.find_element(By.ID, "password").send_keys("YOUR_PASS")
        driver.find_element(By.ID, "login").click()

        print("Logged in successfully.")

    except Exception as e:
        print("Automation error:", e)
        driver.save_screenshot("error.png")
        print("Saved screenshot as error.png")

    finally:
        driver.quit()

if __name__ == "__main__":
    runkptclautomation()
