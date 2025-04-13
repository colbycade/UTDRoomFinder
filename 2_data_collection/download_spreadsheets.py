import os
import time
import glob
import shutil
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def login(driver):

    # login credentials
    username = os.environ.get("username")
    password = os.environ.get("password")

    # pressing login button
    driver.find_element(By.XPATH, "//a[@id='pauth_link']").click()

    # entering credentials
    driver.find_element(By.XPATH, "//input[@id='netid']").send_keys(username)
    time.sleep(1.00)

    driver.find_element(By.XPATH, "//input[@id='password']").send_keys(password)
    time.sleep(1.00)

    # logging in
    driver.find_element(By.XPATH, "//button[@id='login-button']").click()
    
load_dotenv(find_dotenv())

url = "https://coursebook.utdallas.edu/"
service = Service(executable_path = "chromedriver")

driver = webdriver.Chrome(service = service)
driver.get(url)

login(driver)

n = 0
maximum_wait_time = 5.00

while True:
    class_prefix = Select(driver.find_element(By.XPATH, "//select[@id='combobox_cp']"))  # ptr to dropdown menu 
    options = class_prefix.options # list of all elements in dropdown menu

    n += 1
    if n >=len(options):
        print("reached end, quitting")
        break
    
    time.sleep(1.00)
    
    # selecting nth prefix in dropdown menu
    current_prefix = options[n].get_attribute("value")
    class_prefix.select_by_value(current_prefix)
    time.sleep(1.00)

    # pressing "Search Classes" btn
    WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()
        
    # pressing "download excel" btn
    try:
        WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//a[@class='button-link']"))).click()
        time.sleep(1.00)
    except TimeoutException:
        continue

    # downloading excel file
    try:
        WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-controls='c_export']"))).click()
        WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.LINK_TEXT, "Download Excel File"))).click()
        print(f"index {n} was downloaded")
        time.sleep(1.00)
        folder = "raw_classroom_information"
        downloads_path = str(Path.home()/"Downloads")
        spreadsheets = glob.glob(os.path.join(downloads_path, '*.xlsx'))
        if len(spreadsheets) > 0:
            newest_file = max(spreadsheets, key=os.path.getmtime)
            shutil.move(newest_file, folder)
    except TimeoutException:
        driver.back()
        continue

    driver.back()

driver.quit()