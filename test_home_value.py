from acumidata_client import AcumidataClient

# Create the client for PRODUCTION environment
client = AcumidataClient(environment="prod")

# Debug: print first 4 characters of the loaded API key
print("Loaded API Key (first 4 chars):", client.api_key[:4])

# Sample address
address = "531 NE Beck Rd"
city = "Belfair"
state = "WA"
zip_code = "98528"

# Call the API
result = client.get_property_valuation(address, city, state, zip_code)

print("\nFull API Response:")
print(result)

# Extract and print the estimated value and other details
try:
    details = result.get("Details", {})
    property_valuation = details.get("PropertyValuation", {})
    estimated_value = property_valuation.get("EstimatedValue")
    confidence_score = property_valuation.get("ConfidenceScore")
    range_low = property_valuation.get("ValuationRangeLow")
    range_high = property_valuation.get("ValuationRangeHigh")

    print("\n--- Property Valuation Details ---")
    if estimated_value:
        print(f"Estimated Home Value: ${estimated_value:,.2f}")
    if confidence_score is not None:
        print(f"Confidence Score: {confidence_score}")
    if range_low is not None and range_high is not None:
        print(f"Valuation Range: ${range_low:,.0f} - ${range_high:,.0f}")

    # Print first 3 comparable properties (address and price)
    comps = details.get("ComparablePropertyListings", {}).get("Comparables", [])
    if comps:
        print("\nTop 3 Comparable Properties:")
        for comp in comps[:3]:
            addr = comp.get("Address", "N/A")
            price = comp.get("Price", "N/A")
            print(f"- {addr}: ${price:,.0f}")
    else:
        print("No comparable properties found.")
except Exception as e:
    print(f"\nError extracting property details: {str(e)}") 