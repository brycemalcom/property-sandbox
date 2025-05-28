from acumidata_client import AcumidataClient
import json

client = AcumidataClient(environment="prod")

addresses = [
    ("1014 HOLFORD DR", "frisco", "tx", "75034"),
    ("102 COACHMAN PLACE", "georgetown", "ky", "21209"),
    ("10720 LEESA DR", "mckinney", "tx", "75072"),
]

endpoints = [
    ("advantage", "api/Valuation/advantage", ["streetAddress", "zip"]),
    ("simple", "api/Valuation/simple", ["streetAddress", "zip"]),
    ("ranged", "api/Valuation/ranged", ["streetAddress", "zip"]),
    ("estimate", "api/Valuation/estimate", ["streetAddress", "zip"]),  # skipping pcid for now
    ("qvmsimple", "api/Valuation/qvmsimple", ["streetAddress", "zip"]),
    ("collateral", "api/Valuation/collateral", ["streetAddress", "zip"]),
]

for address, city, state, zip_code in addresses:
    print(f"\n=== Testing Address: {address}, {city}, {state} {zip_code} ===")
    for name, endpoint, params_list in endpoints:
        params = {"streetAddress": address, "zip": zip_code}
        print(f"\nEndpoint: /{endpoint}")
        result = client._make_request(endpoint, params)
        if "error" in result:
            print(f"Status: ERROR - {result['error']}")
        else:
            # Try to extract a main value if present
            val = None
            if "valuation" in result:
                val = result["valuation"].get("estimated_value")
            details = result.get("Details")
            if isinstance(details, dict) and "PropertyValuation" in details:
                val = details["PropertyValuation"].get("EstimatedValue")
            print(f"Status: SUCCESS")
            if val:
                print(f"Estimated Value: {val}")
            else:
                print("Estimated Value: Not found in response.")
        print("Full JSON Response:")
        print(json.dumps(result, indent=2)) 