# 0 - import library for the project 
import os, random, sys, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from time import sleep
import requests
import csv
print('- Finish importing package ...')

# 1 - login

#Open Chrome and login Linkedin login site
driver = webdriver.Chrome("/usr/local/bin/chromedriver")
url = 'https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
driver.get(url)
print('- Finish opening a driver ...')

#Entering user name and password to login
login_credential = open('credentials.txt')
line = login_credential.readlines()
username = line[0]
password = line[1]
print('- Finish importing the login credentials ...')

elementID = driver.find_element_by_id('username')
elementID.send_keys(username)
sleep(3)

print('- Keying in the username ...')

elementID = driver.find_element_by_name('session_password')
elementID.send_keys(password)
sleep(3)

print('- Keying in the password ...')

#Click login button access Linkedin
#log_in_button = driver.find_element_by_class_name("btn__primary--large").click()
elementID.submit()
print('- Finish logging in ...')

# 2 - search 

#Click to search bar and input the search query
search = driver.find_element_by_class_name("search-global-typeahead__input") #Define id by using inspect location

#search_button = driver.find_element_by_id("global-nav-typeahead").click() #Click to search bar
key_word = input("What profile do you want to scrape? ")
search.send_keys(key_word)
search.send_keys(Keys.RETURN)
print('- Finish searching ...')

# 3 - scrape URLs

# scrape page 1 URL 
visited_profiles = []
def get_new_profile_ID(soup, search_result):
    profile_ID = []
    pav = soup.find('div', {'class':'neptune-grid two-column'})
    #print(pav)
    all_links = pav.findAll('a',{'class': 'search-result__result-link ember-view'})
    #print(all_links)
    for link in all_links:
        user_ID = link.get('href')
        if user_ID not in search_result and user_ID not in visited_profiles and user_ID not in profile_ID:
            profile_ID.append(user_ID)
    return profile_ID

# loop through all the pages --> scrape all URLs
def get_new_profile_ID_for_multiple_pages():
    input_page = int(input('How many pages you want to scrape: '))
    all_result = []
    search_result = []
    page = 0
    for page in range(input_page):
        search_result = get_new_profile_ID(BeautifulSoup(driver.page_source), search_result)
        sleep(2)
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);') #scroll to the end of the page
        sleep(3)
        next_button = driver.find_element_by_class_name('artdeco-pagination__button--next')
        driver.execute_script("arguments[0].click();", next_button)
        all_result = all_result + search_result
        page = page + 1
        # print('page: ', page, all_result)
        sleep(2)
    return all_result

profile_ID = get_new_profile_ID_for_multiple_pages()
#print(profile_ID)

# 4 - write function to scrape the content and store the data in csv file

for visiting_ID in profile_ID:
    full_link = "https://www.linkedin.com/" + visiting_ID
    visited_profiles.append(full_link)

with open('output.csv', 'w',  newline = '') as file_output:
    headers = ['Name', 'Job Title', 'Location', 'URL']
    writer = csv.DictWriter(file_output, delimiter=',', lineterminator='\n',fieldnames=headers)
    writer.writeheader()
    for linkedin_profile in visited_profiles:
        driver.get(linkedin_profile)
        print('- Accessing profile: ', linkedin_profile)

        last_height = driver.execute_script('return document.body.scrollHeight')

        for i in range(3):
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(5)
            new_height = driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height == new_height

        print('- Start scraping the data ...')

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "html.parser")

        name_div = soup.find('div',{'class':'flex-1 mr5'})
        name_loc = name_div.find_all('ul')
        name = name_loc[0].find('li').get_text().strip() #Remove unnecessary characters 
        print('--- Profile name is: ', name)
        loc = name_loc[1].find('li').get_text().strip() #Remove unnecessary characters 
        print('--- Profile location is: ', loc)
        profile_title = name_div.find('h2').get_text().strip()
        print('--- Profile title is: ', profile_title)
        writer.writerow({headers[0]:name, headers[1]:loc, headers[2]:profile_title, headers[3]:linkedin_profile})