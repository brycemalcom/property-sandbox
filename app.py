import streamlit as st
from acumidata_client import AcumidataClient
import pandas as pd
import io
import hashlib
import json
import os

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Simple user database (in production, use a real database)
USER_DB_FILE = "users.json"

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f)

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def login_form():
    """Display login form"""
    st.title("🔐 Login to Property Dashboard")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            users = load_users()
            if username in users and verify_password(password, users[username]['password']):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.markdown("---")
    st.subheader("Don't have an account?")
    if st.button("Sign Up"):
        st.session_state.show_signup = True
        st.rerun()

def signup_form():
    """Display signup form"""
    st.title("📝 Create Account")
    
    with st.form("signup_form"):
        username = st.text_input("Choose Username")
        email = st.text_input("Email")
        password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        signup_button = st.form_submit_button("Create Account")
        
        if signup_button:
            if not username or not email or not password:
                st.error("Please fill in all fields")
            elif password != confirm_password:
                st.error("Passwords don't match")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                users = load_users()
                if username in users:
                    st.error("Username already exists")
                else:
                    users[username] = {
                        'email': email,
                        'password': hash_password(password)
                    }
                    save_users(users)
                    st.success("Account created successfully! Please login.")
                    st.session_state.show_signup = False
                    st.rerun()
    
    if st.button("Back to Login"):
        st.session_state.show_signup = False
        st.rerun()

def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.username = None
    if 'show_signup' in st.session_state:
        del st.session_state.show_signup
    st.rerun()

# Authentication check
if not st.session_state.authenticated:
    if 'show_signup' in st.session_state and st.session_state.show_signup:
        signup_form()
    else:
        login_form()
    st.stop()

# Main app (only runs if authenticated)

