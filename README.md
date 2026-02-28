# Restaurant Finder MCP Server

A Model Context Protocol (MCP) server for finding nearby restaurants using OpenStreetMap data. This project provides both an MCP server and a Streamlit web interface for discovering restaurants.

## Features

### MCP Server
- **Find restaurants by location** - Search restaurants using latitude and longitude coordinates
- **Find restaurants by address** - Search restaurants by providing an address or city name
- **Get restaurant details** - Retrieve detailed information about a specific restaurant
- **Search by cuisine** - Search for restaurants by cuisine type or keyword

### Streamlit Web App
- **Find Nearby** - Search restaurants near a specific location
- **Search by Cuisine** - Find restaurants of a specific cuisine type
- **Recommendations** - Discover popular cuisines in your area

## Installation

1. Clone the repository:
```
bash
git clone <repository-url>
cd mcp_demo_for_maps
```

2. Create a virtual environment (optional but recommended):
```
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the dependencies:
```
bash
pip install -r requirements.txt
```

## Usage

### Running the Streamlit App

```
bash
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`.

### Running the MCP Server

```
bash
python server.py
```

The MCP server runs on stdio and can be integrated with Claude or other MCP-compatible clients.

## API Dependencies

This project uses the following free OpenStreetMap-based APIs:

- **Nominatim** (https://nominatim.openstreetmap.org) - For geocoding addresses to coordinates
- **Overpass API** (https://overpass-api.de) - For finding restaurants and other POIs

**Note:** Please use these APIs responsibly. They are free services maintained by volunteers. The application includes proper User-Agent headers for identification.

## Project Structure

```
.
├── server.py           # MCP Server implementation
├── streamlit_app.py   # Streamlit web interface
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Available Tools

| Tool | Description |
|------|-------------|
| `find_restaurants_by_location` | Find nearby restaurants given latitude and longitude |
| `find_restaurants_by_address` | Find restaurants given an address or city name |
| `get_restaurant_details` | Get detailed information about a specific restaurant |
| `search_restaurants_by_query` | Search restaurants by cuisine type or keyword |

## Tech Stack

- **Python** - Programming language
- **Streamlit** - Web UI framework
- **MCP** - Model Context Protocol for AI integration
- **httpx** - HTTP client for API requests
- **OpenStreetMap** - Map data source (Nominatim, Overpass API)

## License

MIT License
