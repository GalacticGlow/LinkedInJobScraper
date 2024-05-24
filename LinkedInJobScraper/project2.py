from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import time

url = 'https://www.linkedin.com/jobs/search?position=1&pageNum=0'

options = webdriver.ChromeOptions()
options.add_argument('start-maximized')
service = Service()
driver = webdriver.Chrome(service=service, options=options)

driver.get(url)

job_name = input('What kind of job are you looking for?')
job_location = input('Where would you like your job to be located?')

while True:
    WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.ID, 'job-search-bar-keywords')))
    job_search_bar = driver.find_element(By.ID, 'job-search-bar-keywords')

    WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.ID, 'job-search-bar-location')))
    job_location_field = driver.find_element(By.ID, 'job-search-bar-location')

    job_location_field.click()
    job_location_field.clear()
    job_location_field.send_keys(job_location)

    job_search_bar.send_keys(job_name)
    job_search_bar.send_keys(Keys.ENTER)

    try:
        no_result_message_xpath = '//h1[contains(@class, "core-section-container__main-title main-title")]'
        if len(driver.find_elements(By.XPATH, no_result_message_xpath)) > 0:
            print("Hmmm, it seems like we couldn't find a match for " + job_name + ". Please check the spelling and try again:")
        else:
            break
    except NoSuchElementException:
        print('Something went wrong')
    
    job_name = input('What kind of job are you looking for?')
    job_location = input('Where would you like your job to be located?')

time.sleep(3)
driver.quit()