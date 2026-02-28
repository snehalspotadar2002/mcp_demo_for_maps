import streamlit as st
import asyncio
import httpx
from typing import Any

NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter"

# Page configuration
st.set_page_config(
    page_title="Restaurant Finder",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background-color: #1a1a2e;
        color: #ffffff;
    }
    
    .main-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 10px;
    }
    
    .main-header h1 {
        font-size: 48px;
        font-weight: 700;
        margin: 0;
    }
    
    .subtitle {
        color: #b0b0b0;
        font-size: 16px;
        margin-bottom: 30px;
    }
    
    .nav-tabs {
        display: flex;
        gap: 0;
        margin-bottom: 30px;
        border-bottom: 1px solid #404040;
    }
    
    .nav-tab {
        padding: 12px 20px;
        cursor: pointer;
        border: none;
        background: none;
        color: #888;
        font-size: 14px;
        border-bottom: 3px solid transparent;
        transition: all 0.3s;
    }
    
    .nav-tab.active {
        color: #ff5555;
        border-bottom-color: #ff5555;
    }
    
    .form-section {
        background: rgba(255, 255, 255, 0.02);
        padding: 30px;
        border-radius: 8px;
        margin-top: 20px;
    }
    
    .form-title {
        font-size: 28px;
        font-weight: 600;
        margin-bottom: 20px;
    }
    
    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;
    }
    
    .form-group {
        display: flex;
        flex-direction: column;
    }
    
    .form-label {
        font-size: 14px;
        color: #b0b0b0;
        margin-bottom: 8px;
        font-weight: 500;
    }
    
    .stTextInput input, .stNumberInput input {
        background-color: #2a2a3e !important;
        color: #ffffff !important;
        border: 1px solid #404040 !important;
        border-radius: 4px !important;
        padding: 10px !important;
    }
    
    .search-btn {
        background-color: #ff5555;
        color: white;
        padding: 12px 30px;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        margin-top: 20px;
        transition: all 0.3s;
    }
    
    .search-btn:hover {
        background-color: #ff6666;
    }
    
    .results-section {
        margin-top: 30px;
    }
    
    .results-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 15px;
    }
    
    .restaurant-card {
        background: rgba(255, 255, 255, 0.04);
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 10px;
        border-left: 3px solid #ff5555;
    }
    
    .restaurant-name {
        font-size: 16px;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }
    
    .restaurant-info {
        font-size: 13px;
        color: #a0a0a0;
        line-height: 1.6;
    }
    
    .icon {
        font-size: 32px;
    }
</style>
""", unsafe_allow_html=True)


async def geocode_address(address: str) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params={"q": address, "format": "json", "limit": 1},
                timeout=10.0,
                headers={"User-Agent": "streamlit-restaurant-finder"},
            )
            response.raise_for_status()
            data = response.json()
            if data:
                r = data[0]
                return {"latitude": float(r["lat"]), "longitude": float(r["lon"]), "display_name": r.get("display_name", "")}
            return {}
    except Exception as e:
        return {"error": str(e)}


async def find_restaurants(latitude: float, longitude: float, radius: int = 1000, limit: int = 10):
    lat_radius = radius / 111000
    lon_radius = lat_radius
    bbox = f"{latitude - lat_radius},{longitude - lon_radius},{latitude + lat_radius},{longitude + lon_radius}"

    overpass_query = f"""
    [bbox:{bbox}][out:json];
    (
        node["amenity"="restaurant"];
        way["amenity"="restaurant"];
        relation["amenity"="restaurant"];
    );
    out center;
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(OVERPASS_BASE_URL, data=overpass_query, timeout=30.0, headers={"User-Agent": "streamlit-restaurant-finder"})
            response.raise_for_status()
            data = response.json()

        restaurants = []
        for element in data.get("elements", [])[:limit]:
            if element.get("type") == "node":
                lat = element.get("lat")
                lon = element.get("lon")
            elif element.get("type") in ["way", "relation"]:
                center = element.get("center", {})
                lat = center.get("lat")
                lon = center.get("lon")
            else:
                continue

            if lat and lon:
                tags = element.get("tags", {})
                restaurants.append({
                    "id": element.get("id"),
                    "name": tags.get("name", "Unknown Restaurant"),
                    "latitude": lat,
                    "longitude": lon,
                    "cuisine": tags.get("cuisine", "Not specified"),
                    "phone": tags.get("phone", "Not available"),
                    "website": tags.get("website", tags.get("contact:website", "Not available")),
                    "opening_hours": tags.get("opening_hours", "Not specified"),
                })

        return restaurants
    except Exception as e:
        return [{"error": str(e)}]


def run_async(coro):
    return asyncio.run(coro)


def display_restaurant_card(restaurant):
    """Display a single restaurant as a card"""
    col1, col2 = st.columns([1, 3])
    with col1:
        amenity = restaurant.get('amenity', 'Restaurant')
        emoji = {'Restaurant': '🍽️', 'Café': '☕', 'Pub': '🍺', 'Fast Food': '🍔'}.get(amenity, '🍽️')
        st.markdown(emoji, unsafe_allow_html=True)
    with col2:
        st.markdown(f"### {restaurant.get('name', 'Unknown')}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**Type:** {restaurant.get('amenity', 'Restaurant')}")
            st.markdown(f"**Cuisine:** {restaurant.get('cuisine', 'Not specified')}")
            st.markdown(f"**Phone:** {restaurant.get('phone', 'Not available')}")
        with col_b:
            st.markdown(f"**Lat/Lon:** {restaurant.get('latitude'):.4f}, {restaurant.get('longitude'):.4f}")
            if restaurant.get('website') and restaurant.get('website') != 'Not available':
                st.markdown(f"**Website:** [{restaurant.get('website')}]({restaurant.get('website')})")
            st.markdown(f"**Hours:** {restaurant.get('opening_hours', 'Not specified')}")
    st.divider()



