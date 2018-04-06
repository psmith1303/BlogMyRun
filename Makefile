new:
	./BlogMyRun.py -n -m "http://www.petersmith.org/images/runicon.png"

all:
	./BlogMyRun.py -a -w 60 -m "http://www.petersmith.org/images/runicon.png"

stage:
	mv [0-9]*.md /home/psmith/NAS/Programming/Websites-source/petersmith/content/running
	mv [0-9]*.png /home/psmith/NAS/Programming/Websites-source/petersmith/static/images/run-maps

deploy: stage
	/home/psmith/NAS/Programming/Websites-source/petersmith/Scripts/deploySite.sh

.PHONY: clean

clean:
	rm -fr [0-9]*.md [0-9]*.png
