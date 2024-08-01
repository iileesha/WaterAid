# import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
from datetime import date



# Notes:
# Currently a manual method is used to allow the page to load using (time.sleep(s)), but a better method can be used (WebDriverWait(driver, 20).until(EC.element_to_be_clickable(() to allow for the page to load and to find elements to interact with too.
# This can replace the current implemented method to find and letting the page load of time.sleep(s) and driver.find_element()
# If the program stops working, it could be due to slow connectivity issues, close the window and try again


#Download chrome driver here: https://googlechromelabs.github.io/chrome-for-testing/#stable
#Option to Keep Webpage open
options=Options()
options.add_experimental_option("detach",True)
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#Initialise Chrome Web driver
# service = Service('./chromedriver.exe')
# driver = webdriver.Chrome(service=service,options=options)
driver = webdriver.Chrome(options=options)
driver.get("https://www.wateraid.org/uk/get-involved/events")
page = driver.page_source
driver.maximize_window()

# Handle cookies message box
accept_cookies= WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
driver.execute_script("arguments[0].click();", accept_cookies)

time.sleep(2)
# for COUNTER in range(1, 2):
#     print(COUNTER)
#     if COUNTER == 1:
#         time.sleep(2)
#         driver.execute_script("window.scrollTo(0, 2000)")
#         time.sleep(2)
#         driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/nav/ul/li/a').click()
#     elif COUNTER == 2:
#         time.sleep(5)
#         driver.execute_script("window.scrollBy(0, 750);")
#     else: 
#         time.sleep(5)
#         driver.execute_script("window.scrollBy(0, 900);") #note: scrollby value will differ depending on laptop window size
#         time.sleep(3)
#         driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/nav/ul/li/a').click()
counter = 1
while True:
    try:
        print(counter)
        if counter == 1: 
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/nav/ul/li/a').click()
            counter += 1
        else:
            time.sleep(5)
            driver.execute_script("window.scrollBy(0, 950);") #note: scrollby value will differ depending on laptop window size
            time.sleep(3)
            driver.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/nav/ul/li/a').click()
            counter += 1
    except Exception as e:
        # print(e)
        break
# print("load completed")
time.sleep(2)
        

# Get the page source
page_source = driver.page_source

# Parse the page source with BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

links = []

# Find all div containers for listings
main = soup.findAll('main')
div_main = main[0].find('div', 'landing-page--content')
# print(div_main)
collection_divs = div_main.findAll('div', 'teaser-collection')

# For all div containers, find all <a> elements and extract links from every <a> element
for collection in collection_divs:
    a = collection.findAll('a', href=True)
    for link in a:
        # Extract all href links and append to list
        url = "https://www.wateraid.org/" + link['href']

        # Data Cleaning: 
        if url in links: #prevent duplicates
            continue
        else:
            if url.find("get-involved") != -1: #if 'get-involved' is in url, then continue
                if url.find("plan") == -1 and url.find("guide") == -1 and url.find("alexa") == -1: #if 'plan' or 'guide is not in url, then continue
                    if url.find("shop") == -1: #if 'shop' is not in url, then continue
                        if url.find("event-resources") == -1:
                            links.append(url) 
            else:
                continue

# second measure to prevent duplicates
links = list(set(links))

# Write links list to csv
filename = "Listing Links (" + str(date.today()) + ").csv"

with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    for link in links:
        writer.writerow([link])

# print(links)
# print(len(links))

