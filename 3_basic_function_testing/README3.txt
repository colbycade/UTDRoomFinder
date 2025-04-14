How to Run Basic Function Tests

To unit test the web app, we will use an inmemory mock database and validate the effects of calling each api endpoint.

Prerequisites:
1.  Python 3.x installed.
2.  Pip (Python package installer) installed.
3.  A virtual environment is recommended to isolate dependencies:
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
4.  Install required Python packages:
    pip install -r requirements.txt
5.  Navigate to the testing directory: 
    cd 3_basic_function_testing

Running the Tests:
    A run config for VS Code is included in .vscode/launch.json.
    Alternatively, run tests directly from the command line:

    Command:
    pytest

    Optional: For more detailed output, use the verbose flag:
    pytest -v

    Optional: To see print statements within the tests (useful for debugging):
    pytest -s


Manual Testing
A version of the webapp using a mock database is hosted at https://utdroomfinder.pythonanywhere.com/.
Alternatively, follow the instructions in README1 to run the app locally.