def main():
    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
        <div style="font-size: 48px;">🍽️</div>
        <h1 style="margin: 0; font-size: 48px; font-weight: 700;">Restaurant Finder</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("Find restaurants near you using OpenStreetMap data", unsafe_allow_html=True)
    
    # Navigation tabs (simulated)
    tab1, tab2, tab3 = st.tabs(["🔍 Find Nearby", "🔎 Search", "⭐ Recommendations"])
    
    with tab1:
        st.markdown("### Find Nearby Restaurants")
        
        col1, col2 = st.columns(2)
        
        with col1:
            location = st.text_input("Location", value="Hitech City Hyderabad", key="location_input")
        
        with col2:
            cuisine = st.text_input("Cuisine Type (optional)", value="Indian Andhra style", key="cuisine_input")
        
        radius = st.slider("Search Radius (meters)", 500, 5000, 1000)
        
        col_search, col_empty = st.columns([1, 3])
        with col_search:
            search_btn = st.button("🔍 Find Restaurants", use_container_width=True)
        
        if search_btn:
            with st.spinner("🔍 Geocoding location..."):
                loc = run_async(geocode_address(location))
            
            if not loc or loc.get("error"):
                st.error(f"❌ Could not find location: {location}")
                return
            
            st.success(f"✅ Found location: {loc.get('display_name', location)}")
            
            with st.spinner("🔍 Searching for nearby places..."):
                restaurants = run_async(find_restaurants(loc["latitude"], loc["longitude"], radius=radius, limit=30))
            
            if restaurants:
                # Filter by cuisine if provided
                if cuisine and cuisine.strip():
                    filtered = [r for r in restaurants if cuisine.lower() in r.get("cuisine", "").lower() or cuisine.lower() in r.get("name", "").lower()]
                else:
                    filtered = restaurants
                
                if filtered:
                    st.markdown(f"### 🎯 Found {len(filtered)} Places")
                    for r in filtered[:15]:
                        display_restaurant_card(r)
                else:
                    st.info(f"No {cuisine} places found. Showing all available places:")
                    for r in restaurants[:15]:
                        display_restaurant_card(r)
            else:
                st.info("❌ No places found in this area. This location may have limited data in OpenStreetMap. Try a different location or increase the search radius.")
    
    with tab2:
        st.markdown("### Search by Cuisine")
        
        search_query = st.text_input("Cuisine or restaurant type (e.g., italian, pizza, burger)", value="italian")
        search_location = st.text_input("Location", value="Mumbai")
        search_radius = st.slider("Search Radius (meters)", 500, 5000, 1000, key="search_radius")
        
        if st.button("🔎 Search", use_container_width=True):
            with st.spinner("🔍 Geocoding location..."):
                loc = run_async(geocode_address(search_location))
            
            if not loc or loc.get("error"):
                st.error(f"❌ Could not find location: {search_location}")
                return
            
            with st.spinner(f"🔍 Searching for {search_query} places..."):
                restaurants = run_async(find_restaurants(loc["latitude"], loc["longitude"], radius=search_radius, limit=30))
            
            if restaurants and not restaurants[0].get("error"):
                filtered = [r for r in restaurants if search_query.lower() in r.get("cuisine", "").lower() or search_query.lower() in r.get("name", "").lower()]
                
                if filtered:
                    st.markdown(f"### 🎯 Found {len(filtered)} {search_query.title()} Places")
                    for r in filtered[:15]:
                        display_restaurant_card(r)
                else:
                    st.info(f"No {search_query} places found in {search_location}. Showing all available places:")
                    for r in restaurants[:10]:
                        display_restaurant_card(r)
            else:
                st.info(f"No places found in {search_location}. The area may have limited data in OpenStreetMap.")
    
    with tab3:
        st.markdown("### Popular Cuisines")
        
        col1, col2, col3 = st.columns(3)
        
        popular = ["Indian", "Italian", "Chinese", "Mexican", "Thai", "Japanese"]
        
        # Show popular cuisine buttons
        for i, cuisine_type in enumerate(popular):
            col = [col1, col2, col3][i % 3]
            with col:
                if st.button(f"🍲 {cuisine_type}", key=f"cuisine_{cuisine_type}", use_container_width=True):
                    st.session_state.selected_cuisine = cuisine_type
        
        if "selected_cuisine" in st.session_state:
            rec_location = st.text_input("Enter location for recommendations", value="Delhi")
            if st.button("Get Recommendations"):
                with st.spinner(f"🔍 Finding {st.session_state.selected_cuisine} places..."):
                    loc = run_async(geocode_address(rec_location))
                    if loc and not loc.get("error"):
                        restaurants = run_async(find_restaurants(loc["latitude"], loc["longitude"], radius=2000, limit=30))
                        if restaurants:
                            filtered = [r for r in restaurants if st.session_state.selected_cuisine.lower() in r.get("cuisine", "").lower()]
                            if filtered:
                                st.markdown(f"### ⭐ Best {st.session_state.selected_cuisine} Places in {rec_location}")
                                for r in filtered[:10]:
                                    display_restaurant_card(r)
                            else:
                                st.info(f"No specific {st.session_state.selected_cuisine} places found. Showing all available places in {rec_location}:")
                                for r in restaurants[:10]:
                                    display_restaurant_card(r)
                        else:
                            st.info(f"No places found in {rec_location}. The area may have limited OpenStreetMap data.")
                    else:
                        st.error(f"Could not find location: {rec_location}")

if __name__ == "__main__":
    main()
