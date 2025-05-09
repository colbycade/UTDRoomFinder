## Setup Instructions

Follow these steps to set up and run the application:

1. **Ensure Python is Installed:**
   - Make sure Python 3.7 or higher is installed on your system. You can check by running:
     ```
     python --version
     ```

2. **Navigate to the Project Folder:**
   - Open a terminal or command prompt and navigate to the folder where the project files are located:
     ```
     cd path/to/project-folder
     ```

3. **Create a Virtual Environment:**
   - Create a virtual environment to isolate dependencies:
     ```
     python -m venv .venv
     ```

4. **Activate the Virtual Environment:**
   - On Linux/macOS:
     ```
     source .venv/bin/activate
     ```
   - On Windows:
     ```
     .\.venv\Scripts\activate
     ```

5. **Install Dependencies:**
   - Install the required Python packages using `requirements.txt`:
     ```
     pip install -r requirements.txt
     ```

6. **Authenticate MongoDB**
   - If you want to use the production database, store your username and password as environment variables:
     ```
     export mongodb_user="your_username"
     export mongodb_pwd="your_password"
     ```
   - Alternatively, create a .env file in the root directory of the project:
    ```
    mongodb_user="your_username"
    mongodb_pwd="your_password"
    ```
  - The default database is in-memory. Run `export DB_TYPE="mongo"` to use the production database.
    - There are also VSCode launch configurations for using either database

7. **Run the Application:**
   - Note: You must first navigate to the 1_code directory with `cd 1_code`, or run `export FLASK_APP=1_code/app.py`. 
   - Start the Flask development server:
     ```
     flask run
     ```
   - Open your browser and go to `http://127.0.0.1:5000`.
   