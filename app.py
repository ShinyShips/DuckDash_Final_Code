from flask import Flask, flash, redirect, render_template, request, session, jsonify
import requests
import json
import urllib

app = Flask(__name__)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        value = lookup(request.form.get("place"), request.form.get("food"), request.form.get("price"), request.form.get("transaction"), request.form.get("radius"))
        # print(request.form.get("place"))
        # new_value = jsonify(value)
        return render_template("search_response.html", result=value)
    else:
        return render_template("index.html")


@app.route("/finer_search", methods=["GET", "POST"])
def finer_search():
    if request.method == "POST":
        value = finer_lookup(request.form.get("info"))
        print(value)
        return render_template("finer_search.html", result=value)
    else:
        return render_template("search_response.html")


def lookup(place_name, typeof, cost, transaction, radius):
    api_key = 'SGM-OyedJzwu2FAqQ-z2Vm9rNEahRpWR-a3_4KS6pSrW4nia4MOGBFse_3N5o319MMbO3dR2dHt_LISoWgqY411OM8Cpmnypy2-JsDGeKL6vvcf6O4Ce4d63P6jKXHYx'
    url = 'https://api.yelp.com/v3'
    search_path = 'https://api.yelp.com/v3/businesses/search'
    business_path = 'https://api.yelp.com/v3/businesses/'  # trailing / bc need to append the business id to the path

    headers = {'Authorization': 'Bearer %s' % api_key}

    look_up = ''
    if place_name == '' and typeof != '':
        look_up = typeof
    elif place_name != '' and typeof == '':
        look_up = place_name
    else:
        look_up = place_name

    if cost == '$' and look_up == typeof:
        cost = '1'
    elif cost == '$$' and look_up == typeof:
        cost = '2'
    elif cost == '$$$' and look_up == typeof:
        cost = '3'
    elif cost == '$$$$' and look_up == typeof:
        cost = '4'
    else:
        cost = '1,2,3,4'

    if transaction == 'delivery' and look_up == typeof:
        transaction = 'delivery'
    elif transaction == 'pickup' and look_up == typeof:
        transaction = 'pickup'
    else:
        transaction = 'delivery, pickup'

    if radius != '':
        radius = 2000

    parameters = {'term': look_up,
                  'limit': 20,
                  'radius': radius,
                  'price': cost,
                  'transactions': transaction,
                  'location': 'Hoboken'}

    parameters1 = {'locale': 'en_US'}

    response = requests.get(url=search_path, params=parameters, headers=headers)

    # response = json.loads(response.decode('utf-8'))
    search_data = response.json()

    # print(search_data1['hours'])
    # print(search_data["businesses"])
    new_lis = []
    x = 0
    for biz in search_data['businesses']:

        new_lis.append([biz['name']])
        # ide= search_data['businesses'][x]['id']
        new_lis[x].append(search_data['businesses'][x]['id'])
        print(search_data['businesses'][x]['id'])
        business_path = business_path + search_data['businesses'][x]['id']

        response1 = requests.get(url=business_path, params=parameters1, headers=headers)
        search_data1 = response1.json()
        end_time = 0
        try:
            if int(search_data1['hours'][0]['open'][0]['end']) > 12:
                end_time = int(search_data1['hours'][0]['open'][0]['end']) - 1200
            else:
                end_time = int(search_data1['hours'][0]['open'][0]['end'])

            new_lis[x].append(search_data1['hours'][0]['open'][0]['start'] + ' - ' + str(end_time))
        except:
            new_lis[x].append('Information Unavaiable')

        new_lis[x].append(biz['location']['address1'])
        new_lis[x].append(biz['phone'])
        if biz['is_closed'] == False:
            new_lis[x].append('Open')
        else:
            new_lis[x].append('Closed')
        new_lis[x].append(biz['rating'])
        try:
            if biz['price'] != None:
                new_lis[x].append(biz['price'])
        except:
            new_lis[x].append('Information Unavaiable')
        business_path = 'https://api.yelp.com/v3/businesses/'
        x += 1

    return new_lis


def finer_lookup(place_id):
    api_key = 'SGM-OyedJzwu2FAqQ-z2Vm9rNEahRpWR-a3_4KS6pSrW4nia4MOGBFse_3N5o319MMbO3dR2dHt_LISoWgqY411OM8Cpmnypy2-JsDGeKL6vvcf6O4Ce4d63P6jKXHYx'
    url = 'https://api.yelp.com/v3'
    search_path = 'https://api.yelp.com/v3/businesses/search'
    print(place_id)
    business_path = 'https://api.yelp.com/v3/businesses/' + place_id  # trailing / bc need to append the business id to the path

    headers = {'Authorization': 'Bearer %s' % api_key}

    # parameters = {'term': look_up,
    #              'limit': 1,
    #              'radius': 1000,
    #             'location': 'Hoboken'}

    parameters1 = {'locale': 'en_US'}

    response = requests.get(url=business_path, params=parameters1, headers=headers)

    # response = json.loads(response.decode('utf-8'))
    search_data = response.json()

    # print(search_data)

    # print(search_data['name'])

    # print(search_data1['hours'])
    # print(search_data["businesses"])
    new_lis = []

    for x in range(1):

        new_lis.append([search_data['name']])

        try:
            if int(search_data['hours'][0]['open'][0]['end']) > 12:
                end_time = int(search_data['hours'][0]['open'][0]['end']) - 1200
            else:
                end_time = int(search_data['hours'][0]['open'][0]['end'])
            new_lis[x].append(search_data['hours'][0]['open'][0]['start'] + ' - ' + str(end_time))
        except:
            new_lis[x].append('Information Unavailable')

        new_lis[x].append(search_data['location']['address1'])
        new_lis[x].append(search_data['phone'])
        if search_data['is_closed'] == False:
            new_lis[x].append('Open')
        else:
            new_lis[x].append('Closed')
        new_lis[x].append(search_data['rating'])
        try:
            if search_data['price'] != None:
                new_lis[x].append(search_data['price'])
        except:
            new_lis[x].append(['Information Unavailable'])
        # business_path = 'https://api.yelp.com/v3/businesses/'

        # new_lis[x].append(search_data['url'])
        # new_lis[x].append(search_data['image_url'])

        review_path = 'https://api.yelp.com/v3/businesses/' + place_id + '/reviews'

        response1 = requests.get(url=review_path, params=parameters1, headers=headers)

        search_data1 = response1.json()

        new_lis[x].append(search_data1['reviews'][0]['text'])
        new_lis[x].append(search_data['url'])
        new_lis[x].append(search_data['image_url'])

    return new_lis


if __name__ == '__main__':
    app.run()

