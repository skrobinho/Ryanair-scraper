from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

PATH = "/usr/bin/chromedriver"
driver = webdriver.Chrome(PATH)

driver.get("https://www.ryanair.com/")
driver.maximize_window()

cookies_accept = driver.find_element_by_xpath('//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]')
cookies_accept.click()

time.sleep(2)

one_way = driver.find_element_by_xpath('//fsw-trip-type-button[@data-ref="flight-search-trip-type__one-way-trip"]//button')
one_way.click()

input_departure = driver.find_element_by_id('input-button__departure')
input_departure.click()

time.sleep(1)

clear_selection = driver.find_element_by_xpath('//fsw-airports-list//button')
clear_selection.click()

airports = driver.find_elements_by_xpath('//fsw-airport-item//span//span')
#airport = driver.find_element_by_xpath('//fsw-airport-item//span//span[@data-id="AAL"]')
#print(airport.text)
airports_list = [airport.text for airport in airports]
departure_airport = input("Enter departure airport:")

input_departure.send_keys(departure_airport)

departure_airport = driver.find_element_by_xpath('//fsw-airport-item')
departure_airport.click()

#airport.click()

#input_destination.send_keys("pary")

time.sleep(5)


driver.quit()