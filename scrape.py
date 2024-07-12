import requests 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Download chrome driver here: https://googlechromelabs.github.io/chrome-for-testing/#stable
#Option to Keep Webpage open
options=Options()
options.add_experimental_option("detach",True)
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#Initialise Chrome Web driver
driver = webdriver.Chrome(options=options)
driver.get("https://www.wateraid.org/uk/get-involved/events")
page = driver.page_source


# Handle cookies message box
accept_cookies= WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
driver.execute_script("arguments[0].click();", accept_cookies)

# Find "Load More" button and scroll to bottom of page and click
button = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[2]/nav/ul/li/a")
#     # button.click()
driver.execute_script("arguments[0].scrollIntoView();", button)
driver.execute_script("arguments[0].click();", button)

# button2 = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[2]/nav/ul/li/a")
#     # button.click()
# driver.execute_script("arguments[0].scrollIntoView();", button2)
# driver.execute_script("arguments[0].click();", button2)

# button = driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div[2]/nav/ul/li/a")
# button = driver.find_element(By.CLASS_NAME, "pager__item").get_attribute('href')
#     # button.click()
# driver.execute_script("arguments[0].scrollIntoView();", button)
# driver.execute_script("arguments[0].click();", button)
    
#---------------------------------------------------------------------------------- scraping
URL = "https://www.wateraid.org/uk/get-involved/events"
# page = requests.get(URL) 
# print(page.content)
# soup = BeautifulSoup(page.content, "html.parser")
soup = BeautifulSoup(page, "html.parser")
# print(soup)

# Find all listings URL
for link in soup.find_all('a', {"class": "node node--type-event node--view-mode-teaser teaser"}):
    print(link.get('href'))


#--------------------------------------------------------------------------------- throwaway code

# Find Containers containing events listing first
# events_box = soup.find("div", {"class": "teaser-collection"})
# print(events_box)

# In each container, obtain list of URLs of all events listing
# for link in soup.find_all('a'):
#     print(link.get('href'))
# links= events_box.find_all('a', {"class": "node node--type-event node--view-mode-teaser teaser"})
# print(links)

# for link in soup.find_all("a", {"class": "teaser__link"}):
#     print(link.get('href'))


# var button=document.querySelector("#main-content > div.landing-page--content.landing-page__content.view.view-get-involved-filter-page.view-id-get_involved_filter_page.view-display-id-page_1.js-view-dom-id-ff0047ac604a9143034a4ddf11a9b18989f94b69852a542640d090bcea4e49c1.control-width > nav > ul > li > a");
# setInterval(function(){ 
#     button.click();}, 1000);

# function getElementByXpath(path) {
#   return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
# };

# var button = getElementByXpath("/html/body/div[1]/div/main/div[2]/nav/ul/li/a");

# setInterval(function(){ 
#     button.click();}, 1000);
