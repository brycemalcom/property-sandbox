import os
from dotenv import load_dotenv
from acumidata_client import AcumidataClient

# Load environment variables
load_dotenv()

def main():
    client = AcumidataClient(environment="prod")
    address = "531 NE Beck Rd"
    city = "Belfair"
    state = "WA"
    zip_code = "98528"
    result = client.get_property_advantage(address, city, state, zip_code)
    print("API Response:")
    print(result)

if __name__ == "__main__":
    main() 