st.set_page_config(page_title="Property Valuation Dashboard", layout="centered")
st.markdown("""
<style>
.big-metric {
    font-size: 2.5rem;
    font-weight: bold;
    color: #2E8B57;
    margin-bottom: 0.5rem;
}
.metric-label {
    font-size: 1.1rem;
    color: #888;
    margin-bottom: 0.2rem;
}
.card {
    background: #f8f9fa;
    border-radius: 1rem;
    padding: 2rem 1.5rem 1.5rem 1.5rem;
    box-shadow: 0 2px 8px rgba(44,62,80,0.07);
    margin-bottom: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# Header with logout
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🏠 Property Valuation Dashboard")
    st.write(f"Welcome, {st.session_state.username}!")
with col2:
    st.write("")  # Add some spacing
    if st.button("Logout", type="secondary"):
        logout()

st.write("Enter a property address to get the latest valuation and comparables.")

# Option to upload a CSV file
uploaded_file = st.file_uploader("Upload a CSV file with columns: address, city, state, zip", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    # Normalize column names: lowercase and strip spaces
    df.columns = [col.strip().lower() for col in df.columns]
    st.write("Uploaded CSV:")
    st.dataframe(df)

    if st.button("Process CSV"):
        client = AcumidataClient(environment="prod")
        progress_bar = st.progress(0)
        total_rows = len(df)

        for index, row in df.iterrows():
            address = row['address']
            city = row['city']
            state = row['state']
            zip_code = str(row['zip'])

            result = client.get_property_valuation(address, city, state, zip_code)
            details = result.get("Details", {})
            if not isinstance(details, dict):
                estimated_value = None
                confidence_score = None
                range_low = None
                range_high = None
            else:
                property_valuation = details.get("PropertyValuation", {})
                estimated_value = property_valuation.get("EstimatedValue")
                confidence_score = property_valuation.get("ConfidenceScore")
                range_low = property_valuation.get("ValuationRangeLow")
                range_high = property_valuation.get("ValuationRangeHigh")

            df.at[index, 'EstimatedValue'] = estimated_value
            df.at[index, 'ValuationRangeLow'] = range_low
            df.at[index, 'ValuationRangeHigh'] = range_high
            df.at[index, 'ConfidenceScore'] = confidence_score

            progress_bar.progress((index + 1) / total_rows)

        st.write("Enriched CSV:")
        st.dataframe(df)

        # Provide a download link for the enriched CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download Enriched CSV",
            data=csv,
            file_name="enriched_property_data.csv",
            mime="text/csv"
        )

with st.form("lookup_form"):
    address = st.text_input("Street Address", "531 NE Beck Rd")
    city = st.text_input("City", "Belfair")
    state = st.text_input("State", "WA")
    zip_code = st.text_input("Zip Code", "98528")
    submitted = st.form_submit_button("Get Valuation")

if submitted:
    with st.spinner("Fetching property data..."):
        client = AcumidataClient(environment="prod")
        result = client.get_property_valuation(address, city, state, zip_code)
        
        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            details = result.get("Details", {})
            property_valuation = details.get("PropertyValuation", {})
            comps = details.get("ComparablePropertyListings", {}).get("Comparables", [])

            estimated_value = property_valuation.get("EstimatedValue")
            summary = details.get("PropertySummary", {})
            
            # PropertyBasics is nested inside PropertyDetails
            property_details = details.get("PropertyDetails", {})
            basics = property_details.get("PropertyBasics", {})
            
            # Get year built from PropertyBasics
            year_built_actual = basics.get("YearBuiltActual") if basics else None
            year_built_summary = summary.get("YearBuilt") if summary else None
            year_built_valuation = property_valuation.get("YearBuilt") if property_valuation else None
            
            # Use the first available value and convert to string
            if year_built_actual is not None:
                year_built = str(year_built_actual)
            elif year_built_summary is not None:
                year_built = str(year_built_summary)
            elif year_built_valuation is not None:
                year_built = str(year_built_valuation)
            else:
                year_built = "N/A"
                
            beds = summary.get("Bedrooms", "N/A")
            baths = summary.get("FullBaths", "N/A")

            # Display property details
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Property Details</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="big-metric">{address}, {city}, {state} {zip_code}</div>', unsafe_allow_html=True)
            if estimated_value:
                st.markdown(f'<div class="big-metric">Estimated Value: ${estimated_value:,.2f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Beds", value=beds)
            with col2:
                st.metric(label="Baths", value=baths)
            with col3:
                st.metric(label="Year Built", value=year_built)

            st.markdown("---")
            st.subheader("Market Analysis 📊")
            
            # Get valuation range from PropertyValuation (not from comparable sales)
            valuation_low = property_valuation.get("ValuationRangeLow")
            valuation_high = property_valuation.get("ValuationRangeHigh")
            
            if comps:
                # Calculate average price from comparables
                prices = [float(prop.get("Price", 0)) for prop in comps if prop.get("Price")]
                if prices:
                    avg_price = sum(prices) / len(prices)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Average Price", value=f"${avg_price:,.0f}")
                    with col2:
                        if valuation_low:
                            st.metric(label="Valuation Low", value=f"${valuation_low:,.0f}")
                        else:
                            st.metric(label="Valuation Low", value="N/A")
                    with col3:
                        if valuation_high:
                            st.metric(label="Valuation High", value=f"${valuation_high:,.0f}")
                        else:
                            st.metric(label="Valuation High", value="N/A")

                st.markdown("---")
                st.subheader("Recent Comparable Sales 🏡")
                comp_data = [{
                    "Address": f"{comp.get('Address', 'N/A')}, {comp.get('City', 'N/A')}, {comp.get('State', 'N/A')} {comp.get('Zip', 'N/A')}",
                    "Price": f"${float(comp.get('Price', 0)):,.0f}",
                    "Beds": comp.get("Bedrooms", "-"),
                    "Baths": comp.get("Baths", "-"),
                    "Sqft": comp.get("BuildingSqft", "-"),
                    "Year Built": comp.get("YearBuilt", "-"),
                    "Distance": f"{comp.get('Distance', '-')} mi"
                } for comp in comps[:5]]
                df = pd.DataFrame(comp_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No comparable properties found.")

            # Collapsible JSON/meta data section (only at the bottom)
            with st.expander("Show Full JSON Response"):
                st.json(result)

def get_property_data(address, city, state, zip_code):
    client = AcumidataClient(environment="prod")
    result = client.get_property_valuation(address, city, state, zip_code)
    if "error" in result:
        return None, result["error"]
    try:
        details = result.get("Details", {})
        property_valuation = details.get("PropertyValuation", {})
        estimated_value = property_valuation.get("EstimatedValue")
        confidence_score = property_valuation.get("ConfidenceScore")
        range_low = property_valuation.get("ValuationRangeLow")
        range_high = property_valuation.get("ValuationRangeHigh")
        comps = details.get("ComparablePropertyListings", {}).get("Comparables", [])
        return {
            "estimated_value": estimated_value,
            "confidence_score": confidence_score,
            "range_low": range_low,
            "range_high": range_high,
            "comparables": comps
        }, None
    except Exception as e:
        return None, str(e) 