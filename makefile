APIKEYFILE=key.dat
APIKEY=`cat $(APIKEYFILE)`
PUBLISH_DIR=~/Dropbox/dota/py2dotastats/

default: pdir
	cp makefile *.py LICENSE README.md $(PUBLISH_DIR)
	
pdir:
	mkdir -p $(PUBLISH_DIR)
	
clean:
	rm *.sqlite
