How Classroom Information Is Uploaded Into Database

The first stage of execution is in the 'download_spreadsheets.py'. Note, to run this portion, you will need to update the 'username' and 'password' variables to appropriate UTD accounts. Also note that the coursebook webpage does defend against botting, and, in this case, web scraping, it is recommended to have a rotating proxy setup for this portion. After the program's execution, the downloaded spreadsheets of each class prefix (ie. MATH, CS, EE, etc.) is moved into a folder located where the code is run. Next is to run 'upload.py'. Before running, the database that's used is MongoDB, so you will have to update the following variables: 

'password' to the password of your database
'connection_string' to your database's connection string
'class_information_collection' to your MongoDB cluster's structure

 once you run 'upload.py', the spreadsheets that were previously downloaded are extracted into the aforementioned data structure, and uploaded into the database. For reference,a spreadsheet is provided to simulate the upload to the database

