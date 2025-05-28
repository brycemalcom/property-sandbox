import os
from dotenv import load_dotenv
import requests
from typing import Dict, Any, Optional, Literal

# Load environment variables
load_dotenv()

class AcumidataClient:
    def __init__(self, environment: Literal["prod", "uat"] = "uat"):
        """
        Initialize the client with specified environment
        :param environment: "prod" or "uat"
        """
        self.environment = environment
        self.api_key = self._get_api_key()
        self.base_url = ("https://api.acumidata.com" 
                        if environment == "prod" 
                        else "https://uat.api.acumidata.com")
        
    def _get_api_key(self) -> str:
        """Get the appropriate API key based on environment"""
        if self.environment == "prod":
            return os.getenv("ACUMIDATA_PROD_KEY", "")
        return os.getenv("ACUMIDATA_UAT_KEY", "")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a GET request to the API"""
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        if params is None:
            params = {}
        
        print("1. Starting request...")
        
        try:
            print(f"2. Making request to: {url}")
            print(f"3. With params: {params}")
            print(f"4. Headers: {headers}")
            
            print("5. Sending request...")
            response = requests.get(
                url=url,
                headers=headers,
                params=params
            )
            print("6. Got response!")
            print(f"7. Status code: {response.status_code}")
            
            if response.status_code != 200:
                print(f"8. Error response: {response.text}")
                return {"error": f"API returned status {response.status_code}"}
            
            print("9. Parsing JSON...")
            return response.json()
        
        except Exception as e:
            print(f"X. Error occurred: {str(e)}")
            return {"error": str(e)}

    def get_home_value(self, address: str, city: str, state: str, zip_code: str) -> Dict:
        """
        Call the Acumidata API to get home value and key property data for a given address.
        """
        endpoint = f"{self.base_url}/api/Comps/advantage"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        params = {
            "streetAddress": address,
            "city": city,
            "state": state,
            "zip": zip_code
        }
        try:
            response = requests.get(endpoint, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_property_valuation(self, address: str, city: str, state: str, zip_code: str) -> dict:
        """
        Call the /api/Valuation/estimate endpoint to get property valuation data.
        """
        endpoint = "api/Valuation/estimate"
        params = {
            "streetAddress": address,
            "city": city,
            "state": state,
            "zip": zip_code
        }
        return self._make_request(endpoint, params)

    def get_qvm_simple(self, address: str, city: str, state: str, zip_code: str) -> dict:
        """
        Call the /api/Valuation/qvmsimple endpoint to get Quantarium QVM valuation data.
        """
        endpoint = "api/Valuation/qvmsimple"
        params = {
            "streetAddress": address,
            "city": city,
            "state": state,
            "zip": zip_code
        }
        return self._make_request(endpoint, params)

    def get_property_advantage(self, address: str, city: str, state: str, zip_code: str) -> dict:
        """
        Call the /api/Comps/advantage endpoint to get rich property and comparable data.
        """
        endpoint = "api/Comps/advantage"
        params = {
            "streetAddress": address,
            "city": city,
            "state": state,
            "zip": zip_code
        }
        return self._make_request(endpoint, params)
