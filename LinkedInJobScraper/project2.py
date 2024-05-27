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

#job_name = input('What kind of job are you looking for?')
#job_location = input('Where would you like your job to be located?')

job_name = 'fullstack'
job_location = 'usa'

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

response = requests.get(driver.current_url)
soup = BeautifulSoup(response.text, 'html.parser')

job_names_html = soup.find_all('h3', attrs={'class' : 'base-search-card__title'})
job_companies_html = soup.find_all('a', attrs={'class' : 'hidden-nested-link'})
job_locations_html = soup.find_all('span', attrs={'class' : 'job-search-card__location'})
job_links_html = soup.find_all('a', attrs={'class' : 'base-card__full-link absolute top-0 right-0 bottom-0 left-0 p-0 z-[2]'})

job_names = []
job_companies = []
job_locations = []
job_applicants = []

# Wait for the visibility of the input element using Selenium
job_search_bar_location = WebDriverWait(driver, 5).until(
    ec.visibility_of_element_located((By.ID, 'job-search-bar-location'))
)

# Extract the current value of the input element using Selenium
job_search_bar_cur_val = job_search_bar_location.get_attribute('value')


job_links = driver.find_elements(By.XPATH, "//div[contains(@class, 'base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card')]")

for i in range(10):
    job_names.append(job_names_html[i].text.strip())
    job_companies.append(job_companies_html[i].text.strip())
    if job_locations_html[i].text.strip() == job_search_bar_cur_val:
        job_locations.append('-')
    else:
        job_locations.append(job_locations_html[i].text.strip())
    
    driver.get(job_links_html[i]['href'])
    #WebDriverWait(driver, 3).until(ec.visibility_of_element_located((By.CLASS_NAME, 'num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet')))
    #job_applicants.append(soup.find('span', attrs={'class' : 'num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet'}).text.split(' ')[0])
    #print(driver.find_element(By.CLASS_NAME, 'num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet').text)
    #driver.back()
    
print(job_names)
print(job_companies)
print(job_locations)
print(job_applicants)

time.sleep(5)
driver.quit() 