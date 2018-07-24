import urllib2
import pandas as pd
import json
import re, fileinput
import itertools


# in order to clean the json file from trailing commas
def remove_trailing_commas(json_like):

    trailing_object_commas_re = re.compile(
        r'(,)\s*}(?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
    trailing_array_commas_re = re.compile(
        r'(,)\s*\](?=([^"\\]*(\\.|"([^"\\]*\\.)*[^"\\]*"))*[^"]*$)')
    # Fix objects {} first
    objects_fixed = trailing_object_commas_re.sub("}", json_like)
    # Now fix arrays/lists [] and return the result
    return trailing_array_commas_re.sub("]", objects_fixed)

users = 'https://gist.githubusercontent.com/benjambles/ea36b76bc5d8ff09a51def54f6ebd0cb/raw/524e40ec297353b8070ff10ee0d9d847e44210f5/users.json'
venues = 'https://gist.githubusercontent.com/benjambles/ea36b76bc5d8ff09a51def54f6ebd0cb/raw/524e40ec297353b8070ff10ee0d9d847e44210f5/venues.json'

url_users = urllib2.urlopen(users)
url_venue = urllib2.urlopen(venues)
# dealing with users and lower casing all
with open ('users.json', 'w+') as outfile:
    outfile.write(url_users.read().lower())

# dealing with venues including cleaning the file and lower casing all
with open ('venues.txt', 'w+') as outfile:
    outfile.write(url_venue.read().lower())

original_venues = open('venues.txt')
json_out = ""
for line in original_venues:
    json_out += line

cleansed_venues = remove_trailing_commas(json_out)

with open ('venues.json', 'w+') as outfile:
    outfile.write(cleansed_venues)

# putting the users and venues in two pandas data frames
df_user = pd.DataFrame(pd.read_json('users.json'))
df_venues  = pd.DataFrame(pd.read_json('venues.json'))

# looping through venues within that loop through the user list
# and then checking if any drink in venues is in user drink preference
# also checking if the food users wont east is in the venue food menu.
# finally creating a list consisting of (users, preferred drinks, venue) and (users, food wont eat, venue)
f_message = []
d_message = []
for (venues_name ,venues_drink, venues_food) in itertools.izip_longest(df_venues['name'] ,df_venues['drinks'].iteritems(), df_venues['food'].iteritems()):
    for (v_drink, v_food) in itertools.izip_longest(venues_drink[1], venues_food[1]):
        for (user_name, users_drink, users_food) in itertools.izip_longest(df_user['name'] ,df_user['drinks'].iteritems(),df_user['wont_eat'].iteritems()):
            for u_drink in users_drink[1]:
                if v_drink == u_drink:
                    employee = user_name
                    good_venues = venues_name
                    drink_message = (employee, v_drink, good_venues)
                    if drink_message not in d_message:
                        d_message.append(drink_message)
                for u_food in users_food[1]:
                    if v_food == u_food:
                        food_message = (user_name,v_food ,venues_name)
                        if food_message not in f_message:
                            f_message.append(food_message)


# counting the number of people who can drink and also who wont eat along with the venue name
list_drink = []
for i in range(len(d_message)):
    if (d_message[i][0], d_message[i][2]) not in list_drink:
        list_drink.append((d_message[i][0], d_message[i][2]))

list_food = []
for i in range(len(f_message)):
    if (f_message[i][0], f_message[i][2]) not in list_food:
        list_food.append((f_message[i][0], f_message[i][2]))

output_venue = []
for venues_name in df_venues['name']:
    for drink_results in list_drink:
        if drink_results[1] == venues_name:
            output_venue.append(venues_name)

output_no_Venue = []
for bad_venues_name in df_venues['name']:
    for food_results in list_food:
        if food_results[1] == bad_venues_name:
            output_no_Venue.append(bad_venues_name)

count_drink_venues = {(i, output_venue.count(i)) for i in output_venue}
count_wonteat_venues = {(i, output_no_Venue.count(i)) for i in output_no_Venue}


print('number of people who can drink in these venues')
print(count_drink_venues)
print('number of people who cannot eat in these venues')
print(count_wonteat_venues)

# printing final result
print('Places to go:')
print('((Venue Name, numer of people who can drink), (Venue Name, numer of people who can have food))')
for drink_venues in count_drink_venues:
    if drink_venues[1] > 4:
        for wonteat_venues in count_wonteat_venues:
            if drink_venues[0] == wonteat_venues[0]:
                if wonteat_venues[1] < 3:
                    print(drink_venues, wonteat_venues)

print('Food result: (user name, wont eat food, venue name)')
print(f_message)