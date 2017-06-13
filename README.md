# BlogMyRun

This programme:

1. Gets a list of all runs from SmashRun
2. For each run, it creates a Hugo compatible blog file (YAML header, Markdown body).
3. Add a Google static map to the run

The format of the "blog entries" is determined by a [jinja2
template[(http://jinja.pocoo.org/docs/2.9/), so if your layout does
not quite match mine you can change it.

## Installation

### Requirements

You will need `jinja2` the html templating system. I install it like this:

	sudo pip install jinja2

### Configuration

To access the SmashRun API you will need to get a token. For now, I
use the [SmashRun API Explorer](https://api.smashrun.com/v1/explorer),
and get the token for 'client' (which happens to be me, and will be
you if you do it yourself).

There is an option for little icon that needs to exist on the web
somewhere. It is used as a marker on the Google map to mark the start
of the run. You might like to change it to be something else.
Otherwise, a default marker will be used.

## Usage

BlogMyRun.py      # Converts runs done in the last day

BlogMyRun.py -d 7 # Converts runs done in the last 7 days

BlogMyRun.py -p 2 # Converts page 2 of 100 activities; you can step through all the activities this way

BlogMyRun.py -a   # Converts all the runs from SmashRun; if you hit limits, do it a page (100 activities) at a time, use -p

BlogMyRun.py -m "https://goo.gl/5y3S82" # use the icon at the URL as the marker on the maps

BlogMyRun.py -v   # Be verbose, -v -v be more verbose

## To do.
	
1. For each month, create a macro-log comparing this month with previous months and previous year
2. Add proper OAUTH2 authentication, so the script can work for anyone.
  
