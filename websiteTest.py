from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import random

# Notes:
# This web testing script was implemented using the Selenium library
# The approach of using assertions in this script was implemented with reference to: https://www.geeksforgeeks.org/assertion-states-in-selenium/
# Approach used to work with windows in the test was implemented with reference to: https://www.selenium.dev/documentation/webdriver/interactions/windows/


#Download chrome driver here: https://googlechromelabs.github.io/chrome-for-testing/#stable
#Option to Keep Webpage open
options=Options()
options.add_experimental_option("detach",True)
options.add_argument('--ignore-certificate-errors')
options.add_experimental_option('excludeSwitches', ['enable-logging'])


#Initialise Chrome Web driver
driver = webdriver.Chrome(options=options)
driver.get("https://iileesha.github.io/WaterAid")
page = driver.page_source
driver.maximize_window()


## Test 2: Description of `Who We Are' is rendered
intro_component = driver.find_element(By.ID, 'Who-we-are')
try:
    intro_component = driver.find_element(By.ID, 'Who-we-are')

    # Check if the element is displayed
    if intro_component.is_displayed():
        print("Test Case 2 passed: Who We Are description component exists and is visible.")
    else:
        print("Test Case 2 failed: Who We Are description component exists but is not visible.")
except NoSuchElementException:
    # If the element is not found
    print("Test Case 2 failed: Who We Are description component does not exist on the webpage.")


### Test 3: 5 card components explaining what WaterAid does are rendered
time.sleep(5)
for i in range(1,6):
    test_id = 'card' + str(i)
    try:
        card = driver.find_element(By.ID, test_id)

        # Check if the element is displayed
        if card.is_displayed():
            print(f"Test Case 3 passed: {test_id} component exists and is visible.")
        else:
            print(f"Test Case 3 failed: {test_id} component exists but is not visible.")
    except NoSuchElementException:
        # If the element is not found
        print(f"Test Case 3 failed: {test_id} component component does not exist on the webpage.")


### Test 5: Walter chatbot is rendered on screen
try:
    # Wait for the chatbot to load 
    chatbot_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class*="WatsonAssistantChatHost"]'))
    )

    # Check if the chatbot is visible
    if chatbot_element.is_displayed():
        print("Test Case 5 passed: Chatbot is rendered and visible.")
    else:
        print("Test Case 5 failed: Chatbot is present but not visible.")
except (NoSuchElementException, TimeoutException):
    print("Test Case 5 failed: Chatbot is not rendered on the webpage.")


## Test 1: Clicking on `Our Impact' in the navigation tab opens the relevant web page
try:
    expected_url = "https://iileesha.github.io/WaterAid/ourImpact.html"
    # Locate the "Our Impact" navigation tab
    nav_tab = driver.find_element(By.ID, "ourImpact")
        
    # Click the "Our Impact" tab
    nav_tab.click()
        
    # Wait for the page to navigate and verify the URL
    WebDriverWait(driver, 15).until(
        EC.url_to_be(expected_url)
    )
        
    # Verify the URL
    current_url = driver.current_url
    assert current_url == expected_url, f"Expected URL: {expected_url}, but got: {current_url}"
    print(f"Test Case 1 passed: {current_url} matches {expected_url}")

except (NoSuchElementException, TimeoutException, AssertionError) as e:
    print(f"Test Case 1 failed: {e}")


### Test 4: Clicking on any one of the card components opens a relevant web page on the official WaterAid website in a new tab

# Expected URLs for the cards
expected_card_urls = {
    'card1': 'https://www.wateraid.org/uk/what-we-do/water',
    'card2': 'https://www.wateraid.org/uk/what-we-do/toilets',
    'card3': 'https://www.wateraid.org/uk/what-we-do/hygiene',
    'card4': 'https://www.wateraid.org/uk/what-we-do/climate-change',
    'card5': 'https://www.wateraid.org/uk/what-we-do/women-and-girls'
}

num = random.randint(1, 5)
key_name = "card" + str(num)
expected_card_url = expected_card_urls[key_name]

try: 
    # Return to home/index page
    home_tab = driver.find_element(By.ID, "home")
    home_tab.click()

    card = driver.find_element(By.ID, key_name)
    
    # click on card to open the new link
    card.click()
    print(f"clicked into {key_name}")

    # Wait for the new tab to open and switch to it
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    original_window = driver.current_window_handle
    new_window = [window for window in driver.window_handles if window != original_window][0]
    driver.switch_to.window(new_window)

    # wait for new tab to load
    WebDriverWait(driver, 15).until(
        EC.url_to_be(expected_card_url)
    )

    # Handle cookies message box
    accept_cookies= WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='onetrust-accept-btn-handler']")))
    driver.execute_script("arguments[0].click();", accept_cookies)

    # Verify the URL
    current_url = driver.current_url
    assert current_url == expected_card_url, f"Expected URL: {expected_card_url}, but got: {current_url}"
    print(f"Test Case 4 passed: {current_url} matches {expected_card_url}, card{num} opens relevant web page on official site")

except (NoSuchElementException, TimeoutException, AssertionError) as e:
        print(f"Test Case 4 failed: card{num} does not open relevant web page on official site")


# Close the browser
driver.quit()