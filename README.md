# 🚀 Newsletter Agent

An AI-powered newsletter generator that analyzes GitHub repositories and creates comprehensive technical newsletters with architecture diagrams and structured content. Built with FastAPI, Google Gemini AI, and integrates with Notion for publishing.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![uv](https://img.shields.io/badge/uv-Package%20Manager-purple.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)
![Google Gemini](https://img.shields.io/badge/Google-Gemini%20AI-orange.svg)
![Notion](https://img.shields.io/badge/Notion-API-black.svg)
![AWS S3](https://img.shields.io/badge/AWS-S3-yellow.svg)

## ✨ Features

- 🔍 **GitHub Repository Analysis**: Downloads and analyzes any public GitHub repository
- 🤖 **AI-Powered Content Generation**: Uses Google Gemini AI to create technical newsletters
- 📊 **Architecture Diagrams**: Automatically generates system architecture diagrams using Mermaid
- 🎨 **Visual Content**: Creates and uploads images to AWS S3 for hosting
- 📄 **Notion Integration**: Publishes formatted newsletters directly to Notion pages
- 🚀 **FastAPI Backend**: RESTful API with automatic documentation
- 🔒 **Secure**: API key authentication and environment-based configuration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  Newsletter     │───▶│   Notion Page   │
│   Analysis      │    │  Generator      │    │   Publishing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Code Analysis  │    │  Gemini AI      │    │  Structured     │
│  & File Reading │    │  Processing     │    │  Content Blocks │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Mermaid        │    │  Image          │    │  API            │
│  Diagrams       │    │  Generation     │    │  Response       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip for package management
- AWS Account with S3 access
- Google AI Studio API key
- Notion API integration

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd newsletter-agent
   ```

2. **Install uv (recommended)**
   ```bash
   # macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Create virtual environment and install dependencies**
   
   **Using uv (recommended):**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```
   
   **Using traditional pip:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the root directory:
   ```env
   # API Security
   API_KEY=your-secure-api-key-here
   
   # Google Gemini AI
   GEMINI_API_KEY=your-gemini-api-key
   
   # Notion Integration
   NOTION_API_KEY=your-notion-api-key
   
   # AWS S3 Configuration
   AWS_ACCESS_KEY_ID=your-aws-access-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret-key
   AWS_S3_BUCKET=your-s3-bucket-name
   AWS_S3_REGION=your-s3-region
   ```

5. **Install Playwright (for diagram generation)**
   ```bash
   playwright install chromium
   ```

## 🚀 Usage

### Starting the Server

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

### API Documentation

- **Interactive Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### API Endpoints

#### Health Check
```bash
GET /
Headers: x-api-key: your-api-key
```

#### Generate Newsletter
```bash
POST /newsletter
Headers: 
  x-api-key: your-api-key
  Content-Type: application/json

Body:
{
  "data": {
    "id": "notion-page-uuid-here",
    "properties": {
      "GitHub": {
        "url": "https://github.com/username/repository"
      }
    }
  }
}
```

### Example Usage

```bash
curl -X POST "http://127.0.0.1:8000/newsletter" \
  -H "x-api-key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "id": "12345678-1234-1234-1234-123456789abc",
      "properties": {
        "GitHub": {
          "url": "https://github.com/facebook/react"
        }
      }
    }
  }'
```

## 📁 Project Structure

```
newsletter-agent/
├── main.py                 # FastAPI application and main logic
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
└── lib/                  # Core modules
    ├── agent_template.py  # AI agent prompts and templates
    ├── file_reader.py     # File system utilities
    ├── github.py          # GitHub repository handling
    ├── notion.py          # Notion API integration
    ├── s3.py             # AWS S3 file uploading
    └── tools.py          # Diagram generation utilities
```

## 🔧 Core Components

### AI Agents
- **Newsletter Writer**: Creates initial newsletter content
- **Newsletter Editor**: Refines and improves content
- **Diagram Generator**: Creates system architecture diagrams
- **JSON Converter**: Formats content for Notion blocks

### Integrations
- **GitHub**: Repository analysis and file extraction
- **Google Gemini**: AI-powered content generation
- **Notion**: Newsletter publishing and formatting
- **AWS S3**: Image hosting and storage
- **Mermaid Ink**: Diagram generation service

## 🎨 Generated Content

The newsletter agent automatically creates:

1. **📋 Executive Summary**: Overview of the project
2. **🏗️ Architecture Diagram**: Visual system representation  
3. **✨ Key Features**: Highlighted functionality
4. **🛠️ Technical Stack**: Technologies used
5. **📊 Code Analysis**: Structure and patterns
6. **🔗 Links**: Repository and relevant resources

## 🔒 Security

- API key authentication on all endpoints
- Environment variable configuration
- Secure AWS S3 integration
- Input validation and sanitization

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid image url" in Notion**
   - Images are now automatically uploaded to S3 for compatibility
   - Ensure S3 bucket has public read access configured

2. **Gemini API Errors**
   - Verify your `GEMINI_API_KEY` is valid
   - Check API quotas and usage limits

3. **Notion Integration Issues**
   - Ensure the Notion page UUID is valid
   - Verify Notion API key has proper permissions

4. **S3 Upload Failures**
   - Check AWS credentials and permissions
   - Ensure S3 bucket exists and is accessible

### Debugging

Enable detailed logging by running:
```bash
uvicorn main:app --log-level debug
```

## 📋 Requirements

This project uses [uv](https://docs.astral.sh/uv/) for fast and reliable Python package management. See `requirements.txt` for complete dependency list. Key packages:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-generativeai` - Google Gemini AI
- `requests` - HTTP client
- `boto3` - AWS SDK
- `playwright` - Browser automation
- `pydantic` - Data validation
- `python-dotenv` - Environment management

**Why uv?**
- ⚡ **10-100x faster** than pip for package installation
- 🔒 **More reliable** dependency resolution
- 🚀 **Modern Python tooling** with better caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
