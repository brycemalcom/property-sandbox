from acumidata_client import AcumidataClient

client = AcumidataClient(environment="prod")

addresses = [
    ("1014 HOLFORD DR", "frisco", "tx", "75034"),
    ("102 COACHMAN PLACE", "georgetown", "ky", "21209"),
    ("10720 LEESA DR", "mckinney", "tx", "75072"),
]

for address, city, state, zip_code in addresses:
    print(f"\nTesting: {address}, {city}, {state} {zip_code}")
    result = client.get_qvm_simple(address, city, state, zip_code)
    print("Full API Response:")
    print(result)
    # Try to extract the QVM value from the response
    basic_data = result.get("basic_data", {})
    qvm_value = basic_data.get("qvm_value") if basic_data else None
    if qvm_value:
        print(f"QVM Value: {qvm_value}")
    else:
        print("QVM Value not found in response.") 