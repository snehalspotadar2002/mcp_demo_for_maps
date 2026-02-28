# MCP Demo for Maps

## 📌 Project Overview

**MCP Demo for Maps** is a demonstration project that integrates the
Model Context Protocol (MCP) with mapping functionality. This project
showcases how to build and connect tools using MCP architecture for
map-based operations.

------------------------------------------------------------------------

## 🚀 Features

-   MCP server implementation
-   Custom tool integration
-   Map-based data handling
-   Structured request & response flow
-   Error handling and logging

------------------------------------------------------------------------

## 🏗️ Project Structure

    mcp_demo_for_maps/
    │
    ├── server.py              # Main MCP server
    ├── tools/                 # Tool implementations
    ├── config.py              # Configuration settings
    ├── requirements.txt       # Python dependencies
    ├── README.md              # Project documentation
    └── ...

------------------------------------------------------------------------

## ⚙️ Installation

### 1️⃣ Clone the Repository

``` bash
git clone <your-repository-url>
cd mcp_demo_for_maps
```

### 2️⃣ Create Virtual Environment

``` bash
python -m venv .venv
```

Activate it:

**Windows:**

``` bash
.venv\Scripts\activate
```

**Mac/Linux:**

``` bash
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## ▶️ Running the Project

Start the MCP server:

``` bash
python server.py
```

Or using uvicorn:

``` bash
uvicorn server:app --reload
```

------------------------------------------------------------------------

## 🛠️ How It Works

1.  Client sends a request.
2.  MCP server receives the request.
3.  Server processes the query.
4.  Relevant tool is triggered.
5.  Structured response is returned.

------------------------------------------------------------------------

## 🧪 Example Usage

Example request:

``` json
{
  "query": "Show map location for Pune"
}
```

Example response:

``` json
{
  "status": "success",
  "data": {
    "latitude": 18.5204,
    "longitude": 73.8567
  }
}
```

------------------------------------------------------------------------

## 🔐 Environment Variables

Create a `.env` file:

    API_KEY=your_api_key
    PORT=8000

------------------------------------------------------------------------

## 📄 License

This project is for demonstration and educational purposes.
