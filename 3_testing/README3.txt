How to Run Unit and Integration Tests

To unit test the web app in test_app.py, we use an inmemory mock database and validate the effects of calling each api endpoint.
To perform integration tests in test_db.py, we use a test MongoDB database and validate calling the different database operation methods.

Prerequisites:
1.  Python 3.x installed.
2.  Pip (Python package installer) installed.
3.  A virtual environment is recommended to isolate dependencies:
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
4.  Install required Python packages:
    pip install -r requirements.txt
5.  Navigate to the testing directory: 
    cd 3_testing

Running the Tests:
    A run config for VS Code is included in .vscode/launch.json.
    Alternatively, run all tests directly from the command line:

    To run all tests (both unit and integration):
    `pytest`

    To run a specific test suite:
    `pytest testfile.py`


Manual Testing
A version of the webapp using a mock database is hosted at https://utdroomfinder.pythonanywhere.com/.
Alternatively, follow the instructions in README1 to run the app locally.