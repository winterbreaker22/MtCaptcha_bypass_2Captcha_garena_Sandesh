from undetected_chromedriver import Chrome, ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Using undetected-chromedriver
options = ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize Chrome driver with undetected-chromedriver
driver = Chrome(executable_path=ChromeDriverManager().install(), options=options)

try:
    # Navigate to the webpage
    driver.get("https://shop.garena.my/app/100067/idlogin?next=/app/100067/buy/0")
    time.sleep(10)

    # Find the input field by NAME and fill it
    username_input = driver.find_element(By.NAME, "playerId")
    username_input.send_keys("9109146880")
    time.sleep(3)

    # Optionally, click on the submit button after filling the input
    submit_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    submit_button.click()

    # Wait for a moment (optional)
    time.sleep(5)

finally:
    # Close the browser
    driver.quit()
