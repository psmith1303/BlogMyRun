#!/usr/bin/env python3
#
#
#
import requests
import json
import datetime
import string
import dateutil.parser as dparser
import argparse

import pdb

api_base_url = 'https://api.smashrun.com/v1/'
runner_name = 'peter.smith'
authorization_token = {'access_token': '____7065-vl9c9W0JyCiq+DN6Ku2jvs93VgoW5BCzXFSjH7dGda0'}

test_polyline = 'd_qvEu{sc`@eD}VeSocAuTiZyk@wmAoLeNeP}EoDeCgCuGaFw]o\\i`@_`@gQo]cMyO_a@wAkBk@k@gC{CAiBhD{EvB}NfEsGIuQQoDuC}FkCqPkFaDaKyHwP_d@eGyd@bD_P[qD_NwUqJkLyEaNeC{_@K{y@mBch@dGo]jCqp@s@wHsOcSqKuYgX}Qo@wJqCkGeAmNgGeNeFaGkZuV_KoAaSBiRqDefAe|@uByR_C`CeFwE~AsD'


options_verbose = 0
options_test_map = False
options_ndays = 1
options_marker = False
options_all_days = False
map_marker = 'size:mid%7Ccolor:0xff0000%'

def vlog(level, message):
    if level <= options_verbose:
        print(message)
    return(True)



def call_smashrun_api(api_function, api_extension = '', payload = {}):
    """ Does an authorized call of a SmashRun api function """
    payload.update(authorization_token)
    
    api = ''.join([api_base_url, runner_name, api_function, api_extension])

    vlog(2, 'API url: {}'.format(api))
    
    response = requests.get(api, params=payload)
    
    if response.status_code != 200:
        print("Request failed: {}".format(response.status_code))
        print("Request url: {}".format(response.url))
        print("Request text: {}".format(response.text))
        result = []
    else:
        result = json.loads(response.text)        

    vlog(3, 'API url complete: {}'.format(response.url))

    return(result)


def utc_days_ago(days):
    search_date = datetime.datetime.now() - datetime.timedelta(days=days)
    result = int(search_date.timestamp())

    # pdb.set_trace()
    
    return(result)


def get_activity_list():
    """ Get list the details of a SmashRun Actity """

    payload = {}

    if options_all_days:
        api_function = '/activities/search/ids'
    else:
        # otherwise, get yesterday
        api_function = '/activities/search/ids'
        payload = {'fromDate' : utc_days_ago(options_ndays)}
    
    activity_list = call_smashrun_api(api_function, payload = payload)
    return(activity_list)



def get_activity_details(activity_id):
    """ Get all the details of a SmashRun Actity """
    activity_details_list = call_smashrun_api('/activities/',
                                              api_extension=str(activity_id), payload = {})
    return(activity_details_list)



def get_activity_map(activity_id):
    """ Get the SVG map of a SmashRun activity """
    polyline_list = call_smashrun_api('/activities/',
                                 api_extension= ''.join([str(activity_id), '/polyline']),
                                 payload = {})
    return(polyline_list)


def safe_dictionary_item(dictionary, item):
    """ return an item from a dictionary or None """
    if item in dictionary:
        result = dictionary[item]
    else:
        result = 0
    return(result)


def activity_base_filename(activity_details):
    runDate = dparser.parse(activity_details['startDateTimeLocal'],fuzzy=True)
    fileName = runDate.strftime('%Y%m%d-%H%m-running')
    return(fileName)


