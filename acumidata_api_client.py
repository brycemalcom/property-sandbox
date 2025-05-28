import os
import json
import requests
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

class AcumidataApiClient:
    """
    A clean, simple client for the Acumidata API that handles authentication and property data retrieval.
    """
    def __init__(self, environment: str = "uat"):
        """
        Initialize the Acumidata API client
        :param environment: "prod" or "uat"
        """
        self.environment = environment
        self.base_url = ("https://api.acumidata.com" 
                        if environment == "prod" 
                        else "https://uat.api.acumidata.com")
        
        # Get credentials
        self.username = os.getenv("ACUMIDATA_USERNAME", "bmushaney1")
        self.password = os.getenv("ACUMIDATA_PASSWORD", "relar2024")
        self.api_key = None  # Will be obtained through login
        
        # Login to get API key
        self.login()
    
    def login(self) -> bool:
        """
        Login to Acumidata API to get a valid API key
        :return: True if login successful, False otherwise
        """
        try:
            login_data = {
                "username": self.username,
                "password": self.password
            }
            
            login_response = requests.post(
                f"{self.base_url}/api/Account/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                login_result = login_response.json()
                
                # Extract the API key from the login response
                if 'data' in login_result and 'acumiAPIKey' in login_result['data']:
                    self.api_key = login_result['data']['acumiAPIKey']
                    print(f"✓ Successfully logged in as {self.username}")
                    return True
                else:
                    print("❌ No API key found in login response")
                    return False
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
        except Exception as e:
            print(f"❌ Error during login: {str(e)}")
            return False

    def get_property_data(self, street_address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """
        Get property data from the Acumidata API
        """
        if not self.api_key:
            if not self.login():
                return {"error": "Not authenticated. Login failed."}
        
        endpoint = "api/Comps/advantage"
        
        params = {
            "streetAddress": street_address,
            "city": city,
            "state": state,
            "zip": zip_code
        }
        
        print(f"Fetching property data for {street_address}, {city}, {state} {zip_code}...")
        
        try:
            url = f"{self.base_url}/{endpoint}"
            
            headers = {
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.get(
                url=url,
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                print(f"Error: API returned status {response.status_code}")
                return {"error": f"API returned status {response.status_code}: {response.text}"}
            
            return response.json()
        
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return {"error": str(e)}
    
    def extract_property_details(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key property details from the API response
        """
        if "error" in property_data:
            return property_data
        
        details = {}
        
        # Extract property details from MLS data
        if "mlsData" in property_data and property_data["mlsData"]:
            mls_data = property_data["mlsData"]
            details["property"] = {
                "address": f"{mls_data.get('address', 'N/A')}, {mls_data.get('city', 'N/A')}, {mls_data.get('state', 'N/A')} {mls_data.get('zip', 'N/A')}",
                "beds": mls_data.get("beds", "N/A"),
                "baths": mls_data.get("baths", "N/A"),
                "year_built": mls_data.get("yearBuilt", "N/A"),
                "size": mls_data.get("size", "N/A"),
                "lot_size": mls_data.get("lotSize", "N/A"),
                "has_pool": mls_data.get("pool") is not None and mls_data.get("pool") != ""
            }
        
        # Extract comparable sold properties
        if "searchLists" in property_data and "Sold" in property_data["searchLists"]:
            sold_properties = property_data["searchLists"]["Sold"]
            details["comparable_sold"] = []
            
            for prop in sold_properties[:10]:  # Limit to 10 properties
                details["comparable_sold"].append({
                    "address": f"{prop.get('address', 'N/A')}, {prop.get('city', 'N/A')}, {prop.get('state', 'N/A')} {prop.get('zip', 'N/A')}",
                    "price": prop.get("price", "N/A"),
                    "beds": prop.get("beds", "N/A"),
                    "baths": prop.get("baths", "N/A"),
                    "size": prop.get("size", "N/A"),
                    "year_built": prop.get("yearBuilt", "N/A"),
                    "distance": prop.get("distance", "N/A"),
                    "days_on_market": prop.get("daysOnMarket", "N/A"),
                    "sale_date": prop.get("statusDate", "N/A")
                })
            
            # Calculate average price of comparable properties
            prices = [float(prop.get("price", 0)) for prop in sold_properties if prop.get("price")]
            if prices:
                details["market_analysis"] = {
                    "avg_price": sum(prices) / len(prices),
                    "min_price": min(prices),
                    "max_price": max(prices),
                    "num_comps": len(prices)
                }
                
                # Find similar properties (same beds/baths)
                if "property" in details and "beds" in details["property"] and "baths" in details["property"]:
                    target_beds = details["property"]["beds"]
                    target_baths = details["property"]["baths"]
                    
                    similar_properties = [
                        prop for prop in sold_properties
                        if prop.get("beds") == target_beds and prop.get("baths") == target_baths
                    ]
                    
                    similar_prices = [float(prop.get("price", 0)) for prop in similar_properties if prop.get("price")]
                    if similar_prices:
                        details["market_analysis"]["avg_similar_price"] = sum(similar_prices) / len(similar_prices)
                        details["market_analysis"]["num_similar_comps"] = len(similar_prices)
        
        return details

def main():
    """
    Main function to demonstrate the AcumidataApiClient
    """
    print("=== Acumidata API Client Demo ===")
    
    # Create client
    client = AcumidataApiClient()
    
    # Test with Dallas property
    print("\nTesting Dallas property...")
    dallas_data = client.get_property_data(
        street_address="2555 N Pearl St",
        city="Dallas",
        state="TX",
        zip_code="75201"
    )
    
    if "error" in dallas_data:
        print(f"Error: {dallas_data['error']}")
    else:
        dallas_details = client.extract_property_details(dallas_data)
        
        # Display property details
        print("\n=== Dallas Property Details ===")
        if "property" in dallas_details:
            property_info = dallas_details["property"]
            print(f"Address: {property_info.get('address', 'N/A')}")
            print(f"Beds: {property_info.get('beds', 'N/A')}")
            print(f"Baths: {property_info.get('baths', 'N/A')}")
            print(f"Year Built: {property_info.get('year_built', 'N/A')}")
            print(f"Size: {property_info.get('size', 'N/A')} sq ft")
        
        # Display market analysis
        if "market_analysis" in dallas_details:
            market = dallas_details["market_analysis"]
            print("\nMarket Analysis:")
            print(f"Average Price: ${market.get('avg_price', 0):,.2f}")
            print(f"Based on {market.get('num_comps', 0)} comparable properties")
            
            if "avg_similar_price" in market:
                print(f"Average Price (Similar Properties): ${market.get('avg_similar_price', 0):,.2f}")
                print(f"Based on {market.get('num_similar_comps', 0)} similar properties")
    
    # Test with Belfair property
    print("\nTesting Belfair property...")
    belfair_data = client.get_property_data(
        street_address="531 NE Beck Rd",
        city="Belfair",
        state="WA",
        zip_code="98528"
    )
    
    if "error" in belfair_data:
        print(f"Error: {belfair_data['error']}")
    else:
        belfair_details = client.extract_property_details(belfair_data)
        
        # Display property details
        print("\n=== Belfair Property Details ===")
        if "property" in belfair_details:
            property_info = belfair_details["property"]
            print(f"Address: {property_info.get('address', 'N/A')}")
            print(f"Beds: {property_info.get('beds', 'N/A')}")
            print(f"Baths: {property_info.get('baths', 'N/A')}")
            print(f"Year Built: {property_info.get('year_built', 'N/A')}")
            print(f"Size: {property_info.get('size', 'N/A')} sq ft")
        
        # Display market analysis
        if "market_analysis" in belfair_details:
            market = belfair_details["market_analysis"]
            print("\nMarket Analysis:")
            print(f"Average Price: ${market.get('avg_price', 0):,.2f}")
            print(f"Based on {market.get('num_comps', 0)} comparable properties")
            
            if "avg_similar_price" in market:
                print(f"Average Price (Similar Properties): ${market.get('avg_similar_price', 0):,.2f}")
                print(f"Based on {market.get('num_similar_comps', 0)} similar properties")
    
    # Option to save data
    save_option = input("\nWould you like to save the raw property data to files? (y/n): ")
    if save_option.lower() == 'y':
        with open("dallas_property_data.json", 'w') as f:
            json.dump(dallas_data, f, indent=2)
        with open("belfair_property_data.json", 'w') as f:
            json.dump(belfair_data, f, indent=2)
        print("Data saved to dallas_property_data.json and belfair_property_data.json")

if __name__ == "__main__":
    main() 