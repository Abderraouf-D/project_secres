from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import os, datetime

URL = "http://127.0.0.1/login"

def admin_bot(link, test=False):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-web-security')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    client = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    if test:
        client.get(link)
        print("Link checked...")
        return
        
    client.get(URL)
    WebDriverWait(client, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "login-form"))
    )

    # # set FLAG cookie on http://127.0.0.1/
    # client.add_cookie({'name': 'FLAG', 'value': os.environ.get('FLAG', ''), 'path': '/', 'domain': '127.0.0.1'})


    # Fill out the form
    client.find_element(By.ID, "username").send_keys("admin")
    client.find_element(By.ID, "password").send_keys(os.environ.get('ADMIN_PASSWORD', ''))
    client.find_element(By.CLASS_NAME, "btn").click()
    sleep(1)

    client.get(link)
    print("Link checked...")
    sleep(2)
    client.quit()

if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2:
        print("Usage: python bot.py <link>")
        exit(1)
    link = argv[1]
    admin_bot(link)