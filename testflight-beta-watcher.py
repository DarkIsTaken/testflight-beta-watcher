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
    except Exception as e:
        print(f"Error loading apps from JSON file: {str(e)}")
        return {}

apps_file_path = "apps.json"
apps = load_apps_from_json(apps_file_path)

api_token = os.getenv("PUSHOVER_API_TOKEN")
user_key = os.getenv("PUSHOVER_USER_KEY")
tmpfile = os.path.join(os.getcwd(), "testflight-beta-watcher.log")

def check_beta():
    for app, code in apps.items():
        print(f"\nChecking: {app}")
        
        try:
            resp = requests.get(f"https://testflight.apple.com/join/{code}", timeout=10)
            print(f"Status: {resp.status_code}")
            
            if resp.ok:
                if "Join the Beta" in resp.text:
                    send_push_alert(app, code, "https://testflight.apple.com/join/")
                    write_log(f"✅ Found ✅: {app}, https://testflight.apple.com/join/{code}")
                else:
                    write_log(f"⛔️ Unavailable ⛔️: {app}")
            else:
                write_log(f"⛔️ Error ⛔️: {app} - Status code: {resp.status_code}")
                
        except requests.exceptions.RequestException as e:
            write_log(f"❗ Error ❗: {app} - {str(e)}")
            print(f"Error checking {app}: {str(e)}")

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
        print(f"{datetime.now(pytz.timezone('Europe/Istanbul')).strftime('%Y-%m-%d %H:%M:%S')} -- ✅ Found ✅: {app}, {url + code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending push alert for {app}: {str(e)}")
        write_log(f"❗ Error sending push alert for {app}: {str(e)}")

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
