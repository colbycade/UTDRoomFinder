# Written by Nahum

import os
import time
import certifi
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

load_dotenv(find_dotenv())

# change to your username
user = os.environ.get("mongodb_user")
password = os.environ.get("mongodb_pwd")
connection_string = f"mongodb+srv://{user}:{password}@classroominformation.kbuk2.mongodb.net/?appName=ClassroomInformation"

client = MongoClient(connection_string, tlsCAFile=certifi.where())
database = client['database']
collection = database['2025_Spring']

maximum_wait_time = 10.00
interval_time = 0.50

url = "https://map.concept3d.com/?id=1772#!ce/52264?ct/51161,42147,52285?mc/32.989761,-96.748108?z/19?lvl/2"
driver = webdriver.Chrome()
driver.get(url)
driver.maximize_window()

docs_read = 0

# iterating through every document
for doc in collection.find({}, {"building": 1, "room": 1}).batch_size(10): 
    room_building = doc.get("building")
    room_code = doc.get("room")
    document_id = doc.get("_id")  

    # search for the ith room in the database in the campus map
    search_bar = driver.find_element(By.XPATH, "//input[@id='search-query']")
    # Focus the input field
    search_bar.click()

    # Select everything and delete (cross-platform version)
    search_bar.send_keys(Keys.END)
    search_bar.send_keys(Keys.SHIFT + Keys.HOME)
    search_bar.send_keys(Keys.BACKSPACE)   
    search_bar.send_keys(f"{room_building} {room_code}")
    
    time.sleep(interval_time)
    
    # press the search bar
    WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='search-button']"))).click()

    time.sleep(interval_time)

    # the search results are stored in an unordered list    
    try:
        # Wait for results container to appear
        ul_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='result-scrollwrapper']"))
        )
        li_elements = ul_element.find_elements(By.TAG_NAME, "li")

        # Try to find a matching result
        for li in li_elements:
            if f"{room_building} {room_code}" in li.text:
                li.click()
                break
        else:
            # No matching result in the list
            print(f"No search result match found for {room_building} {room_code}, skipping.")
            continue

    except TimeoutException:
        # Results container never appeared
        print(f"Search timed out for {room_building} {room_code}, skipping.")
        continue

    time.sleep(interval_time)

    # pressing the share button
    WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='share-btn btn']"))).click()

    # getting the direction link
    direction_link = driver.find_element(By.ID, "share-link").get_attribute("value")

    print(f"{docs_read + 1}: {room_building} {room_code} {direction_link}")

    time.sleep(interval_time)

    # add link to mongodb document
    collection.update_one(
        {"_id": document_id},
        {"$set": {"location": direction_link}}
    )

    # exiting share button window
    WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//button[@class='close-btn']"))).click()
    
    time.sleep(interval_time)
    
    # exiting room window
    WebDriverWait(driver, maximum_wait_time).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='close-balloon-details']"))).click()

    docs_read += 1

driver.quit()