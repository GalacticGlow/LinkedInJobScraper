from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests
import os
import csv
import pandas as pd

url = 'https://www.linkedin.com/jobs/search?position=1&pageNum=0'

options = webdriver.ChromeOptions()
options.add_argument('start-maximized')
options.add_argument('--log-level=1')
service = Service()
driver = webdriver.Chrome(service=service, options=options)

actions = ActionChains(driver)

driver.get(url)

job_not_found_message_xpath = '//h1[contains(@class, "core-section-container__main-title main-title")]'
location_not_found_xpath = '//h2[contains(@class, "authwall-sign-in-form__header-title")]'

yankee_list = ['united states of america', 'us', 'usa', 'america', 'united states']

driver.minimize_window()

job_name = input('What kind of job are you looking for?')
job_location = input('Where would you prefer your job to be located?')

driver.maximize_window()

search_query_proper = False

while not search_query_proper:
    driver.maximize_window()
    WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.ID, 'job-search-bar-keywords')))
    job_search_bar = driver.find_element(By.ID, 'job-search-bar-keywords')

    WebDriverWait(driver, 30).until(ec.visibility_of_element_located((By.ID, 'job-search-bar-location')))
    job_location_field = driver.find_element(By.ID, 'job-search-bar-location')

    job_location_field.click()
    job_location_field.clear()
    job_search_bar.clear()

    job_location_field.send_keys(job_location)

    job_search_bar.send_keys(job_name)
    job_search_bar.send_keys(Keys.ENTER)

    if (len(driver.find_elements(By.XPATH, job_not_found_message_xpath)) > 0 or 
        (driver.find_element(By.ID,'job-search-bar-location').get_attribute('value') == 'United States' and job_location.lower() not in yankee_list)):
        print('Either the job name or location are incorrect. Please check your spelling and try again:')
    else:
        search_query_proper = True

    if not search_query_proper:    
        driver.minimize_window()
        job_name = input('What kind of job are you looking for?')
        job_location = input('Where would you like your job to be located?')

driver.minimize_window()

is_a_proper_number = False
while not is_a_proper_number:
    num_jobs = input('How many search results do you need?')
    try:
        num_jobs = int(num_jobs)
        if num_jobs > 0:
            is_a_proper_number = True
    except ValueError:
        print('Enter a number please:')

response = requests.get(driver.current_url)
soup = BeautifulSoup(response.text, 'html.parser')

job_names_html = soup.find_all('h3', attrs={'class' : 'base-search-card__title'})
job_companies_html = soup.find_all('a', attrs={'class' : 'hidden-nested-link'})
job_locations_html = soup.find_all('span', attrs={'class' : 'job-search-card__location'})
job_links_html = soup.find_all('a', attrs={'class' : 'base-card__full-link'})

job_names = []
job_companies = []
job_locations = []
job_applicants = []
job_salaries = []

job_search_bar_location = WebDriverWait(driver, 5).until(
    ec.presence_of_element_located((By.ID, 'job-search-bar-location'))
)

job_search_bar_cur_val = job_search_bar_location.get_attribute('value')

job_links = driver.find_elements(By.XPATH, "//div[contains(@class, 'base-card relative')]")

actual_job_count = driver.find_element(By.CLASS_NAME, 'results-context-header__job-count').text
try:
    actual_job_count = int(actual_job_count)
except ValueError:
    actual_job_count = int(actual_job_count.replace('+', ''))

for i, job_link in enumerate(job_links_html):
    if i + 1 <= actual_job_count:
        job_names.append(job_names_html[i].text.strip())
        job_companies.append(job_companies_html[i].text.strip())
        if job_locations_html[i].text.strip() == job_search_bar_cur_val:
            job_locations.append('-')
        else:
            job_locations.append(job_locations_html[i].text.strip())
        
        url_to_visit = job_link['href']
        job_response = requests.get(url_to_visit)
        job_soup = BeautifulSoup(job_response.text, 'html.parser')

        applicants_version_1 = job_soup.find('span', attrs={'class' : 'num-applicants__caption'})
        applicants_version_2 = job_soup.find('figcaption', attrs={'class' : 'num-applicants__caption'})

        if applicants_version_1:
            job_applicants.append(applicants_version_1.text.strip())
        elif applicants_version_2:
            job_applicants.append(applicants_version_2.text.strip())
        else:
            job_applicants.append('-')

        salary_html = job_soup.find('div', attrs={'class' : 'salary compensation__salary'})
        if salary_html:
            job_salaries.append(salary_html.text.strip())
        else:
            job_salaries.append('-')

        if (i+1)%20 == 0:
            for _ in range(5):
                actions.send_keys(Keys.ARROW_DOWN).perform()
    else:
        print(f'You asked for {num_jobs} jobs, however we unfortunately could only find {i}.')
        break

for i in range(len(job_applicants)):
    job_applicants[i] = job_applicants[i].replace('applicants', '')

driver.minimize_window()

dir_exists = False

while not dir_exists:
    chosen_dir = input('Enter the path to the folder where you would like your file saved:')
    try:
        os.chdir(chosen_dir)
        dir_exists = True
    except OSError:
        print("The folder you chose doesn't exist or is incorrectly typed. Check if you typed the path correctly and try again:")

numeration_column_list = [i+1 for i in range(len(job_names))]

df = pd.DataFrame({
    '№': range(1, len(job_names) + 1),
    'Full position name': job_names,
    'Company': job_companies,
    'Location': job_locations,
    'Number of applicants': job_applicants,
    'Salary': job_salaries
})

df.to_csv('Found LinkedIn jobs.csv', index=False, encoding='utf-8-sig')
print('File successfully saved!!')

driver.quit()