import os
import json
from datetime import datetime
import pytz
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def load_apps_from_json(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}

apps_file_path = "apps.json"
apps = load_apps_from_json(apps_file_path)

api_token = os.getenv("PUSHOVER_API_TOKEN")
user_key = os.getenv("PUSHOVER_USER_KEY")
tmpfile = os.path.join(os.getcwd(), "testflight-beta-watcher.log")

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36"
}

def check_beta():
    for app, code in apps.items():
        print(f"\nChecking: {app}")
        
        try:
            resp = requests.get(f"https://testflight.apple.com/join/{code}", headers=headers, timeout=10)
            print(f"Status: {resp.status_code}")
            
            if resp.ok:
                if "Join the Beta" in resp.text:
                    send_push_alert(app, code, "https://testflight.apple.com/join/")
                    print(f"✅ Found ✅: {app} - {code} - Beta is available!")
                    write_log(f"✅ Found ✅: {app} - {code} - Beta is available!")
                elif "To join the" in resp.text:
                    send_push_alert(app, code, "https://testflight.apple.com/join/")
                    print(f"✅ Found ✅: {app} - {code} - Beta is available!")
                    write_log(f"✅ Found ✅: {app} - {code} - Beta is available!")
                elif "This beta isn't accepting any new testers right now." in resp.text:
                    print(f"⛔️ Unavailable ⛔️: {app} - {code} - This beta isn't accepting new testers.")
                    write_log(f"⛔️ Unavailable ⛔️: {app} - {code} - This beta isn't accepting new testers.")
                elif "This beta is full." in resp.text:
                    print(f"⛔️ Unavailable ⛔️: {app} - {code} - Beta is full.")
                    write_log(f"⛔️ Unavailable ⛔️: {app} - {code} - Beta is full.")
                elif "Not Found" in resp.text:
                    print(f"❗ Error ❗: {app} - {code} - TestFlight page not found.")
                    write_log(f"❗ Error ❗: {app} - {code} - TestFlight page not found.")
                else:
                    print(f"⛔️ Error ⛔️: {app} - {code} - Unexpected response.")
                    write_log(f"⛔️ Error ⛔️: {app} - {code} - Unexpected response.")
            else:
                print(f"⛔️ Error ⛔️: {app} - {code} - Status code: {resp.status_code}")
                write_log(f"⛔️ Error ⛔️: {app} - {code} - Status code: {resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❗ Error ❗: {app} - {code} - {str(e)}")
            write_log(f"❗ Error ❗: {app} - {code} - {str(e)}")

def send_push_alert(app, code, url):
    if not api_token or not user_key:
        print("⛔ Pushover API token or user key is missing! ⛔")
        return
    
    try:
        response = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": api_token,
                "user": user_key,
                "message": f"✅ {app} Beta is available! ✅\n{url + code}",
            },
        )
        response.raise_for_status()
        print(f"{datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%Y-%m-%d %H:%M:%S')} -- ✅ Found ✅: {app} - {url + code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending push alert for {app} - {code}: {str(e)}")
        write_log(f"❗ Error sending push alert for {app} - {code}: {str(e)}")

def write_log(message):
    time24hr = datetime.now(pytz.timezone("Europe/Istanbul")).strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(tmpfile, "a", encoding="utf-8") as log_file:
            log_file.write(f"{time24hr} -- {message}\n")
    except Exception as e:
        print(f"Error writing to log file: {str(e)}")

if __name__ == '__main__':
    while True:
        check_beta()
        print(f"\n😴 Sleeping for 30 minutes...\n")
        time.sleep(1800)
