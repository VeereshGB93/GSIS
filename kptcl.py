from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

def runkptclautomation():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    chrome_options.binary_location = "/usr/bin/google-chrome"
    driver = webdriver.Chrome(options=chrome_options)

    wait = WebDriverWait(driver, 20)
    try:
        driver.get("https://sis.kptcl.net/SISpages/loginSelectionPage.sis")
        # TITLE 1. Open login selection page...
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Bagalakote Zone']"))).click()
        time.sleep(2)
        # TITLE 2. Click Bagalakote Zone...
        wait.until(EC.presence_of_element_located((By.ID, "j_username"))).send_keys("aelakamanahalli110")
        wait.until(EC.presence_of_element_located((By.ID, "j_password"))).send_keys("110lhalli")
        # TITLE 3. Enter login credentials...
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Login']"))).click()
        time.sleep(2)
        # Continue with your other steps as in your original script...
        # 5. Click "Back"
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Back']"))).click()
        time.sleep(1)

        # 6. Click "OK"
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='OK']"))).click()
        time.sleep(1)

        # 7. Click "Maintenance" tab
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@href='#form:tabview:maintenance']"))).click()
        time.sleep(2)

        # 8. Click "Daily maintenance work(s)"
        wait.until(EC.element_to_be_clickable((By.ID, "form:tabview:j_idt95"))).click()
        time.sleep(2)

        # 9. Click "Add"
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Add']"))).click()
        time.sleep(2)

        # 10. Click calendar icon
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class,'ui-icon-calendar')]"))).click()
        time.sleep(1)

        # 11. Select today's date
        today = datetime.now().day
        date_xpath = f"//table[contains(@class,'ui-datepicker-calendar')]//a[text()='{today}']"
        wait.until(EC.element_to_be_clickable((By.XPATH, date_xpath))).click()
        time.sleep(1)

        # 12. Click "Select All" checkbox
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "(//div[contains(@class,'ui-chkbox-box')])[1]"))).click()
        time.sleep(2)

        # 14. Click "Save"
        wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Save']"))).click()
        time.sleep(3)

        # 15. Logout
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@href,'j_spring_security_logout')]"))).click()

        print("KPTCL SIS automation completed successfully.")

    except Exception as e:
        print("Automation error:", e)

    finally:
        time.sleep(5)
        driver.quit()

if __name__ == '__main__':
    runkptclautomation()

