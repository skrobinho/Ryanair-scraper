import sys
import os
import platform
import datetime
from datetime import date
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
            [key, value] for key in air_connections.keys()
            for value in air_connections[key]
            ]
        
        return final_connections

    def get_flights(self, air_connections, main_currency):
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
        # find dates matching to user's preferences
        for air_connection in air_connections:
            try:
                modify_date = self.driver.find_element_by_xpath(
                    '//flights-trip-details[@class="ng-tns-c55-3 ng-star-inserted"]' \
                        '//div/div//button'
                        )
                modify_date.click()
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
            input_departure.send_keys(air_connection[0])
            departure_airport = self.driver.find_element_by_xpath('//fsw-airport-item')
            departure_airport.click()
            input_destination = self.driver.find_element_by_id('input-button__destination')
            input_destination.click()
            try:
                clear_selection = self.driver.find_element_by_xpath(
                    '//fsw-airports-list//button'
                    )
                clear_selection.click()
            except:
                pass
            input_destination.send_keys(air_connection[1])
            destination_airport = self.driver.find_element_by_xpath(
                '//fsw-airport-item//span[@data-ref="airport-item__name"]' \
                    '[not(contains(@data-id,"ANY"))]'
                    )
            destination_airport.click()
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
                first_date = datetime.datetime.strptime(left_limit, '%Y-%m-%d').date()
                last_date = datetime.datetime.strptime(right_limit, '%Y-%m-%d').date()
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
                    available_return_dates = self.driver.find_elements_by_xpath(
                        '//calendar-body//div//div//div[not(contains(@class,"disabled"))]'
                        )
                    if len(available_return_dates) > 0:
                        return_dates_list = [d.get_attribute("data-id") for d in available_return_dates]
                        min_return_date = \
                            datetime.datetime.strptime(departure_date, '%Y-%m-%d').date() \
                                + datetime.timedelta(days=(min_days-1))
                        return_dates = [
                            str(min_return_date + datetime.timedelta(days=day))
                            for day in range(max_days-min_days+1)
                            ]
                        return_dates = list(set(return_dates).intersection(return_dates_list))
                        return_dates.sort()
                        # fill return date on website
                        for count, return_date in enumerate(return_dates):
                            try:
                                modify_date = self.driver.find_element_by_xpath(
                                    '//flights-trip-details' \
                                        '[@class="ng-tns-c55-3 ng-star-inserted"]' \
                                            '//div/div//button'
                                            )
                                modify_date.click()
                            except:
                                pass
                            picked_date = return_dates_list.index(return_date)
                            if count != 0:
                                return_area = self.driver.find_element_by_xpath(
                                    '//fsw-flight-search-widget-controls//div' \
                                        '//fsw-input-button[@uniqueid="dates-to"]'
                                        )
                                return_area.click()
                            available_return_dates = self.driver.find_elements_by_xpath(
                                '//calendar-body//div//div' \
                                    '//div[not(contains(@class,"disabled"))]'
                                    )
                            available_return_dates[picked_date].click()
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
                            return_prices = self.driver.find_elements_by_xpath(
                                '//flight-card[@data-e2e="flight-card--inbound"]' \
                                    '[not(contains(@class,"disabled"))]' \
                                        '//flight-price//span[@data-e2e="flight-card-price"]'
                                        )
                            # check flights hours
                            first_way_hours = self.driver.find_elements_by_xpath(
                                '//flight-card[@data-e2e="flight-card--outbound"]' \
                                    '[not(contains(@class,"disabled"))]'\
                                        '//flight-info//div//span[@class="h2"]'
                                        )
                            second_way_hours = self.driver.find_elements_by_xpath(
                                '//flight-card[@data-e2e="flight-card--inbound"]' \
                                    '[not(contains(@class,"disabled"))]' \
                                        '//flight-info//div//span[@class="h2"]'
                                        )
                            # fill flights dictionary with flight data: dates, prices, flight hours etc.
                            for i in range(int(len(first_way_hours) / 2)):
                                for j in range(int(len(second_way_hours) / 2)):
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

                                        return_price = return_prices[j].text
                                        return_price = list(filter(
                                            None, re.split('(\d*\D+\d+)', return_price)
                                            ))
                                        return_price = [
                                            x.replace(" ", "") for x in return_price
                                            ]
                                        return_price = return_price[0]
                                        return_price = float(return_price.replace(',', '.'))

                                        combined_price = departure_price + return_price
                                    # fill with NaNs when tickets are sold out
                                    except IndexError:
                                        departure_price = np.nan
                                        return_price = np.nan
                                        combined_price = np.nan
                                        currency = np.nan

                                    first_way_departure_hour = first_way_hours[i*2].text
                                    first_way_arrival_hour = first_way_hours[i*2+1].text
                                    second_way_departure_hour = second_way_hours[j*2].text
                                    second_way_arrival_hour = second_way_hours[j*2+1].text

                                    length_in_days = (
                                        datetime.datetime.strptime(return_date, '%Y-%m-%d') \
                                             - datetime.datetime.strptime(departure_date, '%Y-%m-%d')
                                             ).days

                                    flights_data["From"].append(air_connection[0])
                                    flights_data["To"].append(air_connection[1])
                                    flights_data["Date"].append(departure_date)
                                    flights_data["Departure hour"].append(first_way_departure_hour)
                                    flights_data["Arrival hour"].append(first_way_arrival_hour)
                                    flights_data["Trip length"].append(length_in_days)
                                    flights_data["Price"].append(departure_price)
                                    flights_data["Combined price"].append(combined_price)
                                    flights_data["Currency"].append(currency)
                                    flights_data["From"].append(air_connection[1])
                                    flights_data["To"].append(air_connection[0])
                                    flights_data["Date"].append(return_date)
                                    flights_data["Departure hour"].append(second_way_departure_hour)
                                    flights_data["Arrival hour"].append(second_way_arrival_hour)
                                    flights_data["Trip length"].append(length_in_days)
                                    flights_data["Price"].append(return_price)
                                    flights_data["Combined price"].append(combined_price)
                                    flights_data["Currency"].append(currency)
                    else:
                        pass
            else:
                pass
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
                    flights_df["Combined price"] = flights_df.apply(
                        lambda row: self.currency_convert(
                            currency_rates,
                            row['Currency'],
                            main_currency,
                            row["Combined price"]
                            ), 
                        axis=1
                        )
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
