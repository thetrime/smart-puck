"""
Functions for finding out which bins to put out tomorrow if you live in Fife

You need a file called `uprn` containing your UPRN
"""

import urequests
import json
import utime
import ure
import asyncio

# Fetch the UPRN
with open('uprn', 'r') as file:
    uprn = file.read()

authURL = "https://www.fife.gov.uk/api/citizen?preview=false&locale=en"
dataURL = "https://www.fife.gov.uk/api/custom?action=powersuite_bin_calendar_collections&actionedby=bin_calendar&loadform=true&access=citizen&locale=en"
payload = {"name":"bin_calendar","data":{"uprn":uprn},"email":"","caseid":"","xref":"","xref1":"","xref2":""}

# Council website has the weirdest date format. And utime has no strptime
MONTHS = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12
}

def update_bins(then):
    # Fetch the auth value
    response = urequests.get(authURL)
    auth_header = response.headers.get("Authorization", "")
    response.close()

    # Post data to the real URL with the extracted Authorization header
    headers = {"Authorization": auth_header, "Content-Type": "application/json"}
    response = urequests.post(dataURL, json=payload, headers=headers)
    data = json.loads(response.text)['data']
    response.close()

    result = {}
    for collection in data['tab_collections']:
        match = ure.match(r"(\w+), (\w+) (\d+), (\d+)", collection['date'])
        if not match:
            continue

        collection_month = MONTHS.get(match.group(2), 0)
        if collection_month == 0:
            continue
        collection_day = int(match.group(3))
        collection_year = int(match.group(4))

        collection_date = utime.mktime((collection_year, collection_month, collection_day, 0, 0, 0, 0, 0))
        (year, month, day, _, _, _, _, _) = utime.localtime()
        tomorrow = utime.mktime((year, month, day + 1, 0, 0, 0, 0, 0))

        # This sets the value of result[colour] to be:
        #    * True if the collection date is tomorrow
        #    * True if it was already set to true (regardless of the value here
        #    * False if it was previously unset or False, and the collection_date is not tomorrow
        result[collection['colour']] = result.get(collection['colour']) or (collection_date == tomorrow)

    print(f"Bins updated: {result}")
    then(result)

async def bin_updater(then):
    update_bins(then)
    while True:
        await asyncio.sleep(14400) # 4 hours
        update_bins(then)