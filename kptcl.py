from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options   # ✅ This is required
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import os, time
import logging
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


def run_kptcl_automation():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Use new headless mode (Chrome 109+)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://sis.kptcl.net/SIS/pages/loginSelectionPage.sis")

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Bagalakote Zone']"))).click()
        time.sleep(2)

        username = os.getenv("KPTCL_USERNAME")
        password = os.getenv("KPTCL_PASSWORD")

        wait.until(EC.presence_of_element_located((By.ID, "j_username"))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.ID, "j_password"))).send_keys(password)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']"))).click()
        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Back']"))).click()
        time.sleep(1)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='OK']"))).click()
        time.sleep(1)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#form:tabview:maintenance']"))).click()
        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.ID, "form:tabview:j_idt95"))).click()
        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add']"))).click()
        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(@class,'ui-icon-calendar')]"))).click()
        time.sleep(1)

        today = datetime.now().day
        date_xpath = f"//table[contains(@class,'ui-datepicker-calendar')]//a[text()='{today}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()
        time.sleep(1)

        wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[contains(@class,'ui-chkbox-box')])[1]"))).click()
        time.sleep(2)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))).click()
        time.sleep(3)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'j_spring_security_logout')]"))).click()
        print("✅ KPTCL SIS automation completed successfully.")

    except Exception as e:
        print("❌ Automation error:", e)

    finally:
        time.sleep(3)
        driver.quit()

if __name__ == "__main__":
    run_kptcl_automation()





