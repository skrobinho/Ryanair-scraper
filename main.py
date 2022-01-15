import ryanair_gui

def main():
    ryanair_webdriver = ryanair_gui.RyanairWebdriver()
    ryanair_webdriver.open_website()
    flights_df = ryanair_webdriver.get_flights('EUR')
    ryanair_webdriver.save_as_excel(flights_df)
    ryanair_webdriver.quit_driver()

if __name__ == "__main__":
    main()