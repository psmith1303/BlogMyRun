#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#
import requests
import json
import datetime
import string
import dateutil.parser as dparser
import argparse
import sys
import os
import time
from jinja2 import Environment, FileSystemLoader

import pdb

#
# Some basic definitions
#
authorization_token = {'access_token': '____7065-HQz+b1C3qaqyLuH6lrIPe54LtTrbCBboa6u3SVxvYE'}
api_base_url = 'https://api.smashrun.com/v1/my/'
error_code = 1      # In case we need to sys.exit()
map_marker = 'size:mid%7Ccolor:0xff0000%'
datestamp_filename = 'BlogMyRun-datestamp.txt'
bad_runs = [674029,672025,592434,674029,
            592449,592450,602932,3372906,
            3384512,3391412,3931662,3942470]


#
# Command-line variables
#
options_all_days = False
options_marker = False
options_ndays = 1
options_new_runs = False
options_page = 0
options_run_id = 0
options_stats = False
options_template_file = 'BlogMyRun.markdown'
options_test_map = False
options_verbose = 0
options_wait = 0

#             
# 592475


def vlog(level, message):
    """ print out a message if needed """
    if level <= options_verbose:
        print(message)
    return(True)


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)


def call_smashrun_api(api_function, api_extension = '', payload = {}):
    """ Does an authorized call of a SmashRun api function with a payload """
    payload.update(authorization_token)

    api = ''.join([api_base_url, api_function, api_extension])
    vlog(3, 'API url: {}'.format(api))
    
    response = requests.get(api, params=payload)
    
    if response.status_code != 200:
        print("*** Request failed: {} ***".format(response.status_code))
        print("*** Request url: {} ***".format(response.url))
        print("*** Request text: {} ***".format(response.text))
        result = []
        # sys.exit(error_code)
    else:
        result = json.loads(response.text)        

    vlog(4, 'API url complete: {}'.format(response.url))

    return(result)



def utc_days_ago(days):
    """ Convert a number of days into a unix timestamp """
    search_date = datetime.datetime.now() - datetime.timedelta(days=days)
    result = int(search_date.timestamp())
    return(result)



def get_activity_list():
    """ Get list the details of a SmashRun Actity """

    payload = {}
    api_function = '/activities/search/ids'

    if options_new_runs:
        if os.path.isfile(datestamp_filename):
            last_modified_date = int(os.path.getmtime(datestamp_filename))
        else:
            last_modified_date = 0

        vlog(2, 'Time stamp {}'.format(datetime.datetime.fromtimestamp(
            last_modified_date).strftime('%Y-%m-%d %H:%M:%S')))
            
        payload = {'fromDate' : last_modified_date}
    else:
        payload = {'fromDate' : utc_days_ago(options_ndays)}
        
    if options_all_days:
        # otherwise, get all runs since a date
        payload = {}
        
    if options_page > 0:
        # otherwise, get 100 runs on page 'n'
        payload = {'page' : options_page-1, 'count' : 100}
    
    activity_list = call_smashrun_api(api_function, payload = payload)
    return(activity_list)



def get_activity_details(activity_id):
    """ Get all the details of a SmashRun Actity """
    activity_details_list = call_smashrun_api('/activities/',
                                              api_extension=str(activity_id), payload = {})
    return(activity_details_list)



def get_activity_map(activity_id):
    """ Get the Google route of a SmashRun activity """
    polyline_list = call_smashrun_api('/activities/',
                                 api_extension= ''.join([str(activity_id), '/polyline']),
                                 payload = {})
    return(polyline_list)



def get_activity_map_thumbnail(activity_id):
    """ Get the SVG map of a SmashRun activity """
    polyline_list = call_smashrun_api('/activities/',
                                 api_extension= ''.join([str(activity_id), '/polyline/svg']),
                                 payload = {})
    return(polyline_list['polyline'])




def safe_dictionary_item(dictionary, item):
    """ return an item from a dictionary or None """
    if item in dictionary:
        result = dictionary[item]
    else:
        result = 0
    return(result)



