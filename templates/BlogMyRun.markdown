+++
date = "{{ RunDate }}"
title = "{{ RunTitle }}"
categories = ["{{ RunCategory }}"]
slug = "{{ RunSlug }}"
type = "run"
draft = "False"
runmap = "{{ RunMapFile }}"
svgmap = '{{ RunSVG }}'
+++

{{ RunNotes }}

<!--more-->

<center>
[![Click to see the run on SmashRun]({{ RunMapFile }} "A map of this run")]({{ RunSmashRunURL }})
</center>

#### Run details

* Distance: {{ RunDistance }} Km
* Duration: {{ RunDuration }}
* Average pace: {{ RunPace }} min/Km
* Calories: {{ RunCalories }} Cal
* Heart rate (ave): {{ RunHeartRateAve }} bpm
* Heart rate (max): {{ RunHeartRateAve }} bpm
* Heart rate (min): {{ RunHeartRateAve }} bpm
* Elevation gain: {{ RunVertGain }} m
* Elevation loss: {{ RunVertLoss }} m
* Weather: {{ RunWeather }}
* Temperature: {{ RunTemp }} &deg;C
* Humidity: {{ RunHumidity }}%
* Activity: {{ RunActivity }}
* Source: {{ RunSource }}
* Run ID: {{ RunID }}

Full details at [SmashRun]({{ RunSmashRunURL }})
