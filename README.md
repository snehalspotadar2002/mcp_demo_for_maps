MCP Demo for Maps
📌 Project Overview

MCP Demo for Maps is a demonstration project that integrates the Model Context Protocol (MCP) with mapping functionality. This project showcases how to build and connect tools using MCP architecture for map-based operations.

The goal of this demo is to:

Demonstrate MCP server setup

Implement tool integration

Handle map-related queries

Enable structured tool responses

🚀 Features

MCP server implementation

Custom tool integration

Map-based data handling

Structured request & response flow

Error handling and logging

🏗️ Project Structure
mcp_demo_for_maps/
│
├── server.py              # Main MCP server
├── tools/                 # Tool implementations
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── ...

(Update structure if your folder layout is different.)

⚙️ Installation
1️⃣ Clone the Repository
git clone <your-repository-url>
cd mcp_demo_for_maps
2️⃣ Create Virtual Environment
python -m venv .venv

Activate it:

Windows:

.venv\Scripts\activate

Mac/Linux:

source .venv/bin/activate
3️⃣ Install Dependencies
pip install -r requirements.txt
▶️ Running the Project

Start the MCP server:

python server.py

If using uvicorn:

uvicorn server:app --reload
🛠️ How It Works

Client sends a request.

MCP server receives the request.

Server processes the query.

Relevant tool is triggered.

Structured response is returned.

🧪 Example Usage

Example request:

{
  "query": "Show map location for Pune"
}

Example response:

{
  "status": "success",
  "data": {
    "latitude": 18.5204,
    "longitude": 73.8567
  }
}
🐞 Troubleshooting
Import Errors

Make sure:

Virtual environment is activated

Dependencies are installed correctly

Tool Not Found Error

Verify tool is registered correctly

Check naming consistency

📦 Requirements

Python 3.9+

MCP compatible environment

Required packages listed in requirements.txt

🔐 Environment Variables (If Required)

Create a .env file:

API_KEY=your_api_key
PORT=8000
📄 License

This project is for demonstration and educational purposes.
