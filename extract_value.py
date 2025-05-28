import json

# Load the Belfair property data
with open('belfair_property_data.json') as f:
    data = json.load(f)

# Extract property details
mls_data = data.get('mlsData', {})
address = mls_data.get('address', 'N/A')
city = mls_data.get('city', 'N/A')
state = mls_data.get('state', 'N/A')
zip_code = mls_data.get('zip', 'N/A')
beds = mls_data.get('beds', 'N/A')
baths = mls_data.get('baths', 'N/A')
year_built = mls_data.get('yearBuilt', 'N/A')
size = mls_data.get('size', 'N/A')

print(f"=== Property Details ===")
print(f"Address: {address}, {city}, {state} {zip_code}")
print(f"Beds: {beds}")
print(f"Baths: {baths}")
print(f"Year Built: {year_built}")
print(f"Size: {size} sq ft")
print()

# Extract comparable sold properties
sold_properties = data.get('searchLists', {}).get('Sold', [])
if sold_properties:
    # Calculate average price
    prices = [float(prop.get('price', 0)) for prop in sold_properties if prop.get('price')]
    avg_price = sum(prices) / len(prices) if prices else 0
    
    # Find similar properties (same beds/baths)
    similar_properties = [
        prop for prop in sold_properties
        if prop.get('beds') == beds and prop.get('baths') == baths
    ]
    similar_prices = [float(prop.get('price', 0)) for prop in similar_properties if prop.get('price')]
    avg_similar_price = sum(similar_prices) / len(similar_prices) if similar_prices else 0
    
    print(f"=== Value Estimates ===")
    print(f"Number of comparable sold properties: {len(prices)}")
    print(f"Average price of all comparable properties: ${avg_price:,.2f}")
    
    if similar_prices:
        print(f"Number of similar properties (same beds/baths): {len(similar_prices)}")
        print(f"Average price of similar properties: ${avg_similar_price:,.2f}")
    
    print("\n=== Recent Comparable Sales ===")
    for i, prop in enumerate(sold_properties[:5], 1):
        print(f"Property {i}:")
        print(f"  Address: {prop.get('address', 'N/A')}, {prop.get('city', 'N/A')}, {prop.get('state', 'N/A')} {prop.get('zip', 'N/A')}")
        print(f"  Price: ${float(prop.get('price', 0)):,.2f}")
        print(f"  Beds/Baths: {prop.get('beds', 'N/A')}/{prop.get('baths', 'N/A')}")
        print(f"  Size: {prop.get('size', 'N/A')} sq ft")
        print(f"  Year Built: {prop.get('yearBuilt', 'N/A')}")
        print(f"  Distance: {prop.get('distance', 'N/A')} miles")
        print(f"  Sale Date: {prop.get('statusDate', 'N/A')}")
        print()
else:
    print("No comparable sold properties found.") 