import sys
import os

# Calculate the absolute path to the '1_code' directory
# os.path.dirname(__file__) gives the directory of conftest.py (3_basic_function_testing)
test_dir = os.path.dirname(__file__)
# os.path.join(..., '..', '1_code') goes up one level then into the 1_code directory
code_dir = os.path.abspath(os.path.join(test_dir, '..', '1_code'))

# Add the '1_code' directory to the Python path
sys.path.insert(0, code_dir)
