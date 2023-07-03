from time import sleep
from datetime import *
import sys
import pandas as pd
from playwright.sync_api import sync_playwright

def load_web(URL, df, dates):
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="domcontentloaded")
        sleep(6)
        try:
            alert_page = page.query_selector("//div[@class='b-pv3 alert-warn']")
        except:
            alert_page = True

        if alert_page is True or alert_page is not None:
            try:
                alert_text = alert_page.inner_text()
                if 'Unfortunately, this hotel is not available' in alert_text:
                    ua = []    
            except:
                try:
                    ua = page.query_selector_all("//div[@class='p-rate-card  b-ph0@md']")
                except:
                    ua = []
        else:
            try:
                ua = page.query_selector_all("//div[@class='p-rate-card  b-ph0@md']")
            except:
                ua = []
                
        if ua:
            temp_title = page.query_selector("//div[@class='hotel-name-text b-text_display-1 b-text_weight-bold']")

            if temp_title is None:
                temp_title = page.query_selector("//div[@class='b-text_copy-5 b-text_weight-light b-text_style-uppercase']")

            title = temp_title.inner_text()

            data = []
            for item in ua:
                room_type = item.query_selector("//div[@data-js='room-title']").inner_text()
                points = item.query_selector("//div[@class='rate b-text_weight-bold b-text_display-2']").inner_text()
                check_in = dates[0]
                check_out = dates[1]
                data.append((check_in, check_out, title, room_type, points))
        else:
            data = []
            check_in = dates[0]
            check_out = dates[1]
            data.append((check_in, check_out, 'None', 'None', 'None'))
        
        new_df =pd.DataFrame(data, columns=['Check-in', 'Check-out', 'Hotel', 'Room type', 'Points'])
        print(new_df)
        df = pd.concat([df, new_df], ignore_index=True)
        browser.close()
    return df
   
def get_URL_concat(hotel_code, item):
    URL = []
    URL.append('https://www.hyatt.com/shop/')
    URL.append(hotel_code)
    URL.append('?rooms=1&adults=1&checkinDate=')
    URL.append(item[0])
    URL.append('&checkoutDate=')
    URL.append(item[1])
    URL.append('&kids=0&accessibilityCheck=false&rateFilter=woh')
    return ''.join(URL)

def get_dates_list_string(start_date, end_date, nights):
    dates_list_string =[]
    while(start_date <= end_date):
        stay_start = start_date
        stay_end = stay_start+timedelta(days=nights)
        pair = (stay_start.strftime('%Y-%m-%d'), stay_end.strftime('%Y-%m-%d'))
        dates_list_string.append(pair)
        start_date = start_date+timedelta(1)
    return dates_list_string

def run(hotel_code, start_date, end_date):
    df=pd.DataFrame()
    start_date_object = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_object =  datetime.strptime(end_date, '%Y-%m-%d').date()
    items = get_dates_list_string(start_date_object, end_date_object, 1)
    for item in items:
        print("\nSearching", item, '...')
        URL_concat = get_URL_concat(hotel_code, item)
        df = load_web(URL_concat, df, item)
    print('\nDone searching, results:')
    print(df)

if __name__ == '__main__':
    run('itmph', '2023-12-01', '2023-12-31')

