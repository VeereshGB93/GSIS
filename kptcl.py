# kptcl.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

BASE_URL = "https://sis.kptcl.net/SIS"

def get_viewstate(html):
    """Extract JSF ViewState token from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    vs = soup.find("input", {"name": "javax.faces.ViewState"})
    return vs["value"] if vs else ""

def run_kptcl_automation():
    session = requests.Session()

    username = os.getenv("KPTCL_USERNAME")
    password = os.getenv("KPTCL_PASSWORD")

    if not username or not password:
        print("❌ Missing environment variables KPTCL_USERNAME or KPTCL_PASSWORD.")
        return

    try:
        # STEP 1: Load login page
        print("➡️ Loading login page...")
        headers = {
                    "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                                    ),
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://sis.kptcl.net/",
                }
        r = session.get(f"{BASE_URL}/pages/loginSelectionPage.sis", headers=headers)
        print("Status:", r.status_code)
        print("Final URL:", r.url)
        print("Response snippet:", r.text[:300])
        if r.status_code != 200:
            print("❌ Failed to load login page.")
            return
        viewstate = get_viewstate(r.text)

        # STEP 2: Select Zone
        print("➡️ Selecting Bagalakote Zone...")
        zone_payload = {
            "form": "form",
            "form:zone_selection_input": "Bagalakote Zone",
            "form:zone_selection_focus": "",
            "form:j_idt20": "form:j_idt20",  # zone select button
            "javax.faces.ViewState": viewstate,
        }
        r = session.post(f"{BASE_URL}/pages/loginSelectionPage.sis", data=zone_payload)
        viewstate = get_viewstate(r.text)

        # STEP 3: Login
        print("➡️ Logging in...")
        login_payload = {
            "j_username": username,
            "j_password": password,
            "login": "Login",
            "javax.faces.ViewState": viewstate,
        }
        r = session.post(f"{BASE_URL}/j_spring_security_check", data=login_payload)
        if "logout" not in r.text.lower():
            print("❌ Login failed — check credentials.")
            return
        print("✅ Logged in successfully.")

        # STEP 4: Access main page
        r = session.get(f"{BASE_URL}/pages/main.sis")
        viewstate = get_viewstate(r.text)

        # STEP 5: Simulate maintenance form submission
        today = datetime.now().strftime("%d-%m-%Y")
        print(f"➡️ Submitting maintenance record for {today}...")

        maintenance_payload = {
            "form": "form",
            "form:tabview:j_idt95": "form:tabview:j_idt95",
            "form:tabview:date_input": today,
            "form:tabview:add_button": "Add",
            "javax.faces.ViewState": viewstate,
        }

        r = session.post(f"{BASE_URL}/pages/main.sis", data=maintenance_payload)
        if r.status_code == 200:
            print("✅ Maintenance form submitted successfully.")
        else:
            print("❌ Maintenance submission failed.")

        # STEP 6: Logout
        print("➡️ Logging out...")
        session.get(f"{BASE_URL}/j_spring_security_logout")
        print("✅ Logged out successfully.")
        print("🎉 KPTCL automation completed successfully (requests-based).")

    except Exception as e:
        print("❌ Automation error:", e)

if __name__ == "__main__":
    run_kptcl_automation()



