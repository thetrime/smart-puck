"""
Functions for finding out which bins to put out tomorrow if you live in Fife

This is a very rough PoC. It works, but it is just a script really.

You need a file called `uprn` containing your UPRN
"""

import urequests
import json
import utime
import ure

# Fetch the UPRN
with open('uprn', 'r') as file:
    uprn = file.read()

authURL = "https://www.fife.gov.uk/api/citizen?preview=false&locale=en"
dataURL = "https://www.fife.gov.uk/api/custom?action=powersuite_bin_calendar_collections&actionedby=bin_calendar&loadform=true&access=citizen&locale=en"
payload = {"name":"bin_calendar","data":{"uprn":uprn},"email":"","caseid":"","xref":"","xref1":"","xref2":""}


{"name":"keyservice","data":{"uprn":"<PUT UPRN HERE>"},"details":"","identifier":"","xref":"","xref1":"","xref2":""}

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

# Fetch the auth value from the first URL
response = urequests.get(authURL)
auth_header = response.headers.get("Authorization", "")
response.close()

# Post data to the real URL with the extracted Authorization header
headers = {"Authorization": auth_header, "Content-Type": "application/json"}
response = urequests.post(dataURL, json=payload, headers=headers)
print("Response Status:", response.status_code)
data = json.loads(response.text)['data']
response.close()

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
    (year, month, day, _, _, _, _, _, _) = utime.localtime()
    tomorrow = utime.mktime((year, month, day + 1, 0, 0, 0, 0, 0))

    if collection_date == tomorrow:
        print(f"Time to put out your {collection['colour']} bins!")

    print(f"  Record: {collection['colour']} on {collection['date']}, tomorrow={tomorrow} collection_date={collection_date}")