def create_hugo_post(activity_details):
    """ create a hugo blog post from the activity_details and the added polyline """

    # The url of the equivalent page on SmashRun
    run_url = ' http://smashrun.com/{}/run/{}'.format(runner_name, activity_details['activityId'])

    
    # get the date of the run    
    runDate = dparser.parse(activity_details['startDateTimeLocal'],fuzzy=True)
    fileName = activity_base_filename(activity_details) + '.md'
    imageName = '{}{}'.format(activity_base_filename(activity_details), '.png')
    runDate.strftime('%Y%m%d-%H%m-running.md')
    slugName = runDate.strftime('run-details-%Y%m%d-%H%m')
    postDate = runDate.isoformat()
    logDate = runDate.strftime('%Y%m%d%H%m')
    #
    # Fix timezone
    #
    if postDate[19] == '-':
        postDate = postDate[:19] + '+' + postDate[20:]
    else:
        postDate = postDate[:19] + '-' + postDate[20:]

    print(fileName)

    fwrite = open("{}".format(fileName), 'w')

    seconds = activity_details['duration']
    hours, seconds =  seconds // 3600, seconds % 3600
    minutes, seconds = seconds // 60, seconds % 60                  
    duration = '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)

    seconds = activity_details['duration'] // activity_details['distance']
    hours, seconds =  seconds // 3600, seconds % 3600
    minutes, seconds = seconds // 60, seconds % 60                  
    pace = '{:02.0f}:{:02.0f}'.format(minutes, seconds)
    
    # write the header
    #
    fwrite.write('+++\n')
    fwrite.write('date = "' + postDate + '"\n')
    fwrite.write('title = "Ran {:.1f} Km in {} ({} min/Km)"\n'.format(activity_details['distance'], duration, pace))
    fwrite.write('categories = ["Runs"]\n')
    fwrite.write('slug = "' + slugName + '"\n')
    fwrite.write('draft = "False"\n')
    fwrite.write('runmap = "/images/run-maps/{}"\n'.format(imageName))
    fwrite.write('+++\n\n')

    fwrite.write(activity_details['notes'])

    fwrite.write('\n<!--more-->\n')
    fwrite.write('\n<center>')
    
    fwrite.write('[![Click to see the run on SmashRun](/images/run-maps/{} "A map of this run")]({})\n'.format(imageName, run_url))

    fwrite.write('</center>\n\n')


    fwrite.write('#### Details\n\n')
    fwrite.write('* Distance: {:.1f} Km\n'.format(safe_dictionary_item(activity_details, 'distance')))
    fwrite.write('* Duration: {}\n'.format(duration))
    fwrite.write('* Average pace: {} min/Km\n'.format(pace))
    fwrite.write('* Calories: {} Cal\n'.format(safe_dictionary_item(activity_details,'calories')))
    fwrite.write('* Heart rate (ave): {} bpm\n'.format(safe_dictionary_item(activity_details, 'heartRateAverage')))
    fwrite.write('* Heart rate (max):  {} bpm\n'.format(safe_dictionary_item(activity_details, 'heartRateMax')))
    fwrite.write('* Heart rate (min):  {} bpm\n'.format(safe_dictionary_item(activity_details, 'heartRateMin')))
    fwrite.write('* Elevation gain: {:.0f} m\n'.format(safe_dictionary_item(activity_details, 'elevationGain')))
    fwrite.write('* Elevation loss: {:.0f} m\n'.format(safe_dictionary_item(activity_details, 'elevationLoss')))
    fwrite.write('* Weather: {}\n'.format(safe_dictionary_item(activity_details, 'weatherType')))
    fwrite.write('* Temperature: {:.0f} &deg;C\n'.format(safe_dictionary_item(activity_details, 'temperature')))
    fwrite.write('* Humidity: {}%\n'.format(safe_dictionary_item(activity_details, 'humidity')))
    fwrite.write('* Activity: {}\n'.format(safe_dictionary_item(activity_details, 'activityType')))
    fwrite.write('* Source: {}\n'.format(safe_dictionary_item(activity_details, 'source')))
    fwrite.write('* Run ID: {}\n'.format(safe_dictionary_item(activity_details, 'activityId')))
    
    fwrite.write('\nFull details at [SmashRun]({})\n'.format(run_url))

    fwrite.close()
    return(True)

 
def create_map_image(activity_details):
    fileName = activity_base_filename(activity_details) + '.png'

    latitude = safe_dictionary_item(activity_details, 'startLatitude')
    longitude = safe_dictionary_item(activity_details, 'startLongitude')
    polyline = activity_details['polyline']

    payload = ['https://maps.googleapis.com/maps/api/staticmap?',
               'maptype=hybrid',
               'size=400x400',
               'sensor=true',
               'markers={}%7Clabel:S%7C{},{}'.format(map_marker, latitude, longitude),
               'path=enc:{}'.format(polyline)
    ]

    
    url = '&'.join(payload)

    response = requests.get(url)

    f=open(fileName,'wb')
    f.write(response.content)
    f.close()
    
    return(True)




def check_positive(value):
    ivalue = int(value)
    
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def parse_args():
    """ parse any commandline arguments """
    global options_verbose
    global options_test_map
    global options_ndays                   # We use the default of 1 when nothing is specified.
    global options_marker
    global options_all_days
    global map_marker


    parser = argparse.ArgumentParser(description='Import runs from SmashRun to Hugo formatted blog posts.')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='count')
    parser.add_argument('-a', '--all', help='Get all the activities from SmashRun',
                        action='store_true')
    parser.add_argument('-d', '--days',
                        help='Get the activities that occured in the last n days (default: %(default)s)',
                        type=check_positive, default=1, action='store')
    parser.add_argument('-m', '--marker', help='URL of icon to be used as a marker on the maps', action='store')

    args = parser.parse_args()

    options_verbose = args.verbose

    if args.marker:
        map_marker = 'icon:{}'.format(args.marker)
    
    if args.all:
        options_all_days = True       # Note this takes priority over the ndays option

    options_ndays = args.days

        
    options_test_map = False
        
    return(True)



def main():
    """ process  runs from SmashRun into blog posts """
    parse_args()

    for activity in get_activity_list():
        vlog(1, 'Activity ID: {}'.format(activity))
        activity_details = get_activity_details(activity)
        activity_details.update(get_activity_map(activity))
        create_hugo_post(activity_details)
        create_map_image(activity_details)
    return(True)



if __name__ == "__main__":
    main()

    
# For each month it create a macro-log comparing this month with
# previous months and previous year

# Add proper OAUTH2 authentication, so the script can work for anyone.
