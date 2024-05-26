from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import time
from bs4 import BeautifulSoup
import requests

url = 'https://www.linkedin.com/jobs/search?position=1&pageNum=0'

options = webdriver.ChromeOptions()
options.add_argument('start-maximized')
service = Service()
driver = webdriver.Chrome(service=service, options=options)

driver.get(url)

job_not_found_message_xpath = '//h1[contains(@class, "core-section-container__main-title main-title")]'
location_not_found_xpath = '//h2[contains(@class, "authwall-sign-in-form__header-title")]'
job_found = True

yankee_list = ['united states of america', 'us', 'usa', 'america', 'united states']

job_name = input('What kind of job are you looking for?')
job_location = input('Where would you like your job to be located?')

time.sleep(3)

while True:
    WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.ID, 'job-search-bar-keywords')))
    job_search_bar = driver.find_element(By.ID, 'job-search-bar-keywords')

    WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.ID, 'job-search-bar-location')))
    job_location_field = driver.find_element(By.ID, 'job-search-bar-location')

    job_location_field.click()
    job_location_field.clear()
    job_location_field.send_keys(job_location)

    job_search_bar.clear()
    job_search_bar.send_keys(job_name)
    job_search_bar.send_keys(Keys.ENTER)

    if len(driver.find_elements(By.XPATH, job_not_found_message_xpath)) > 0:
        print("Hmmm, it seems like we couldn't find a match for " + job_name + " in " + job_location + ". Please check the spelling and try again:")
        job_found = False
    elif driver.find_element(By.XPATH,'//input[contains(@value, "United States")]').is_displayed() and job_location.lower() not in yankee_list:
        print("Hmmm, it seems like we couldn't find a country called " + job_location + ". Please check the spelling and try again:")
    else:
        break

    if not job_found:
        job_name = input('What kind of job are you looking for?')
    job_location = input('Where would you like your job to be located?')

print('The loop has been broken')

job_card_class = 'base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card'

job_names = []
job_companies = []

response = requests.get(driver.current_url)
soup = BeautifulSoup(response.text, 'html.parser')
job_cards = soup.find_all('div', attrs={'class' : job_card_class})

#for i in range(3):
print(job_cards)

time.sleep(50000)
driver.quit()