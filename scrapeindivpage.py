import requests 
from bs4 import BeautifulSoup
import csv
import pandas as pd


# URL = "https://www.wateraid.org/uk/get-involved/events/london-landmarks-half-marathon"
# URL = "https://www.wateraid.org/uk/get-involved/events/yorkshire-three-peaks-weekend"
# URL = "https://www.wateraid.org/uk/get-involved/events/trek-kilimanjaro"
# URL = "https://www.wateraid.org/uk/get-involved/events/dragon-boat-race"
# URL = "https://www.wateraid.org/uk/get-involved/events/the-severn-trent-mountain-challenge"
# URL = "https://www.wateraid.org/uk/get-involved/fundraising/lent-appeal-jars-of-change"
# URL = "https://www.wateraid.org/uk/get-involved/fundraising/harvest-appeal"
# URL = "https://www.wateraid.org//uk/get-involved/teaching-resources/ks3/managing-climate-change"

# links = ["https://www.wateraid.org//uk/get-involved/events/ride-across-britain", "https://www.wateraid.org//uk/get-involved/teaching-resources/ks3/managing-climate-change", "https://www.wateraid.org/uk/get-involved/fundraising/harvest-appeal"]
# links = ["https://www.wateraid.org//uk/get-involved/events/dragon-boat-race", "https://www.wateraid.org//uk/get-involved/fundraising/play-our-raffle"]
links = []
with open('Listing Links (2024-07-15).csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        URL = row[0]
        links.append(URL)

activity_df = pd.DataFrame()
for URL in links:
    print(URL)
    page = requests.get(URL) 

    # Data Cleaning part 2: if URL does not point to html page, then ignore 
    # (this data cleaning) was placed here for greater efficiency because requests.get() was required
    content_type = page.headers.get('content-type', '')
    if 'text/html' not in content_type: 
        continue
    # page.encoding = 'uft-8'
    soup = BeautifulSoup(page.content, "html.parser")
    # print(soup.getText())

    # List of variables to be extracted - typically every event must have event name and event description
    event_name = ""
    # Upon analysis of different webpages on the site, it is found that WaterAid typically presents event dates in 3 ways:
    # (1) If there are no exact data / multiple dates possible, date is represented as a string of explanation words e.g. "New date TBC"
    # (2) If date of event is just one day, date is simply represented as e.g. "25 July 2024"
    # (3) If date of event takes place over a few days/ range of days, dates will be represented as a string of range e.g. "5 July 2024 - 7 July 2024"
    event_date = "" 
    event_loc = ""
    event_synopsis = ""
    event_description = ""
    event_link_to_register = ""
    cat1_activity_type = ""


    # [1] Extract Event Name
    event_name = soup.find('h1').text.strip()
    # print("name is", event_name)

    # [2] Extract Date (if available)
    try:
        #finds outer div container containing date div containers
        date_div = (soup.find('div', {"class":"field field-name-field-event-date paragraph--type--property"}) or 
                    soup.find('div', {"class":"paragraph paragraph--type--property paragraph--view-mode--default"}) ) 
        
        if date_div:
            # print(date_div.find('div', 'property-label').get_text())
            if date_div.find('div', 'property-label').get_text().find("Date") != -1:
                # print("Date header is found")
                date_content = date_div.findAll('div', class_='property property-value')[0]

                # if date is not already represented as a string, find date enclosed within <time> tags
                if date_content.find('time'):    
                    dates = date_content.findAll('time')
                    # print(dates)
                    # if there are two dates enclosed within <time> tags, then put "-" in between to represent as 3rd case
                    if len(dates) == 1:
                        date = dates[0]
                        event_date = date.get_text()
                    elif len(dates) == 2:
                        start = dates[0].get_text()
                        end = dates[1].get_text()
                        event_date = start + " - " + end
                            
                else: # else assign its value to event_date
                    event_date = date_content.get_text()

            else:
                event_date = "NA"

        else: # Dates usually contained within top left column, however sometimes it may be placed within the main body of information, hence type2:
            date_div_type2 = soup.findAll('div', class_='control-width clearfix')[0]
            date_content_type2 = date_div_type2.findAll('p')[0] #dates usually appear on the first instance of <p>
            # print("date content header", date_content_type2.get_text().find("Date"))
            # if date_content_type2.findAll('strong'): #test to see if <strong> within p; if no <strong> means date does not exist in text body
            if date_content_type2.get_text().find("Date") != -1: #if "Date" is part of the text, then date exist in text body
                end_index = date_content_type2.get_text().find("Location:")
                event_date = date_content_type2.get_text()[6:end_index]
            else:
                event_date = "NA"
                
    except:
        event_date = "NA"

    # print("date is", event_date)

    # [3] Extract Location (if available)
    try:
        #finds outer div container containing location div containers
        loc_div = soup.findAll('div', {"class":"paragraph paragraph--type--property paragraph--view-mode--default"})
        if loc_div != []:
            for para in loc_div:
            #finds location label div container within previous div and check its text is "Location:" or "Where:"
                loc_label = para.find('div', class_='property property-label').get_text()
                if "Location" in loc_label or "Where" in loc_label:
                    event_loc = para.findAll('div', class_='property property-value')[0].get_text()
                    break
                elif "Start" in loc_label:
                    event_loc += para.findAll('div', class_='property property-value')[0].get_text() + " to "
                    continue #to find next para with finish
                elif "Finish" in loc_label:
                    event_loc += para.findAll('div', class_='property property-value')[0].get_text()
                else:
                    continue
            if event_loc == "":
                event_loc = "NA"

        else: # Location usually contained within top left column, however sometimes it may be placed within the main body of information, hence type2:
            loc_div_type2 = soup.findAll('div', class_='control-width clearfix')[0]
            loc_content_type2 = loc_div_type2.findAll('p')[0]
            loc_content_type2_text = loc_content_type2.get_text()
            strong_check = loc_content_type2.findAll('strong') # check if <strong> within <p>
            if strong_check: # if <strong> within <p>, then there might be location and check if there is location
                for item in strong_check:
                    if "Location" in item.get_text():
                        start = loc_content_type2_text.find("Location:") + 10
                        end = loc_content_type2_text.find("Open to:")
                        if end == -1:
                            event_loc = loc_content_type2_text[start:]
                        else:
                            event_loc = loc_content_type2_text[start:end]
                        break
                    else:
                        event_loc = "NA"
            else: # if <strong> not within <p>, there is no location 
                event_loc = "NA"
            
    except:
        event_loc = "NA"

    # print("location is", event_loc)

    # [4] Extract Activity/Event Synopsis
    event_synopsis = soup.find('div', 'field field-name-field-synopsis').get_text().strip()
    event_synopsis.replace('&nbsp;', ' ')
    # print(event_synopsis)

    # [5] Extract Activity Description
    try:
        # Case 1: Check if Activity Description added as additional sub text of synopsis, if yes, extract
        synopsis_div = soup.findAll('div', 'event__synopsis column--middle')[0]
        sub_info_div = synopsis_div.findAll('div', 'field field-name-body control-width__inner--small')
        if sub_info_div != []:
            # if sub_info_div is not empty list means there are additional text in synopsis
            paras_in_div = sub_info_div[0].findAll('p')
            for para in paras_in_div:
                text = para.get_text()
                event_description += text
                event_description += " "
        
        else: 
            # else means no additional text in synopsis so check for case 2:
            # Case 2: Activity description contained within event content div container
            main_content_body_div = soup.find('div', 'event__content')
            main_sub_div_L1 = main_content_body_div.find('div', 'field field-name-field-wa-page-sections')
            main_sub_div_L2 = main_sub_div_L1.findAll('div', 'paragraph paragraph--type--page-section paragraph--view-mode--default bundle--general-text-area control-width')
            # from analysis of web pages, index til 2 because sufficient / valid activity description will be contained within first 1-3 paras in L2 sub div
            for para_div in main_sub_div_L2[:2]: 
                para = para_div.findAll('p')
                # If first <p> element contains <strong> element means that body of text is not description, we need to check the next para_div for description
                has_strong = para[0].findAll('strong')
                if has_strong != []: #if has strong list is not empty means <strong> element exist so then move onto the next para_div i.e. continue
                    continue
                else: #if has strong list is empty means the paragraphs in that para_div is the description, extract all text and break to stop loop
                    for p in para:
                        event_description += p.get_text()
                    if para_div.find('ul'): #for teaching resources type of activity, some of their webpages have <ul> as part of description, so check for that and extract
                        event_description += para_div.find('ul').get_text().strip()
                    event_description.replace('Â ', '&nbsp;')
                    break
            
        if event_description == "": #if event description still empty, means no description
            event_description = "NA"

    except:
        event_description = "NA"

    # print("eventdesp is", event_description)

    # [6] Find all hyperlinks to register for event 
    try: 
        # Find all <a> elements with class containing the word "button", 
        url_div = soup.findAll('a', "button")
        unique_ls_url_element = list(set(url_div)) # remove duplicates
        # and amongst these buttons find the button with the word "Register" and obtain the href links
        for a in unique_ls_url_element:
            if "Register" in a.get_text():
                event_link_to_register = a['href']

        if event_link_to_register == "":
            event_link_to_register = "NA"
                

    except:
        event_link_to_register = "NA"

    # print("link is", event_link_to_register)

    # [7] Extract type of activity level 1 category from page URL
    rev_url = URL[::-1]
    idx_of_last_slash = len(URL) - 1 - rev_url.find('/')
    start_idx = URL.find('get-involved/') + 13
    cat1_activity_type = URL[start_idx:idx_of_last_slash].replace('-', ' ')
    if cat1_activity_type.find("/") != -1:
        cat1_activity_type = cat1_activity_type[:cat1_activity_type.find("/")]
    # print(cat1_activity_type)

    activity = pd.DataFrame({
        'Listing URL': [URL],
        'Name of Activity': [event_name],
        'Date': [event_date],
        'Location': [event_loc],
        'Event Synopsis': [event_synopsis],
        'Event Description': [event_description],
        'Registration Link': [event_link_to_register],
        'Activity Category': [cat1_activity_type]
    })
    # print(event_description)
    activity_df = pd.concat([activity, activity_df])


activity_df.to_csv('Listings Details.csv', index=False, encoding='utf-8-sig')
