from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import csv
import re

# Login to Linkedin
# Open chrome and direct to linkedin login page
driver = webdriver.Chrome("C:\chromedriver_win32\chromedriver.exe")
driver.implicitly_wait(10)
url = 'https://www.linkedin.com/login'
driver.get(url)

# Extract credentital information
credential = open('login_credential.txt')
line = credential.readlines()
username = line[0]
password = line[1]

# Fill out form & login
email_field = driver.find_element(By.ID, 'username')
email_field.send_keys(username)
sleep(1.5)
password_field = driver.find_element(By.NAME, 'session_password')
password_field.send_keys(password)
sleep(1.5)
login_button = driver.find_element(By.XPATH, '//*[@id="organic-div"]/form/div[3]/button')
login_button.click()
sleep(1)

# Search for the profiles
driver.maximize_window()
search_field = driver.find_element(By.XPATH, '//*[@id="global-nav-typeahead"]/input')
search_query = input('What profile do you want to scrape? ')
search_field.send_keys(search_query)
search_field.send_keys(Keys.RETURN)
object_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="People"]')
object_button.click()

# Retrieve all profile url in current page
def GetURL():
    page_source = BeautifulSoup(driver.page_source)
    profiles = page_source.find_all('a', href = re.compile("/in/"))
    all_profile_url = []
    for profile in profiles:
        profile_url = profile['href'][0:profile['href'].find('?')]
        if profile_url not in all_profile_url:
            all_profile_url.append(profile_url)
    return all_profile_url

# Retrieve profile url in multiple pages
def GetURLonPages():
    number_of_page = int(input('Number of page you want to crawl: '))
    profile_urls = []
    for page in range(number_of_page):
        urls_one_page = GetURL()
        profile_urls = profile_urls + urls_one_page
        sleep(1)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        driver.find_element(By.CSS_SELECTOR, '[aria-label="Next"]').click()
        sleep(1)
    return profile_urls

profile_urls = GetURLonPages()
print(profile_urls)

# Write retrieved profile to csv
with open('linkedin-profile.csv', 'w', newline = '', encoding="utf-8") as fhand:
    headers = ['Name', 'Job Title', 'Location', 'URL']
    writer = csv.DictWriter(fhand, delimiter=',', lineterminator='\n', fieldnames=headers)
    writer.writeheader()

    for profile_url in profile_urls:
        driver.get(profile_url)
        page_source = BeautifulSoup(driver.page_source, 'html.parser')
        info_div = page_source.find('div', class_="mt2 relative")
        name = info_div.h1.string.strip()
        title = info_div.find('div', class_="text-body-medium break-words").string.strip()
        location = info_div.find('span', class_="text-body-small inline t-black--light break-words").string.strip()
        print(name, title, location)
        writer.writerow({headers[0]:name, headers[1]:location, headers[2]:title, headers[3]:profile_url})
