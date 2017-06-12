# BlogMyRun

This programme:

1. Gets a list of all runs from SmashRun
2. For each run, it creates a Hugo compatible blog file (YAML header, Markdown body).
3. Add a Google static map to the run

## Installation

There is a little icon (runicon.png) that needs to exist on the web
somewhere. It is used as a marker on the Google map. You might like to change it to be something else. 

## Usage

BlogMyRun.py      # Converts runs done in the last day

BlogMyRun.py -d 7 # Converts runs done in the last 7 days

BlogMyRun.py -a   # Converts all the runs from SmashRun

BlogMyRun.py -m "https://goo.gl/5y3S82" # use the icon at the URL as the marker on the maps

BlogMyRun.py -v   # Be verbose, -v -v be more verbose

## To do.
	
1. For each month, create a macro-log comparing this month with previous months and previous year
2. Add proper OAUTH2 authentication, so the script can work for anyone.
  
