import os
import json
import requests
from dotenv import load_dotenv
import openai
from typing import Dict, Any, Optional, List

# Load environment variables
load_dotenv()

class PropertyDataProcessor:
    def __init__(self, environment: str = "uat"):
        """
        Initialize the property data processor
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
        self._login()
        
        # Initialize OpenAI client if API key is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.openai_client = openai.OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None
            print("Warning: OpenAI API key not found. AI analysis will not be available.")
    
    def _login(self) -> bool:
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
                return {"error": f"API returned status {response.status_code}"}
            
            return response.json()
        
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return {"error": str(e)}
    
    def extract_key_property_insights(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key insights from the property data
        """
        insights = {
            "property_details": {},
            "market_analysis": {},
            "comparable_properties": {
                "sold": [],
                "pending": [],
                "active": []
            }
        }
        
        # Extract property details
        if "mlsData" in property_data and property_data["mlsData"]:
            mls_data = property_data["mlsData"]
            insights["property_details"] = {
                "address": f"{mls_data.get('address', '')}, {mls_data.get('city', '')}, {mls_data.get('state', '')} {mls_data.get('zip', '')}",
                "beds": mls_data.get("beds"),
                "baths": mls_data.get("baths"),
                "year_built": mls_data.get("yearBuilt"),
                "size": mls_data.get("size"),
                "lot_size": mls_data.get("lotSize"),
                "has_pool": mls_data.get("pool") is not None,
                "predicted_price": mls_data.get("predictedPrice", 0)
            }
        
        # Extract comparable sold properties
        if "searchLists" in property_data and "sold" in property_data["searchLists"]:
            sold_properties = property_data["searchLists"]["sold"]
            for prop in sold_properties[:10]:  # Limit to 10 properties
                insights["comparable_properties"]["sold"].append({
                    "address": f"{prop.get('address', '')}, {prop.get('city', '')}, {prop.get('state', '')} {prop.get('zip', '')}",
                    "price": prop.get("price"),
                    "beds": prop.get("beds"),
                    "baths": prop.get("baths"),
                    "size": prop.get("size"),
                    "year_built": prop.get("yearBuilt"),
                    "distance": prop.get("distance"),
                    "days_on_market": prop.get("daysOnMarket")
                })
        
        # Extract pending properties
        if "searchLists" in property_data and "pending" in property_data["searchLists"]:
            pending_properties = property_data["searchLists"]["pending"]
            for prop in pending_properties[:5]:  # Limit to 5 properties
                insights["comparable_properties"]["pending"].append({
                    "address": f"{prop.get('address', '')}, {prop.get('city', '')}, {prop.get('state', '')} {prop.get('zip', '')}",
                    "price": prop.get("price"),
                    "beds": prop.get("beds"),
                    "baths": prop.get("baths"),
                    "size": prop.get("size"),
                    "year_built": prop.get("yearBuilt"),
                    "distance": prop.get("distance"),
                    "days_on_market": prop.get("daysOnMarket")
                })
        
        # Extract active listings (open)
        if "searchLists" in property_data and "open" in property_data["searchLists"]:
            open_properties = property_data["searchLists"]["open"]
            for prop in open_properties[:10]:  # Limit to 10 properties
                insights["comparable_properties"]["active"].append({
                    "address": f"{prop.get('address', '')}, {prop.get('city', '')}, {prop.get('state', '')} {prop.get('zip', '')}",
                    "price": prop.get("price"),
                    "beds": prop.get("beds"),
                    "baths": prop.get("baths"),
                    "size": prop.get("size"),
                    "year_built": prop.get("yearBuilt"),
                    "distance": prop.get("distance"),
                    "days_on_market": prop.get("daysOnMarket")
                })
        
        # Calculate market analysis
        if insights["comparable_properties"]["sold"]:
            sold_prices = [float(prop["price"]) for prop in insights["comparable_properties"]["sold"] if prop["price"]]
            if sold_prices:
                insights["market_analysis"]["avg_sold_price"] = sum(sold_prices) / len(sold_prices)
                insights["market_analysis"]["min_sold_price"] = min(sold_prices)
                insights["market_analysis"]["max_sold_price"] = max(sold_prices)
        
        if insights["comparable_properties"]["active"]:
            active_prices = [float(prop["price"]) for prop in insights["comparable_properties"]["active"] if prop["price"]]
            if active_prices:
                insights["market_analysis"]["avg_listing_price"] = sum(active_prices) / len(active_prices)
                insights["market_analysis"]["min_listing_price"] = min(active_prices)
                insights["market_analysis"]["max_listing_price"] = max(active_prices)
        
        return insights
    
    def generate_ai_insights(self, property_insights: Dict[str, Any], user_query: Optional[str] = None) -> str:
        """
        Generate AI insights based on property data
        """
        if not self.openai_client:
            return "AI analysis not available. Please set the OPENAI_API_KEY environment variable."
        
        # Format the property insights for the AI
        property_json = json.dumps(property_insights, indent=2)
        
        # Default query if none provided
        if not user_query:
            user_query = "What insights can you provide about this property and its market value?"
        
        # Create the prompt for the AI
        prompt = f"""
        You are a real estate expert AI assistant. You have been provided with property data and market analysis.
        Please analyze this data and provide helpful insights to the user.
        
        Property Data:
        {property_json}
        
        User Query: {user_query}
        
        Provide a detailed, conversational response that addresses the user's query and offers valuable insights 
        about the property and its market value. Include specific data points from the property data to support 
        your analysis. If there are ways the homeowner could potentially increase their property value, mention those as well.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo",  # Use an appropriate model
                messages=[
                    {"role": "system", "content": "You are a real estate expert AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error generating AI insights: {str(e)}")
            return f"Error generating AI insights: {str(e)}"

class PropertyAIAssistant:
    def __init__(self):
        self.processor = PropertyDataProcessor()
        self.current_property_data = None
        self.current_property_insights = None
    
    def analyze_property(self, street_address: str, city: str, state: str, zip_code: str) -> Dict[str, Any]:
        """
        Analyze a property and store the results
        """
        # Get property data
        self.current_property_data = self.processor.get_property_data(
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code
        )
        
        # Extract insights
        if "error" not in self.current_property_data:
            self.current_property_insights = self.processor.extract_key_property_insights(self.current_property_data)
            return self.current_property_insights
        else:
            return self.current_property_data
    
    def get_ai_response(self, user_query: str) -> str:
        """
        Get AI response to a user query about the current property
        """
        if not self.current_property_insights:
            return "Please analyze a property first using the analyze_property method."
        
        return self.processor.generate_ai_insights(self.current_property_insights, user_query)

def main():
    """
    Main function to demonstrate the PropertyAIAssistant
    """
    print("=== Property AI Assistant ===")
    
    # Create assistant
    assistant = PropertyAIAssistant()
    
    # Get property details from user
    street_address = input("Enter street address: ")
    city = input("Enter city: ")
    state = input("Enter state (2-letter code): ")
    zip_code = input("Enter ZIP code: ")
    
    # Analyze property
    print("\nAnalyzing property...")
    insights = assistant.analyze_property(street_address, city, state, zip_code)
    
    if "error" in insights:
        print(f"Error: {insights['error']}")
        return
    
    # Print basic property details
    property_details = insights.get("property_details", {})
    print("\nProperty Details:")
    print(f"Address: {property_details.get('address', 'N/A')}")
    print(f"Beds: {property_details.get('beds', 'N/A')}")
    print(f"Baths: {property_details.get('baths', 'N/A')}")
    print(f"Year Built: {property_details.get('year_built', 'N/A')}")
    print(f"Size: {property_details.get('size', 'N/A')} sq ft")
    
    # Market analysis
    market_analysis = insights.get("market_analysis", {})
    if market_analysis:
        print("\nMarket Analysis:")
        if "avg_sold_price" in market_analysis:
            print(f"Average Sold Price: ${market_analysis['avg_sold_price']:,.2f}")
        if "avg_listing_price" in market_analysis:
            print(f"Average Listing Price: ${market_analysis['avg_listing_price']:,.2f}")
    
    # Interactive chat loop
    print("\n=== AI Chat Mode ===")
    print("Ask questions about the property or type 'exit' to quit.")
    
    while True:
        user_query = input("\nYour question: ")
        if user_query.lower() in ["exit", "quit", "q"]:
            break
        
        ai_response = assistant.get_ai_response(user_query)
        print("\nAI Response:")
        print(ai_response)
    
    print("\nThank you for using Property AI Assistant!")

if __name__ == "__main__":
    main() 