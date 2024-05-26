# Example Python script with intentional small errors for educational purposes

imp ort hashlib
import os

def insecure_md5_hash(input_string):
    # Using MD5 for cryptographic purposes is insecure as it's vulnerable to collision attacks
    return hashlib.md5(input_string.encode()).hexdigest()

def read_file(file_path):
    # No exception handling for potential IO errors
    with open(file_path, 'r') as file:
        return file.read()

def get_user_data():
    # Simulated deprecated function usage
    user_data = os.popen('whoami') # os.popen is deprecated in favor of subprocess.run
    return user_data.read().strip()

if __name__ == "__main__":
    user_input = "test123"
    print("MD5 Hash:", insecure_md5_hash(user_input))
    
    try:
        print("Reading from non_existing_file.txt:", read_file("non_existing_file.txt"))
    except FileNotFoundError:
        print("Error: File not found.")
    
    print("Current User:", get_user_data())