def activity_base_filename(activity_details):
    """ make up the base filename to store Hugo posts, and their matching images """
    runDate = dparser.parse(activity_details['startDateTimeLocal'],fuzzy=True)
    fileName = runDate.strftime('%Y%m%d-%H%m-running')
    return(fileName)



def create_hugo_post(activity_details, username):
    """ create a hugo blog post from the activity_details and the added polyline """

    activity_id = activity_details['activityId']

    # The url of the equivalent page on SmashRun
    run_url = 'http://smashrun.com/{}/run/{}'.format(username, activity_id)
    
    # get the date of the run    
    runDate = dparser.parse(activity_details['startDateTimeLocal'],fuzzy=True)
    fileName = activity_base_filename(activity_details) + '.md'
    imageName = '{}{}'.format(activity_base_filename(activity_details), '.png')
    runDate.strftime('%Y%m%d-%H%m-running.md')
    slugName = runDate.strftime('run-details-%Y%m%d-%H%m')
    postDate = runDate.isoformat()
    logDate = runDate.strftime('%Y%m%d%H%m')
    svgPolyline = get_activity_map_thumbnail(activity_id)
    #
    # Fix timezone
    #
    if postDate[19] == '-':
        postDate = postDate[:19] + '+' + postDate[20:]
    else:
        postDate = postDate[:19] + '-' + postDate[20:]

    seconds = activity_details['duration']
    hours, seconds =  seconds // 3600, seconds % 3600
    minutes, seconds = seconds // 60, seconds % 60                  
    duration = '{:02.0f}:{:02.0f}:{:02.0f}'.format(hours, minutes, seconds)

    if activity_details['distance'] > 0:
        seconds = activity_details['duration'] // activity_details['distance']
        hours, seconds =  seconds // 3600, seconds % 3600
        minutes, seconds = seconds // 60, seconds % 60                  
        pace = '{:02.0f}:{:02.0f}'.format(minutes, seconds)
    else:
        pace = '00:00:00'

    #
    # Okay, let's populate the template
    #
    path = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(path, 'templates')
    template_environment = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=False,
        line_statement_prefix=None, # Do not what this mucking up markdown!
        trim_blocks=False)

    context = {'RunDate'         : str(postDate),
               'RunTitle'        : 'Ran {:.1f} Km in {} ({} min/Km)'.format(activity_details['distance'],
                                                                     duration, pace),
               'RunCategory'     : 'Runs',
               'RunSlug'         : slugName,
               'RunSVG'          : svgPolyline,
               'RunMapFile'      : '/images/run-maps/{}'.format(imageName),
               'RunNotes'        : activity_details['notes'],
               'RunSmashRunURL'  : run_url,
               'RunDistance'     : '{:.1f}'.format(safe_dictionary_item(activity_details, 'distance')),
               'RunDuration'     : str(duration),
               'RunPace'         : pace,
               'RunCalories'     : str(safe_dictionary_item(activity_details,'calories')),
               'RunHeartRateAve' : str(safe_dictionary_item(activity_details, 'heartRateAverage')),
               'RunHeartRateMax' : str(safe_dictionary_item(activity_details, 'heartRateMax')),
               'RunHeartRateMin' : str(safe_dictionary_item(activity_details, 'heartRateMin')),
               'RunVertGain'     : '{:.0f}'.format(safe_dictionary_item(activity_details, 'elevationGain')),
               'RunVertLost'     : '{:.0f}'.format(safe_dictionary_item(activity_details, 'elevationLoss')),
               'RunWeather'      : safe_dictionary_item(activity_details, 'weatherType'),
               'RunTemp'         : '{:.0f}'.format(safe_dictionary_item(activity_details, 'temperature')),
               'RunHumidity'     : safe_dictionary_item(activity_details, 'humidity'),
               'RunActivity'     : safe_dictionary_item(activity_details, 'activityType'),
               'RunSource'       : safe_dictionary_item(activity_details, 'source'),
               'RunID'           : str(safe_dictionary_item(activity_details, 'activityId'))
    }
    
    markdown = template_environment.get_template(options_template_file).render(context)

    vlog(2, fileName)
    with open(fileName, 'w') as fwrite:
        vlog(5, markdown)
        fwrite.write(markdown)
        fwrite.close()
        
    return(True)

 
