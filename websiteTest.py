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
# service = Service('./chromedriver.exe')
# driver = webdriver.Chrome(service=service,options=options)
driver = webdriver.Chrome(options=options)
driver.get("https://iileesha.github.io/WaterAid")
page = driver.page_source
driver.maximize_window()