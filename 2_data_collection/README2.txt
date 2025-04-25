How Classroom Information Is Uploaded Into Database

The first stage of execution is in the 'download_spreadsheets.py'. 
Note, to run this portion, you will need to update the 'username' and 'password' variables to appropriate UTD accounts. 
- You can manually adjust these variables in the code, set the 'username' and 'password' environment variables, or include them in a .env file.
Also note that the coursebook webpage does defend against botting, and, in this case, web scraping, it is recommended to have a rotating proxy setup for this portion. 
After the program's execution, the downloaded spreadsheets of each class prefix (ie. MATH, CS, EE, etc.) is moved into the "raw_classroom_information" folder located where the code is run. 

The next script to run is 'upload.py'.
Before running, the database that's used is MongoDB, so you will have to update the following variables: 

- 'user' to your MongoDB username
    - Alternatively, set the environment variable 'mongodb_user' or include it in a .env file.
- 'password' to your MongoDB password
    - Alternatively, set the environment variable 'mongodb_pwd' or include it in a .env file.
- 'class_information_collection' to your MongoDB cluster's structure

Once you run 'upload.py', the spreadsheets that were previously downloaded are extracted into the aforementioned data structure, and uploaded into the database. 
For reference, a spreadsheet is provided to simulate the upload to the database.

How to Initialize Semester Data

The application needs to track each individual school day, so we need to take the scraped data and create a complete day-by-day schedule for each room. 
The script to transform the scraped data is 'initialize_semester.py'.
Because this is ran for a specific semester, there is some configuration needed before running:
- The name of the MongoDB collection that the scraped data is stored in must be placed in the `CLASS_INFO_COLLECTION` variable.
- The desired name of the new collection where semester data will be stored must be placed in the `SEMESTER_COLLECTION` variable.
- The first and last day of class for the current semester must be placed in the `CLASSES_START` and `CLASSES_END` variables.
- Any days where there will be no school between these two dates should be indicated in the `HOLIDAYS` variable.

