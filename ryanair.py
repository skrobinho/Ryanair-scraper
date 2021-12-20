from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import datetime
from datetime import date
import time

class Ryanair_webdriver():
    #TODO: add Firefox, Safari, Edge webdrivers
    def __init__(self, WEBDRIVER_PATH="/usr/bin/chromedriver"):
        self.WEBDRIVER_PATH = WEBDRIVER_PATH
        self.driver = webdriver.Chrome(self.WEBDRIVER_PATH)
        self.driver.implicitly_wait(2)
        pass

    def open_website(self):
        self.driver.get("https://www.ryanair.com/")
        self.driver.maximize_window()
        cookies_accept = self.driver.find_element_by_xpath('//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]')
        cookies_accept.click()

    def get_air_connections(self):
        input_departure = self.driver.find_element_by_id('input-button__departure')
        input_departure.click()
        clear_selection = self.driver.find_element_by_xpath('//fsw-airports-list//button')
        clear_selection.click()
        airports = self.driver.find_elements_by_xpath('//fsw-airport-item//span//span')
        airports_list = [airport.text for airport in airports]
        print("Available airports:", airports_list)
        departure_airports = input("Enter departure airports:")
        departure_airports = "".join(departure_airports.split())
        departure_airports = departure_airports.replace("_", " ")
        departure_airports = departure_airports.split(',')
        destinations_list = []
        air_connections = {}
        for dep_airport in departure_airports:
            input_departure.click()
            clear_selection = self.driver.find_element_by_xpath('//fsw-airports-list//button')
            clear_selection.click()
            input_departure.send_keys(dep_airport)
            departure_airport = self.driver.find_element_by_xpath('//fsw-airport-item')
            departure_airport.click()
            input_destination = self.driver.find_element_by_id('input-button__destination')
            input_destination.click()
            destination_airports = self.driver.find_elements_by_xpath('//fsw-airport-item//span//span[@data-ref="airport-item__name"][not(contains(@data-id,"ANY"))]')
            air_connections[dep_airport] = [airport.text for airport in destination_airports]
            for airport in destination_airports:
                if airport.text not in destinations_list:
                    destinations_list.append(airport.text)
        print("Available destinations:", destinations_list)
        destinations = input("Enter destination airports:")
        destinations = "".join(destinations.split())
        destinations = destinations.replace("_", " ")
        destinations = destinations.split(',')
        for departure in air_connections.keys():
            air_connections[departure] = list(set(air_connections[departure]) & set(destinations))
        air_connections = [[key, value] for key in air_connections.keys() for value in air_connections[key]]
        
        return air_connections

    def get_flights(self, air_connections):
        left_limit = input("Specify left limit (YYYY-MM-DD):")
        right_limit = input("Specify right limit (YYYY-MM-DD):")
        min_days = input("Specify minimum nubmer of days:")
        min_days = int(min_days)
        max_days = input("Specify maximum number of days:")
        max_days = int(max_days)
        adults = input("Number of adults (min. 1):")
        adults = int(adults)
        teens = input("Number of teenagers:")
        teens = int(teens)
        kids = input("Number of kids:")
        kids = int(kids)
        toddlers = input("Number of toddlers:")
        toddlers = int(toddlers)
        flight_data = {"Index" : [], "From" : [], "To": [], "Date" : [], "Departure hour" : [], "Arrival hour" : [], "Price" : [], "Combined price" : [], "Currency" : []}
        for air_connection in air_connections:
            try:
                modify_date = self.driver.find_element_by_xpath('//flights-trip-details[@class="ng-tns-c55-3 ng-star-inserted"]//div/div//button')
                modify_date.click()
            except:
                pass
            input_departure = self.driver.find_element_by_id('input-button__departure')
            input_departure.click()
            try:
                clear_selection = self.driver.find_element_by_xpath('//fsw-airports-list//button')
                clear_selection.click()
            except:
                pass
            input_departure.send_keys(air_connection[0])
            departure_airport = self.driver.find_element_by_xpath('//fsw-airport-item')
            departure_airport.click()
            input_destination = self.driver.find_element_by_id('input-button__destination')
            input_destination.click()
            try:
                clear_selection = self.driver.find_element_by_xpath('//fsw-airports-list//button')
                clear_selection.click()
            except:
                pass
            input_destination.send_keys(air_connection[1])
            destination_airport = self.driver.find_element_by_xpath('//fsw-airport-item//span[@data-ref="airport-item__name"][not(contains(@data-id,"ANY"))]')
            destination_airport.click()
            months = self.driver.find_elements_by_xpath('//month-toggle//div//div//div//div//div[contains(@class,"m-toggle__month")]')
            year = date.today().year
            month = date.today().month
            years_months = []
            if len(str(month)) < 2:
                year_month = str(year) + "-" + "0" + str(month)
            else:
                year_month = str(year) + "-" + str(month)  
            years_months.append(year_month)
            for _ in range(11):
                if month == 12:
                    month = 1
                    year = year + 1
                else:
                    month = month + 1
                    year = year

                if len(str(month)) < 2:
                    year_month = str(year) + "-" + "0" + str(month)
                else:
                    year_month = str(year) + "-" + str(month)
                years_months.append(year_month)
            picked_month = left_limit[:-3]
            picked_month = years_months.index(picked_month)
            first_date = datetime.datetime.strptime(left_limit, '%Y-%m-%d').date()
            last_date = datetime.datetime.strptime(right_limit, '%Y-%m-%d').date()
            numdays = (last_date - first_date).days
            date_list = [str(first_date + datetime.timedelta(days=day)) for day in range(numdays+1)]
            if picked_month > 8:
                next_dates =  self.driver.find_element_by_xpath('//month-toggle//div//div//icon[@iconid="glyphs/chevron-right"]')
                for i in range(picked_month - 8):
                    next_dates.click()
                months[picked_month].click()
            else:
                months[picked_month].click()
            available_dates = self.driver.find_elements_by_xpath('//calendar-body//div//div//div[not(contains(@class,"disabled"))]')
            dates_list = [d.get_attribute("data-id") for d in available_dates]
            departure_dates = list(set(date_list).intersection(dates_list))
            departure_dates.sort()
            for index, departure_date in enumerate(departure_dates):
                try:
                    modify_date = self.driver.find_element_by_xpath('//flights-trip-details[@class="ng-tns-c55-3 ng-star-inserted"]//div/div//button')
                    modify_date.click()
                except:
                    pass
                picked_date = dates_list.index(departure_date)
                if index != 0:
                    departure_area = self.driver.find_element_by_xpath('//fsw-flight-search-widget-controls//div//fsw-input-button[@uniqueid="dates-from"]')
                    departure_area.click()
                available_dates = self.driver.find_elements_by_xpath('//calendar-body//div//div//div[not(contains(@class,"disabled"))]')
                available_dates[picked_date].click()
                available_return_dates = self.driver.find_elements_by_xpath('//calendar-body//div//div//div[not(contains(@class,"disabled"))]')
                return_dates_list = [d.get_attribute("data-id") for d in available_return_dates]
                min_return_date = datetime.datetime.strptime(departure_date, '%Y-%m-%d').date() + datetime.timedelta(days=(min_days-1))
                return_dates = [str(min_return_date + datetime.timedelta(days=day)) for day in range(max_days-min_days+1)]
                return_dates = list(set(return_dates).intersection(return_dates_list))
                return_dates.sort()
                for count, return_date in enumerate(return_dates):
                    try:
                        modify_date = self.driver.find_element_by_xpath('//flights-trip-details[@class="ng-tns-c55-3 ng-star-inserted"]//div/div//button')
                        modify_date.click()
                    except:
                        pass
                    picked_date = return_dates_list.index(return_date)
                    if count != 0:
                        return_area = self.driver.find_element_by_xpath('//fsw-flight-search-widget-controls//div//fsw-input-button[@uniqueid="dates-to"]')
                        return_area.click()
                    available_return_dates = self.driver.find_elements_by_xpath('//calendar-body//div//div//div[not(contains(@class,"disabled"))]')
                    available_return_dates[picked_date].click()
                    passengers_picker = self.driver.find_elements_by_class_name('counter__button-wrapper--enabled')
                    if adults > 1:
                        for i in range(adults-1):
                            passengers_picker[0].click()
                    else:
                        pass
                    if teens > 0:
                        for i in range(teens):
                            passengers_picker[1].click()
                    if kids > 0:
                        for i in range(kids):
                            passengers_picker[2].click()
                    if toddlers > 0:
                        for i in range(toddlers):
                            passengers_picker[3].click()
                    search = self.driver.find_element_by_xpath('//fsw-flight-search-widget//div//div//div/button')
                    search.click()
                    prices = self.driver.find_elements_by_xpath('//ry-price//span')
                    departure_price = ''
                    for i in range(1,4):
                        departure_price += prices[i].text
                    return_price = ''
                    for i in range(5,8):
                        return_price += prices[i].text
                    departure_price = float(departure_price.replace(',', '.'))
                    return_price = float(return_price.replace(',', '.'))
                    combined_price = departure_price + return_price
                    currency = prices[0].text

                    hours = self.driver.find_elements_by_xpath('//flight-info//div//span[@class="h2"]')
                    first_way_departure_hour = hours[0].text
                    first_way_arrival_hour = hours[1].text
                    second_way_departure_hour = hours[2].text
                    second_way_arrival_hour = hours[3].text
                    
                    flight_data["From"].append(air_connection[0])
                    flight_data["To"].append(air_connection[1])
                    flight_data["Date"].append(departure_date)
                    flight_data["Departure hour"].append(first_way_departure_hour)
                    flight_data["Arrival hour"].append(first_way_arrival_hour)
                    flight_data["Price"].append(departure_price)
                    flight_data["Combined price"].append(combined_price)
                    flight_data["Currency"].append(currency)

                    flight_data["From"].append(air_connection[1])
                    flight_data["To"].append(air_connection[0])
                    flight_data["Date"].append(return_date)
                    flight_data["Departure hour"].append(second_way_departure_hour)
                    flight_data["Arrival hour"].append(second_way_arrival_hour)
                    flight_data["Price"].append(return_price)
                    flight_data["Combined price"].append(combined_price)
                    flight_data["Currency"].append(currency)
        indexes = list(range(1, int(len(flight_data["From"]) / 2) + 1)) * 2
        indexes.sort()
        flight_data["Index"] = indexes

        return flight_data

    def quit_driver(self):
        self.driver.quit()
