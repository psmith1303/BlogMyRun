# BlogMyRun

This programme:

1. Gets a list of all runs from SmashRun
2. For each run, it creates a Hugo compatible blog file (YAML header, Markdown body).
3. Add a Google static map to the run

## Installation

There is a little icon (runicon.png) that needs to exist on the web
somewhere. It is used as a marker on the Google map. You might like to change it to be something else. 




## To do.

1. Add a command line option to select  the icon used on map to be either:
  a. the default marker, or
  b. specify some icon on the web to use, e.g.,
	  BlogMyRun -i http://example.com/images/icon.png
  
2. Add a command line option to select the date from which runs should be uploaded, e.g.

    BlogMyRun.py -n 7  # seven days in the past, or
	BlogMyRun.py -a    # All of the history
   	BlogMyRun.py       # Just runs from today
	
2. For each month it create a macro-log comparing this month with previous months and previous year
3. Add proper OAUTH2 authentication, so the script can work for anyone.
  
