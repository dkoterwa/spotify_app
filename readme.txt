!!!IMPORTANT!!!: repository does not contain secrets of spotify developer account, since they are sensitive data. If it is necessary for you to check every functionality of our app, then I can provide them (email me: d.koterwa2@student.uw.edu.pl).
!!!IMPORTANT!!!

I've recorded demo in order to provide the confirmation that everything is working, we were also showing everything in the class:
link to demo: https://www.youtube.com/watch?v=NSv8EIZC5w4

DESCRIPTION OF FILES:

spotify_data - folder with example of json files with personal streaming history and csv consisting songs to recommend.

notebooks - folder with notebooks to do some EDA, construct functions, etc.

website - main folder with app:
        __init__.py - script, which creates an app
        
        main.py - script, which contains every app route of app and operations done on every subpage
        
        song_characteristics.py - script with functions manipulating personal data in order to get 	insights 
        
        spotify_db.db - database with old structure (not used)
        
        spotify_db3.db - database used to manage data
        
        read_db.py - script with functions related to database (data upload, user upload)
        
        db_clear.py - script to easily clear specific table of database
        
        webscraping.py - we built it first to get photos of artists, but downloading them from API 	turned out to be a better option
        
        spot_secrets.py - file containing secrets of spotify developer account 
        
        db_check.py - script to easily check what is inside specific table of database
        
        plots.py - script with functions, which create plots
        
        Spotify_wrapped_doc.docx - file with documentation

templates - folder with html files of every app route

static - folder with static elements of website
        
HOW TO RUN THE APP:
    1. run main.py file
    2. upload json data and generate the results