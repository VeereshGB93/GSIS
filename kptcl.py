from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

def runkptclautomation():
    chrome_options = webdriver.ChromeOptions()

    # Required for GitHub Actions
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--window-size=1920x1080")

    # ❌ DO NOT set binary_location in GitHub Actions
    # chrome_options.binary_location = "/usr/bin/google-chrome"

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 25)

    try:
        print("Opening KPTCL SIS login page...")
        driver.get("https://sis.kptcl.net/SISpages/loginSelectionPage.sis")

        print("Page Title:", driver.title)
        print("Page Source First 500 chars:")
        print(driver.page_source[:500])
    
        # 1. Select zone
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Bagalakote Zone']"))).click()

        # 2. Login
        wait.until(EC.presence_of_element_located((By.ID, "j_username"))).send_keys("aelakamanahalli110")
        wait.until(EC.presence_of_element_located((By.ID, "j_password"))).send_keys("110lhalli")
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']"))).click()

        # 3. Back
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Back']"))).click()

        # 4. OK
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='OK']"))).click()

        # 5. Maintenance tab
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#form:tabview:maintenance']"))).click()

        # 6. Daily maintenance
        wait.until(EC.element_to_be_clickable((By.ID, "form:tabview:j_idt95"))).click()

        # 7. Add
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add']"))).click()

        # 8. Calendar
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'ui-icon-calendar')]"))
        ).click()

        # 9. Select today's date
        today = datetime.now().day
        date_xpath = f"//table[contains(@class,'ui-datepicker-calendar')]//a[text()='{today}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()

        # 10. Select All checkbox
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//div[contains(@class,'ui-chkbox-box')])[1]"))
        ).click()

        # 11. Save
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))).click()

        # 12. Logout
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href,'j_spring_security_logout')]"))
        ).click()

        print("KPTCL SIS automation completed successfully.")

    except Exception as e:
        print("Automation error:", e)
        print("Capturing screenshot...")

        try:
            driver.save_screenshot("error.png")
            print("Saved screenshot as error.png")
        except:
            print("Failed to capture screenshot.")

    finally:
        driver.quit()

if __name__ == "__main__":
    runkptclautomation()