def create_map_image(activity_details):
    """ Use the Google static maps api to create a map image """
    
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

def process_activity(activity_id, username):
    """ For a given activity_id create a post etc """
    
    activity_details = get_activity_details(activity_id)
    
    if len(activity_details) > 0:
        activity_details.update(get_activity_map(activity_id))
        create_hugo_post(activity_details, username)
        create_map_image(activity_details)
        result = True
    else:
        vlog(0, 'Error: Skipping run ID: {}'.format(activity_id))
        result = False
    return(result)

def process_activity_list(username):
    """ iterate through the list of activities """
    for activity in get_activity_list():
        if activity in bad_runs:
            vlog(0, 'Skipping bad run ID: {}'.format(activity))
        else:
            vlog(1, 'Activity ID: {}'.format(activity))
            process_activity(activity, username)
            if options_wait > 0:
                time.sleep(options_wait)
    return(True)


def check_positive(value):
    """ Check if an option is a positive integer """
    ivalue = int(value)
    
    if ivalue <= 0:
         raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def parse_args():
    """ parse any commandline arguments """
    global options_verbose
    global options_test_map
    global options_ndays                   # We use the default of 1 when nothing is specified.
    global options_new_runs
    global options_marker
    global options_page
    global options_run_id
    global options_stats
    global options_all_days
    global map_marker


    parser = argparse.ArgumentParser(description='Import runs from SmashRun to Hugo formatted blog posts.')

    parser.add_argument('-a', '--all', help='Get all the activities from SmashRun',
                        action='store_true')
    parser.add_argument('-d', '--days',
                        help='Get the activities that occured in the last n days (default: %(default)s)',
                        type=check_positive, default=1, const=1, nargs='?', action='store')
    parser.add_argument('-m', '--marker', help='URL of icon to be used as a marker on the maps',
                        action='store')
    parser.add_argument('-n', '--new-runs', help='Get all the runs since the last time the script was used',
                        action='store_true')
    parser.add_argument('-p', '--page', help='Get page n of 100 entries',
                        type=int, default=0, action='store')
    parser.add_argument('-r', '--run-id', help='Get a specific RUNID',
                        type=int, default=0, action='store')
    parser.add_argument('-s', '--stats', help='Print out some stats about SmashRun',
                        action='store_true')
    parser.add_argument('-w', '--wait', help='Wait n seconds between fetching runs (to overcome rate limiting)', 
                        type=check_positive, default=0, const=1, nargs='?', action='store')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', 
                        type=check_positive, default=0, const=1, nargs='?', action='store')

    args = parser.parse_args()

    if args.all:
        options_all_days = True       # Note this takes priority over the ndays option
    
    if args.marker:
        map_marker = 'icon:{}'.format(args.marker)

    if args.run_id:
        options_run_id = args.run_id
        
    if args.page:
        options_page = args.page

    if args.verbose:
        options_verbose = args.verbose
    else:
        options_verbose = 0

    options_ndays = args.days
    options_new_runs = args.new_runs
    options_test_map = False
        
    return(True)



def get_username():
    """ Get list the details of a SmashRun Actity """

    payload = {}
    api_function = '/userinfo'

    userinfo = call_smashrun_api(api_function, payload = payload)
    vlog(2, userinfo)

    username = userinfo['userName']
    vlog(1, username)
    return(username)


def main():
    """ process  runs from SmashRun into blog posts """
    parse_args()

    username = get_username()

    if options_run_id > 0:
        process_activity(options_run_id, username)
    else:
        process_activity_list(username)
        
    touch(datestamp_filename)
    return(True)



if __name__ == "__main__":
    main()

    
# For each month it create a macro-log comparing this month with
# previous months and previous year

# Add proper OAUTH2 authentication, so the script can work for anyone.
