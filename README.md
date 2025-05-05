This is a web app that allows UTD students to find unoccupied rooms on campus to study in.  

Code is split between collecting classroom data, the web app itself, and testing:

Web Application Code (1_code):
- static/css/style.css - contains styling code for frontend
- static/js/script.js - contains dyanmic frontend code
- templates/base.html - base html for all pages on website
- templates/search.html - the search page
- templates/results.html - the search results page
- templates/schedule.html - the page that displays a given room's schedule on a certain day
- templates/map.html - a page with an embedded campus map
- app.py - contains the web app backend with API endpoints and calls to database access methods
- db_interface.py - interface outlining the necessary database access methods
- mock_db.py - an in-memory database implementation with sample data
- mongodb.py - a persistent database implementation that connects to MongoDB
- util.py - a utility class with some shared methods

Data Collection Scripts (2_data_collection):
1. 'download_spreadsheets.py' - downloads course schedule spreadsheets from the UTD coursebook
2. 'upload.py' - uploads raw course schedule data to MongoDB
3. 'intialize_semester.py' - initializes semester data and transforms raw data into daily room schedules
4. 'scrape_direction_url' - retrieves url links to room locations on the UTD campus map

Test Suites (3_testing):
- test_app.py - unit tests for the backend API endpoints
- test_db.py - integration tests for the MongoDB database

Detailed instructions for running data collection scripts, executing tests, and hosting the server and frontend locally are found in the README files within each subfolder. 

As explained in the README files, you will need a valid UTD student username and password as well as a username and password for connecting to MongoDB.
You should create a .env file in the root directory of this project with the following information:

username="your_utd_username"
password="your_utd_password"
mongodb_user="your_mongodb_username"
mongodb_pwd="your_mongodb_password"

Additionally, a demo is hosted at https://utdroomfinder.pythonanywhere.com.  