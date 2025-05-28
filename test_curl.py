print("=== Acumidata API Test (CURL) ===")

import subprocess
import json
from urllib.parse import quote

# API details
url = "https://uat.api.acumidata.com/api/Comps/advantage"
api_key = "J+mZiF5ERbq+qbtCkowTIrQCN5kBYYjlV0PR8ha4LeA="  # Your UAT key

# URL encode the address properly
address = quote("531 NE Beck Rd")
params = f"streetAddress={address}&city=Belfair&state=WA&zip=98528"

# Construct curl command with verbose output
curl_command = f'''curl -v -X GET "{url}?{params}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {api_key}"'''

print("\nExecuting curl command...")
print("Command:", curl_command)
try:
    # Execute curl command and capture output
    result = subprocess.run(
        curl_command, 
        shell=True, 
        capture_output=True, 
        text=True,
        check=True  # This will raise an exception if the command fails
    )
    
    print("\nCommand output:")
    print("Status:", result.returncode)
    print("\nStdout:")
    print(result.stdout or "No stdout")
    print("\nStderr:")
    print(result.stderr or "No stderr")
    
except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")
    print("Stdout:", e.stdout or "No stdout")
    print("Stderr:", e.stderr or "No stderr")
except Exception as e:
    print(f"Error: {str(e)}")
    print("Type:", type(e))

print("\nTest complete") 