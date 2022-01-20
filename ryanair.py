import sys
import os
import platform
import copy
import datetime
from datetime import date, timedelta
import re
from selenium import webdriver
import requests
import pandas as pd
import numpy as np

class RyanairWebdriver():
    #TODO: add Firefox, Safari, Edge webdrivers
    def __init__(self, webdriver_path="/usr/bin/chromedriver"):
        """
        :param str webdriver_path: webdriver path
        """
        self.webdriver_path = webdriver_path
        self.driver = webdriver.Chrome(self.webdriver_path)
        self.driver.implicitly_wait(2)

    #TODO: add WizzAir scrapper
    def open_website(self):
        """Open ryanair website"""
        self.driver.get("https://www.ryanair.com/")
        self.driver.maximize_window()
        cookies_accept = self.driver.find_element_by_xpath(
            '//*[@id="cookie-popup-with-overlay"]/div/div[3]/button[2]'
            )
        cookies_accept.click()

    def get_air_connections(self):
        """Find air connections between specified departure and destination airports"""
        input_departure = self.driver.find_element_by_id('input-button__departure')
        input_departure.click()
        clear_selection = self.driver.find_element_by_xpath('//fsw-airports-list//button')
        clear_selection.click()
        airports = self.driver.find_elements_by_xpath('//fsw-airport-item//span//span')
        airports_list = [airport.text for airport in airports]
        airports_list.sort()
        print("Available airports:", airports_list)
        departure_airports = input("Enter departure airports:")
        departure_airports = "".join(departure_airports.split())
        departure_airports = departure_airports.replace("_", " ")
        departure_airports = departure_airports.split(',')
        destinations_list = []
        air_connections = {}
        selected_connections = {}
        # create list of possible destinations
        for dep_airport in departure_airports:
            input_departure.click()
            clear_selection = self.driver.find_element_by_xpath('//fsw-airports-list//button')
            clear_selection.click()
            input_departure.send_keys(dep_airport)
            departure_airport = self.driver.find_element_by_xpath('//fsw-airport-item')
            departure_airport.click()
            input_destination = self.driver.find_element_by_id('input-button__destination')
            input_destination.click()
            destination_airports = self.driver.find_elements_by_xpath(
                '//fsw-airport-item//span//span[@data-ref="airport-item__name"]' \
                    '[not(contains(@data-id,"ANY"))]'
                )
            air_connections[dep_airport] = [airport.text for airport in destination_airports]
            for airport in destination_airports:
                if airport.text not in destinations_list:
                    destinations_list.append(airport.text)
        destinations_list.sort()            
        print("Available destinations:", destinations_list)
        destinations = input("Enter destination airports:")
        destinations = "".join(destinations.split())
        destinations = destinations.replace("_", " ")
        destinations = destinations.split(',')
        # create all possible connections between departure and destination airports
        for departure in air_connections.keys():
            selected_connections[departure] = list(
                set(air_connections[departure]) & set(destinations)
                )
        final_connections = [
            [key, value] for key in selected_connections.keys()
            for value in selected_connections[key]
            ]
        
        return final_connections

    def get_flights(self, final_connections, main_currency='EUR', return_airport=False):
        """Find air connections between specified departure and destination airports"""
        try:
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
        except Exception as e:
            print("Something went wrong, check input values and try again\n" \
                f"{type(e).__name__}: {e}")
            self.quit_driver()
            sys.exit(1)
        flights_data = {
            "Index" : [],
            "From" : [],
            "To": [],
            "Date" : [],
            "Departure hour" : [],
            "Arrival hour" : [],
            "Trip length" : [],
            "Price" : [],
            "Combined price" : [],
            "Currency" : []
            }
        first_way_flights = copy.deepcopy(flights_data)
        second_way_flights = copy.deepcopy(flights_data)
        flights_dicts = [first_way_flights, second_way_flights]
        # find dates matching to user's preferences
        for idx in range(2):
            for air_connection in final_connections:
                try:
                    modify_date = self.driver.find_element_by_xpath(
                        '//flights-trip-details[@class="ng-tns-c55-3 ng-star-inserted"]' \
                            '//div/div//button'
                            )
                    modify_date.click()
                except:
                    pass
                try:
                    one_way = self.driver.find_element_by_xpath('//fsw-trip-type-button[@data-ref="flight-search-trip-type__one-way-trip"]//button')
                    one_way.click()
                except:
                    pass
                input_departure = self.driver.find_element_by_id('input-button__departure')
                input_departure.click()
                try:
                    clear_selection = self.driver.find_element_by_xpath(
                        '//fsw-airports-list//button'
                        )
                    clear_selection.click()
                except:
                    pass
                if idx == 0:
                    input_departure.send_keys(air_connection[0])
                elif idx == 1:
                    input_departure.send_keys(air_connection[1])
                dep_airports = self.driver.find_elements_by_xpath(
                    '//fsw-airport-item//span//span'
                    )
                for departure_airport in dep_airports:
                    if idx == 0 and (air_connection[0] == departure_airport.text):
                        departure_airport.click()
                        break
                    elif idx == 1 and (air_connection[1] == departure_airport.text):
                        departure_airport.click()
                        break
                input_destination = self.driver.find_element_by_id('input-button__destination')
                input_destination.click()
                try:
                    clear_selection = self.driver.find_element_by_xpath(
                        '//fsw-airports-list//button'
                        )
                    clear_selection.click()
                except:
                    pass
                if idx == 0:
                    input_destination.send_keys(air_connection[1])
                elif idx == 1:
                    input_destination.send_keys(air_connection[0])
                dest_airports = self.driver.find_elements_by_xpath(
                    '//fsw-airport-item//span[@data-ref="airport-item__name"]' \
                        '[not(contains(@data-id,"ANY"))]'
                    )
                for destination_airport in dest_airports:
                    if idx == 0 and (air_connection[1] == destination_airport.text):
                        destination_airport.click()
                        break
                    elif idx == 1 and (air_connection[0] == destination_airport.text):
                        destination_airport.click()
                        break
                months = self.driver.find_elements_by_xpath(
                    '//month-toggle//div//div//div//div//div[contains(@class,"m-toggle__month")]'
                    )
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

                    if len(str(month)) < 2:
                        year_month = str(year) + "-" + "0" + str(month)
                    else:
                        year_month = str(year) + "-" + str(month)
                    years_months.append(year_month)
                # dates format validation
                try:
                    picked_month = left_limit[:-3]
                    picked_month = years_months.index(picked_month)
                    if idx == 0:
                        first_date = datetime.datetime.strptime(left_limit, '%Y-%m-%d').date()
                        last_date = datetime.datetime.strptime(right_limit, '%Y-%m-%d').date()
                    elif idx == 1:
                        first_date = datetime.datetime.strptime(left_limit, '%Y-%m-%d').date() \
                            + timedelta(days=min_days)
                        last_date = datetime.datetime.strptime(right_limit, '%Y-%m-%d').date() \
                            + timedelta(days=max_days)
                except ValueError:
                    print("ValueError: Wrong date format or date has passed")
                    self.quit_driver()
                    sys.exit(1)
                # check whether right date limit is after left date limit
                try:
                    numdays = (last_date - first_date).days
                    if numdays < 0:
                        raise ValueError("Return date is earlier than departure date")
                except ValueError as e:
                    print(e)
                    self.quit_driver()
                    sys.exit(1)
                date_list = [str(first_date + datetime.timedelta(days=day)) for day in range(numdays+1)]
                if picked_month > 8:
                    next_dates =  self.driver.find_element_by_xpath(
                        '//month-toggle//div//div//icon[@iconid="glyphs/chevron-right"]'
                        )
                    for i in range(picked_month - 8):
                        next_dates.click()
                    months[picked_month].click()
                else:
                    months[picked_month].click()
                available_dates = self.driver.find_elements_by_xpath(
                    '//calendar-body//div//div//div[not(contains(@class,"disabled"))]'
                    )
                # check if there are available flights on given dates
                if len(available_dates) > 0:
                    dates_list = [d.get_attribute("data-id") for d in available_dates]
                    departure_dates = list(set(date_list).intersection(dates_list))
                    departure_dates.sort()
                    # fill departure date on website
                    for index, departure_date in enumerate(departure_dates):
                        try:
                            modify_date = self.driver.find_element_by_xpath(
                                '//flights-trip-details[@class="ng-tns-c55-3 ng-star-inserted"]' \
                                    '//div/div//button'
                                    )
                            modify_date.click()
                        except:
                            pass
                        picked_date = dates_list.index(departure_date)
                        dep_date = datetime.datetime.strptime(departure_date, '%Y-%m-%d').date()
                        if index != 0:
                            departure_area = self.driver.find_element_by_xpath(
                                '//fsw-flight-search-widget-controls//div' \
                                    '//fsw-input-button[@uniqueid="dates-from"]'
                                    )
                            departure_area.click()
                        available_dates = self.driver.find_elements_by_xpath(
                            '//calendar-body//div//div//div[not(contains(@class,"disabled"))]'
                            )
                        available_dates[picked_date].click()
                        passengers_picker = self.driver.find_elements_by_class_name(
                            'counter__button-wrapper--enabled'
                            )
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
                        search = self.driver.find_element_by_xpath(
                            '//fsw-flight-search-widget//div//div//div/button'
                            )
                        search.click()
                        # check flights prices
                        departure_prices = self.driver.find_elements_by_xpath(
                            '//flight-card[@data-e2e="flight-card--outbound"]' \
                                '[not(contains(@class,"disabled"))]' \
                                    '//flight-price//span[@data-e2e="flight-card-price"]'
                                    )
                        # check flights hours
                        departure_hours = self.driver.find_elements_by_xpath(
                            '//flight-card[@data-e2e="flight-card--outbound"]' \
                                '[not(contains(@class,"disabled"))]'\
                                    '//flight-info//div//span[@class="h2"]'
                                    )
                        cities = self.driver.find_elements_by_xpath(
                            '//flight-card//flight-info//span[@class="time__city b2"]'
                            )
                        # fill flights dictionary with flight data: dates, prices, flight hours etc.
                        for i in range(int(len(departure_hours) / 2)):
                            try:
                                departure_price = departure_prices[i].text
                                departure_price = list(filter(
                                    None, re.split('(\d*\D+\d+)', departure_price)
                                    ))
                                departure_price = [
                                    x.replace(" ", "") for x in departure_price
                                    ]
                                currency = departure_price[1]
                                departure_price = departure_price[0]
                                departure_price = float(departure_price.replace(',', '.'))
                            # fill with NaNs when tickets are sold out
                            except IndexError:
                                departure_price = np.nan
                                currency = np.nan

                            departure_hour = departure_hours[i*2].text
                            arrival_hour = departure_hours[i*2+1].text
                            departure_city = cities[i*2].text
                            arrival_city = cities[i*2+1].text

                            flights_dicts[idx]["From"].append(departure_city)
                            flights_dicts[idx]["To"].append(arrival_city)
                            flights_dicts[idx]["Date"].append(dep_date)
                            flights_dicts[idx]["Departure hour"].append(departure_hour)
                            flights_dicts[idx]["Arrival hour"].append(arrival_hour)
                            flights_dicts[idx]["Trip length"].append(np.nan)
                            flights_dicts[idx]["Price"].append(departure_price)
                            flights_dicts[idx]["Combined price"].append(np.nan)
                            flights_dicts[idx]["Currency"].append(currency)
                else:
                    pass

        for i in range(len(first_way_flights["From"])):
            for j in range(len(second_way_flights["From"])):
                length_in_days = (second_way_flights["Date"][j] - first_way_flights["Date"][i]).days
                if return_airport:
                    condition = (min_days <= length_in_days <= max_days) and \
                        (first_way_flights["To"][i] == second_way_flights["From"][j]) and \
                            (first_way_flights["From"][i] == second_way_flights["To"][j])
                else:
                    condition = (min_days <= length_in_days <= max_days) and \
                        (first_way_flights["To"][i] == second_way_flights["From"][j])
                if condition:
                    flights_data["From"].append(first_way_flights["From"][i])
                    flights_data["To"].append(first_way_flights["To"][i])
                    flights_data["Date"].append(first_way_flights["Date"][i])
                    flights_data["Departure hour"].append(first_way_flights["Departure hour"][i])
                    flights_data["Arrival hour"].append(first_way_flights["Arrival hour"][i])
                    flights_data["Trip length"].append(length_in_days)
                    flights_data["Price"].append(first_way_flights["Price"][i])
                    flights_data["Combined price"].append(np.inf)
                    flights_data["Currency"].append(first_way_flights["Currency"][i])
                    flights_data["From"].append(second_way_flights["From"][j])
                    flights_data["To"].append(second_way_flights["To"][j])
                    flights_data["Date"].append(second_way_flights["Date"][j])
                    flights_data["Departure hour"].append(second_way_flights["Departure hour"][j])
                    flights_data["Arrival hour"].append(second_way_flights["Arrival hour"][j])
                    flights_data["Trip length"].append(length_in_days)
                    flights_data["Price"].append(second_way_flights["Price"][j])
                    flights_data["Combined price"].append(np.inf)
                    flights_data["Currency"].append(second_way_flights["Currency"][j])
        # check if any flights have beend scrapped 
        try:
            if len(flights_data["From"]) > 0:
                # create pandas DataFrame from dictionary
                indexes = list(range(1, int(len(flights_data["From"]) / 2) + 1)) * 2
                indexes.sort()
                flights_data["Index"] = indexes
                flights_df = pd.DataFrame(flights_data)
                flights_df = flights_df.dropna()
                # convert currencies to main currency
                flights_df["Currency"] = flights_df["Currency"].str.lower()
                currency_dict = {
                    "dkr" : "DKK",
                    "kč" : "CZK",
                    "dhs" : "MAD",
                    "nkr" : "NOK",
                    "zł" : "PLN",
                    "sfr" : "CHF",
                    "kr" : "SEK",
                    "ft" : "HUF",
                    "£" : "GBP",
                    "€" : "EUR"
                    }
                flights_df = flights_df.replace({"Currency" : currency_dict})
                currency_rates = self.get_currency_rates()
                # check if every currency has been mapped to ISO format
                try:
                    flights_df["Price"] = flights_df.apply(
                        lambda row: self.currency_convert(
                            currency_rates,
                            row['Currency'],
                            main_currency,
                            row["Price"]
                            ),
                            axis=1
                        )
                    flights_df["Combined price"] = flights_df.groupby("Index")["Price"].transform('sum')
                    flights_df["Currency"] = main_currency
                except KeyError:
                    print("Unknown currency, keeping original currencies")
                flights_df = flights_df.set_index(
                    ["Index",
                    "Combined price",
                    "Trip length",
                    "From"
                    ]).sort_values(
                        by=["Combined price", "Trip length", "Index"],
                        ascending=[True, False, True]
                        )
            else:
                raise Exception("No available flights on given dates")
        except Exception as e:
            print(e)
            self.quit_driver()
            sys.exit(1)
            
        return flights_df

    def get_currency_rates(self):
        """Scrap current currencies exchange rates"""
        exchangerate_data = requests.get('https://api.exchangerate-api.com/v4/latest/EUR').json()
        rates = exchangerate_data['rates']
        return rates

    def currency_convert(self, rates, from_currency, to_currency, amount):
        """Convert currencies"""
        if from_currency != 'EUR':
            amount = amount / rates[from_currency]
        return round(amount * rates[to_currency], 2)

    def save_as_csv(self, flights_df, path='./flights.csv', open_file=False):
        """Save DataFrame as *.csv file"""
        flights_df.to_csv(path)
        if open_file:
            if platform.system() == 'Linux':
                os.system(f"libreoffice {path}")
            if platform.system() == 'Windows':
                os.system(f"start excel.exe {path}")
            if platform.system() == 'Darwin':
                os.system("")
            else:
                pass

    def save_as_excel(self, flights_df, path='./flights.xlsx', open_file=False):
        """Save DataFrame as *.xlsx file"""
        flights_df.to_excel(path)
        if open_file:
            if platform.system() == 'Linux':
                os.system(f"libreoffice {path}")
            if platform.system() == 'Windows':
                os.system(f"start excel.exe {path}")
            if platform.system() == 'Darwin':
                os.system("")
            else:
                pass

    def quit_driver(self):
        """Quit webdriver"""
        self.driver.quit()
