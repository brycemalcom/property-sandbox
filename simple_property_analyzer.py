import os
import json
from dotenv import load_dotenv
import requests
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

class SimplePropertyAnalyzer:
    def __init__(self, environment: str = "uat"):
        """
        Initialize the property analyzer
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
                "Content-Type": "application/json",
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
    
    def analyze_property(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze property data and provide insights
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
                "has_pool": mls_data.get("pool") is not None
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
        
        # Calculate market analysis
        if insights["comparable_properties"]["sold"]:
            sold_prices = [float(prop["price"]) for prop in insights["comparable_properties"]["sold"] if prop["price"]]
            if sold_prices:
                insights["market_analysis"]["avg_sold_price"] = sum(sold_prices) / len(sold_prices)
                insights["market_analysis"]["min_sold_price"] = min(sold_prices)
                insights["market_analysis"]["max_sold_price"] = max(sold_prices)
                
                # Find similar properties (same beds/baths)
                if "beds" in insights["property_details"] and "baths" in insights["property_details"]:
                    target_beds = insights["property_details"]["beds"]
                    target_baths = insights["property_details"]["baths"]
                    
                    similar_properties = [
                        prop for prop in insights["comparable_properties"]["sold"]
                        if prop["beds"] == target_beds and prop["baths"] == target_baths
                    ]
                    
                    if similar_properties:
                        similar_prices = [float(prop["price"]) for prop in similar_properties if prop["price"]]
                        if similar_prices:
                            insights["market_analysis"]["avg_similar_price"] = sum(similar_prices) / len(similar_prices)
        
        return insights

    def generate_human_readable_insights(self, insights: Dict[str, Any]) -> str:
        """
        Generate human-readable insights from the analyzed data
        """
        output = []
        
        # Property details
        property_details = insights.get("property_details", {})
        if property_details:
            output.append("=== PROPERTY DETAILS ===")
            output.append(f"Address: {property_details.get('address', 'N/A')}")
            output.append(f"Beds: {property_details.get('beds', 'N/A')}")
            output.append(f"Baths: {property_details.get('baths', 'N/A')}")
            output.append(f"Year Built: {property_details.get('year_built', 'N/A')}")
            output.append(f"Size: {property_details.get('size', 'N/A')} sq ft")
            output.append(f"Has Pool: {'Yes' if property_details.get('has_pool') else 'No'}")
            output.append("")
        
        # Market analysis
        market_analysis = insights.get("market_analysis", {})
        if market_analysis:
            output.append("=== MARKET ANALYSIS ===")
            if "avg_sold_price" in market_analysis:
                output.append(f"Average Sold Price: ${market_analysis['avg_sold_price']:,.2f}")
            if "min_sold_price" in market_analysis:
                output.append(f"Minimum Sold Price: ${market_analysis['min_sold_price']:,.2f}")
            if "max_sold_price" in market_analysis:
                output.append(f"Maximum Sold Price: ${market_analysis['max_sold_price']:,.2f}")
            if "avg_similar_price" in market_analysis:
                output.append(f"Average Price for Similar Properties: ${market_analysis['avg_similar_price']:,.2f}")
            output.append("")
        
        # Comparable properties
        sold_properties = insights.get("comparable_properties", {}).get("sold", [])
        if sold_properties:
            output.append("=== RECENTLY SOLD COMPARABLE PROPERTIES ===")
            for i, prop in enumerate(sold_properties[:5], 1):  # Show top 5
                output.append(f"Property {i}:")
                output.append(f"  Address: {prop.get('address', 'N/A')}")
                output.append(f"  Price: ${float(prop.get('price', 0)):,.2f}")
                output.append(f"  Beds/Baths: {prop.get('beds', 'N/A')}/{prop.get('baths', 'N/A')}")
                output.append(f"  Size: {prop.get('size', 'N/A')} sq ft")
                output.append(f"  Year Built: {prop.get('year_built', 'N/A')}")
                output.append(f"  Distance: {prop.get('distance', 'N/A')} miles")
                output.append(f"  Days on Market: {prop.get('days_on_market', 'N/A')}")
                output.append("")
        
        # Value insights
        if property_details and market_analysis and "avg_similar_price" in market_analysis:
            output.append("=== VALUE INSIGHTS ===")
            output.append(f"Based on comparable properties with {property_details.get('beds', 'N/A')} beds and {property_details.get('baths', 'N/A')} baths:")
            output.append(f"The estimated market value is around ${market_analysis['avg_similar_price']:,.2f}")
            output.append("")
            
            # Simple recommendations
            output.append("=== RECOMMENDATIONS ===")
            output.append("To potentially increase property value:")
            output.append("1. Consider updating kitchen and bathrooms if they haven't been renovated recently")
            output.append("2. Ensure curb appeal is maximized with landscaping and exterior maintenance")
            output.append("3. If the property doesn't have a pool and many comparable properties do, consider adding one")
            output.append("4. Energy-efficient upgrades can increase value and reduce utility costs")
            output.append("5. Open floor plans are currently desirable in the market")
        
        return "\n".join(output)

def main():
    """
    Main function to demonstrate the SimplePropertyAnalyzer
    """
    print("=== Simple Property Analyzer ===")
    
    # Create analyzer
    analyzer = SimplePropertyAnalyzer()
    
    # Get property details from user
    street_address = input("Enter street address: ")
    city = input("Enter city: ")
    state = input("Enter state (2-letter code): ")
    zip_code = input("Enter ZIP code: ")
    
    # Get property data
    print("\nFetching property data...")
    property_data = analyzer.get_property_data(street_address, city, state, zip_code)
    
    if "error" in property_data:
        print(f"Error: {property_data['error']}")
        return
    
    # Analyze property
    print("Analyzing property data...")
    insights = analyzer.analyze_property(property_data)
    
    # Generate human-readable insights
    print("\n" + "=" * 50)
    print(analyzer.generate_human_readable_insights(insights))
    print("=" * 50)
    
    # Option to save data
    save_option = input("\nWould you like to save the raw property data to a file? (y/n): ")
    if save_option.lower() == 'y':
        filename = f"property_data_{street_address.replace(' ', '_')}_{city}.json"
        with open(filename, 'w') as f:
            json.dump(property_data, f, indent=2)
        print(f"Data saved to {filename}")
    
    print("\nThank you for using Simple Property Analyzer!")

if __name__ == "__main__":
    main() 