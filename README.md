# Engeto Project 03

## Election scraper.
### election-scraper: 3rd project to ENGETO Online Python Academy.

author: Martin Alex Urbiš

email: urbis.martin@gmail.com

discord: segen0

### Project Description

The aim of the project is to develop an application that will extract the results of the 2017 parliamentary elections for a selected electoral district. The link to the source website can be found here.

### Package Instalation

The libraries that are used in the code are stored in the requirements.txt file. To install, create a new virtual environment and run the following with the manager installed:

$ pip3 --version                    # check manager version

$ pip install -r requirements.txt   # packages installation


### Project Execution

Execution of the file election_scraper.py requires two mandatory arguments on the command line:

python election-scraper.py <odkaz_uzemni_celek> <vystupni_soubor>

After the program is executed, the output file with the results with the extension .csv is downloaded to the currently used directory from where election-scraper was executed.

### Project Demonstration

Voting results for the electoral district Zlin:

1. argument: 'https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7204'
2. argument: 'vysledky_zlin'

Program execution: python election_scraper.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7204" "vysledky_zlin"

The download process: 

DOWNLOADING DATA FROM SELECTED URL: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=13&xnumnuts=7204
SAVE TO FILE:  vysledky_zlin.csv
ENDING THE PROGRAM  election_scraper.py

Output preview (csv file):

code,location,registred,envelopes,valid,Občanská demokratická strana ...
588318,Bělov,257,174,174,25,0,0,8,-,0,14,20,1,0,-,2,0,0,14,-,-,-,0,6,51,0,0,9,-,4,0,0,20,0,-
585076,Biskupice,564,314,314,17,1,0,16,-,0,15,34,2,6,-,15,0,0,16,-,-,-,0,1,102,0,1,38,-,2,0,2,42,4,-
557102,Bohuslavice nad Vláří,315,201,201,19,1,0,24,-,1,8,13,2,3,-,1,1,0,16,-,-,-,0,2,65,1,0,22,-,0,0,3,18,1,-
585092,Bohuslavice u Zlína,637,399,397,32,0,0,28,-,0,36,24,6,5,-,5,0,0,21,-,-,-,0,8,125,0,3,40,-,1,2,0,54,7,-



