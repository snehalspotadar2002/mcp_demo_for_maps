#!/usr/bin/env python3
"""MCP Server for finding nearby restaurants using OpenStreetMap data."""

import json
import asyncio
import logging
from typing import Any
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("restaurant-mcp-server")

# Initialize MCP server
server = Server("restaurant-finder")

# Nominatim API for geocoding
NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
# Overpass API for finding restaurants
OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter"

# Tool definitions
TOOLS = [
    Tool(
        name="find_restaurants_by_location",
        description="Find nearby restaurants given latitude and longitude coordinates",
        inputSchema={
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude coordinate"
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude coordinate"
                },
                "radius": {
                    "type": "integer",
                    "description": "Search radius in meters (default: 1000)",
                    "default": 1000
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of restaurants to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["latitude", "longitude"]
        }
    ),
    Tool(
        name="find_restaurants_by_address",
        description="Find nearby restaurants given an address or city name",
        inputSchema={
            "type": "object",
            "properties": {
                "address": {
                    "type": "string",
                    "description": "Address or city name to search for"
                },
                "radius": {
                    "type": "integer",
                    "description": "Search radius in meters (default: 1000)",
                    "default": 1000
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of restaurants to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["address"]
        }
    ),
    Tool(
        name="get_restaurant_details",
        description="Get detailed information about a specific restaurant",
        inputSchema={
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude of the restaurant"
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude of the restaurant"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the restaurant"
                }
            },
            "required": ["latitude", "longitude", "name"]
        }
    ),
    Tool(
        name="search_restaurants_by_query",
        description="Search for restaurants by cuisine type or keyword in a given location",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Cuisine type or keyword (e.g., 'italian', 'pizza', 'indian')"
                },
                "address": {
                    "type": "string",
                    "description": "Address or city name to search in"
                },
                "radius": {
                    "type": "integer",
                    "description": "Search radius in meters (default: 1000)",
                    "default": 1000
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of restaurants to return (default: 10)",
                    "default": 10
                }
            },
            "required": ["query", "address"]
        }
    )
]


async def geocode_address(address: str) -> dict[str, Any]:
    """Convert address to coordinates using Nominatim."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NOMINATIM_BASE_URL}/search",
                params={
                    "q": address,
                    "format": "json",
                    "limit": 1
                },
                timeout=10.0,
                headers={"User-Agent": "mcp-restaurant-finder"}
            )
            response.raise_for_status()
            data = response.json()
            
            if data:
                result = data[0]
                return {
                    "latitude": float(result["lat"]),
                    "longitude": float(result["lon"]),
                    "display_name": result.get("display_name", "")
                }
            return {}
    except Exception as e:
        logger.error(f"Geocoding error: {e}")
        return {}


async def find_restaurants(latitude: float, longitude: float, radius: int = 1000, limit: int = 10) -> list[dict[str, Any]]:
    """Find restaurants using Overpass API with fallback amenities."""
    import math
    
    try:
        # Convert radius from meters to approximate degrees
        lat_radius = radius / 111000
        lon_radius = radius / (111000 * abs(math.cos(math.radians(latitude))))
        
        bbox = f"{latitude - lat_radius},{longitude - lon_radius},{latitude + lat_radius},{longitude + lon_radius}"
        
        # Extended query to include restaurants, cafes, pubs, and fast food
        overpass_query = f"""[out:json][timeout:30];
