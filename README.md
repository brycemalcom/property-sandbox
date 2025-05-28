# Acumidata API Client

A clean, simple Python client for interacting with the Acumidata API.

## Features

- Proper authentication flow using username/password to obtain API key
- Property data retrieval using the Comps/advantage endpoint
- Extraction of key property details and market analysis
- Support for both UAT and production environments

## Setup

1. Install the required dependencies:

```bash
pip install requests python-dotenv
```

2. Create a `.env` file with your Acumidata credentials:

```
ACUMIDATA_USERNAME=your_username
ACUMIDATA_PASSWORD=your_password
```

## Usage

The main client is in `acumidata_api_client.py`. You can run it directly to see a demo:

```bash
python acumidata_api_client.py
```

### Using the client in your code

```python
from acumidata_api_client import AcumidataApiClient

# Create client (defaults to UAT environment)
client = AcumidataApiClient()

# Get property data
property_data = client.get_property_data(
    street_address="2555 N Pearl St",
    city="Dallas",
    state="TX",
    zip_code="75201"
)

# Extract key details
property_details = client.extract_property_details(property_data)

# Access property information
if "property" in property_details:
    address = property_details["property"]["address"]
    beds = property_details["property"]["beds"]
    baths = property_details["property"]["baths"]
    
# Access market analysis
if "market_analysis" in property_details:
    avg_price = property_details["market_analysis"]["avg_price"]
    num_comps = property_details["market_analysis"]["num_comps"]
```

## Authentication Flow

The client handles authentication automatically:

1. It first attempts to log in using the provided username and password
2. It extracts the API key from the login response
3. It uses this API key as a Bearer token for subsequent API requests

If authentication fails, the client will return an error dictionary with details.

## API Endpoints Used

- `/api/Account/login` - For authentication
- `/api/Comps/advantage` - For property data retrieval

## Response Structure

The raw API response contains:

- `metadata` - Request information
- `mlsData` - Property details from MLS
- `titleData` - Property title information
- `searchLists` - Comparable properties (Sold, Pending, Active)

The `extract_property_details` method processes this data into a more usable format. 