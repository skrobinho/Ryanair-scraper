# Flights scraping and comparing app
The aim of the app is to search for every possible flight connection based on user input:
- Departure date range,
- Minimum and maxiumum number of days between departure and return,
- Number of passengers.

Flights are being searched and saved, then sorted ascending by price. There are main 4 steps in this process:

### 1. Webdriver initialization, opening Ryanair website and running GUI.
Program opens a website and scraps all possible departure airports. In the meantime it runs GUI, Departure airports listbox is being filled with scrapped airports.
### 2. Entering the input data.
User picks departure airports and confirms choice. Driver searchs for available destination airports and fills listbox. Then user defines destinations and confirms choice. Afterwards user decide if return flight should be to the same airport or to any of the departure list. Then user deines date range, minimum and maximum number of days and number of passengers.
### 3. Collecting flights, saving as DataFrame and sorting ascending by price.
Webdriver searches for air connetions between departure and destination airports - pairs of flights are saved as an one connection. Data is being grouped by number of flight, sorted and saved as pandas DataFrame.
Prices are converted to one, choosen currency - current exchange rates are downloaded using ExchangeRate-API.
### 4. Conversion to CSV/XLSX file.
Data is saved as a *.csv or *.xlsx format and optionally automatically opened.