(
  node["amenity"="restaurant"]({bbox});
  way["amenity"="restaurant"]({bbox});
  relation["amenity"="restaurant"]({bbox});
  node["amenity"="cafe"]({bbox});
  way["amenity"="cafe"]({bbox});
  node["amenity"="pub"]({bbox});
  way["amenity"="pub"]({bbox});
  node["amenity"="fast_food"]({bbox});
  way["amenity"="fast_food"]({bbox});
);
out center;"""
        
        async with httpx.AsyncClient(timeout=40.0) as client:
            for attempt in range(2):
                try:
                    response = await client.post(
                        OVERPASS_BASE_URL,
                        data=overpass_query,
                        timeout=40.0,
                        headers={"User-Agent": "mcp-restaurant-finder"}
                    )
                    response.raise_for_status()
                    data = response.json()
                    break
                except Exception as e:
                    if attempt == 0:
                        logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying...")
                        await asyncio.sleep(2)
                    else:
                        logger.error(f"Final attempt failed: {e}")
                        return []
        
        restaurants = []
        amenity_map = {
            "restaurant": "Restaurant",
            "cafe": "Café",
            "pub": "Pub",
            "fast_food": "Fast Food"
        }
        
        for element in data.get("elements", []):
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
                amenity_type = tags.get("amenity", "restaurant")
                
                restaurant = {
                    "id": element.get("id"),
                    "type": element.get("type"),
                    "name": tags.get("name", f"Unnamed {amenity_map.get(amenity_type, 'Place')}"),
                    "latitude": lat,
                    "longitude": lon,
                    "amenity": amenity_map.get(amenity_type, amenity_type),
                    "cuisine": tags.get("cuisine", "Not specified"),
                    "phone": tags.get("phone", "Not available"),
                    "website": tags.get("website", tags.get("contact:website", "Not available")),
                    "opening_hours": tags.get("opening_hours", "Not specified"),
                }
                restaurants.append(restaurant)
        
        # Sort by name and return limited results
        restaurants = sorted(restaurants, key=lambda x: x.get("name", ""))[:limit]
        logger.info(f"Found {len(restaurants)} places from Overpass API")
        return restaurants
    
    except Exception as e:
        logger.error(f"Error fetching restaurants: {e}")
        import traceback
        traceback.print_exc()
        return []



@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return TOOLS


@server.call_tool()
async def handle_tool_call(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name == "find_restaurants_by_location":
            latitude = arguments.get("latitude")
            longitude = arguments.get("longitude")
            radius = arguments.get("radius", 1000)
            limit = arguments.get("limit", 10)
            
            restaurants = await find_restaurants(latitude, longitude, radius, limit)
            
            if not restaurants:
                result = "No restaurants found in the specified area."
            else:
                result = f"Found {len(restaurants)} restaurants:\n\n"
                for i, restaurant in enumerate(restaurants, 1):
                    result += f"{i}. {restaurant['name']}\n"
                    result += f"   Cuisine: {restaurant['cuisine']}\n"
                    result += f"   Coordinates: {restaurant['latitude']}, {restaurant['longitude']}\n"
                    result += f"   Phone: {restaurant['phone']}\n"
                    result += f"   Website: {restaurant['website']}\n"
                    result += f"   Hours: {restaurant['opening_hours']}\n"
                    result += f"   Rating: {restaurant['rating']}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "find_restaurants_by_address":
            address = arguments.get("address")
            radius = arguments.get("radius", 1000)
            limit = arguments.get("limit", 10)
            
            # First geocode the address
            location = await geocode_address(address)
            if not location:
                return [TextContent(type="text", text=f"Could not find coordinates for address: {address}")]
            
            restaurants = await find_restaurants(
                location["latitude"],
                location["longitude"],
                radius,
                limit
            )
            
            if not restaurants:
                result = f"No restaurants found near {location.get('display_name', address)}."
            else:
                result = f"Found {len(restaurants)} restaurants near {location.get('display_name', address)}:\n\n"
                for i, restaurant in enumerate(restaurants, 1):
                    result += f"{i}. {restaurant['name']}\n"
                    result += f"   Cuisine: {restaurant['cuisine']}\n"
                    result += f"   Coordinates: {restaurant['latitude']}, {restaurant['longitude']}\n"
                    result += f"   Phone: {restaurant['phone']}\n"
                    result += f"   Website: {restaurant['website']}\n"
                    result += f"   Hours: {restaurant['opening_hours']}\n"
                    result += f"   Rating: {restaurant['rating']}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_restaurant_details":
            latitude = arguments.get("latitude")
            longitude = arguments.get("longitude")
            name = arguments.get("name")
            
            # Use Nominatim reverse geocoding to get detailed info
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{NOMINATIM_BASE_URL}/reverse",
                        params={
                            "format": "json",
                            "lat": latitude,
                            "lon": longitude,
                            "zoom": 18,
                            "addressdetails": 1
                        },
                        timeout=10.0,
                        headers={"User-Agent": "mcp-restaurant-finder"}
                    )
                    response.raise_for_status()
                    data = response.json()
                
                address = data.get("address", {})
                result = f"Restaurant: {name}\n"
                result += f"Coordinates: {latitude}, {longitude}\n"
                result += f"Address: {data.get('display_name', 'Not available')}\n"
                result += f"City: {address.get('city', address.get('town', 'N/A'))}\n"
                result += f"Country: {address.get('country', 'N/A')}\n"
                
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"Error getting restaurant details: {e}")
                return [TextContent(type="text", text=f"Error retrieving details for {name}")]
        
        elif name == "search_restaurants_by_query":
            query = arguments.get("query", "").lower()
            address = arguments.get("address")
            radius = arguments.get("radius", 1000)
            limit = arguments.get("limit", 10)
            
            # Geocode the address
            location = await geocode_address(address)
            if not location:
                return [TextContent(type="text", text=f"Could not find coordinates for address: {address}")]
            
            # Get all restaurants in the area
            restaurants = await find_restaurants(
                location["latitude"],
                location["longitude"],
                radius,
                limit * 2  # Fetch more to account for filtering
            )
            
            # Filter by query (cuisine or name)
            filtered = []
            for restaurant in restaurants:
                cuisine = restaurant.get("cuisine", "").lower()
                name = restaurant.get("name", "").lower()
                if query in cuisine or query in name:
                    filtered.append(restaurant)
            
            # Limit results
            filtered = filtered[:limit]
            
            if not filtered:
                result = f"No {query} restaurants found near {location.get('display_name', address)}."
            else:
                result = f"Found {len(filtered)} {query} restaurants near {location.get('display_name', address)}:\n\n"
                for i, restaurant in enumerate(filtered, 1):
                    result += f"{i}. {restaurant['name']}\n"
                    result += f"   Cuisine: {restaurant['cuisine']}\n"
                    result += f"   Coordinates: {restaurant['latitude']}, {restaurant['longitude']}\n"
                    result += f"   Phone: {restaurant['phone']}\n"
                    result += f"   Website: {restaurant['website']}\n"
                    result += f"   Hours: {restaurant['opening_hours']}\n\n"
            
            return [TextContent(type="text", text=result)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error(f"Tool call error: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    await server.run_stdio()


if __name__ == "__main__":
    asyncio.run(main())
