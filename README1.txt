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
     python -m venv venv
     ```

4. **Activate the Virtual Environment:**
   - On Linux/macOS:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```

5. **Install Dependencies:**
   - Install the required Python packages using `requirements.txt`:
     ```
     pip install -r requirements.txt
     ```

6. **Run the Application:**
   - Start the Flask development server:
     ```
     flask run
     ```
   - Open your browser and go to `http://127.0.0.1:5000`.