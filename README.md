# Health-Assistant Application

A production-ready AI-powered health assistant built with FastAPI, Streamlit, Google Gemini 1.5 Flash, and Dropbox integration. This application provides a secure chat interface for health queries and medical report analysis.

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit UI  │────▶│   FastAPI Backend│────▶│  Gemini 1.5 Flash│
│   (Frontend)    │◀────│   (API Layer)    │◀────│  (AI Engine)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │
        ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  File Upload    │     │   Dropbox API   │
│  (PDF Reports)  │     │  (File Storage) │
└─────────────────┘     └─────────────────┘
```

## ✨ Features

- **AI-Powered Chat**: Natural language conversations about health topics using Gemini 1.5 Flash
- **Medical Report Analysis**: Upload PDF medical reports for AI-assisted analysis and summarization
- **Secure File Storage**: Optional Dropbox integration for storing medical documents
- **Modern UI**: Clean, responsive Streamlit interface with chat history management
- **Production Ready**: Comprehensive error handling, input validation, and security best practices
- **API Documentation**: Interactive Swagger UI for API testing and documentation

## 📁 Project Structure

```
health-assistant/
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Active configuration (gitignored)
├── README.md                 # This file
├── run.py                    # Backend launcher script
├── run_streamlit.py          # Frontend launcher script
└── app/
    ├── __init__.py           # Package initializer
    ├── main.py               # FastAPI application with all endpoints
    ├── streamlit_app.py      # Streamlit frontend application
    ├── agents/
    │   ├── __init__.py       # Agents package initializer
    │   ├── gemini_tool.py    # Google Gemini AI integration
    │   └── dropbox_tool.py   # Dropbox API integration
    └── utils/
        ├── __init__.py       # Utils package initializer
        └── helpers.py        # PDF parsing, text processing utilities
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API Key ([Get it here](https://aistudio.google.com/app/apikey))
- Dropbox Access Token (optional, for file storage features)

### Installation

1. **Navigate to the project directory**:
```bash
cd /workspace
```

2. **Create and activate a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
DROPBOX_ACCESS_TOKEN=your_dropbox_access_token_here  # Optional
BACKEND_URL=http://localhost:8000
```

### Running the Application

#### Option 1: Using Launcher Scripts (Recommended)

**Terminal 1 - Start Backend:**
```bash
python run.py
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run app/streamlit_app.py
```

#### Option 2: Direct Commands

**Terminal 1 - Start Backend:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
streamlit run app/streamlit_app.py
```

#### Option 3: Production Mode

**Backend (Production):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access the Application

- **Frontend UI**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/api/health

## 📡 API Endpoints

### POST `/api/chat`
Send a message to the AI assistant.

**Request Body:**
```json
{
  "query": "What are the symptoms of diabetes?"
}
```

**Response:**
```json
{
  "status": "success",
  "response": "Diabetes symptoms include frequent urination, excessive thirst...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### POST `/api/upload`
Upload a PDF medical report for analysis.

**Request:**
- Content-Type: `multipart/form-data`
- Form field: `query` (user question)
- Form field: `file` (PDF file)

**Response:**
```json
{
  "status": "success",
  "response": "Based on your medical report...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET `/api/health`
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "health-assistant-api",
  "version": "1.0.0"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | Your Google Gemini API key |
| `DROPBOX_ACCESS_TOKEN` | ❌ No | Dropbox access token for file storage |
| `BACKEND_URL` | ❌ No | Backend API URL (default: http://localhost:8000) |

### PDF Parsing

The application supports multiple PDF parsing strategies:
- **PyPDF2**: Fast extraction for standard PDFs
- **pdfplumber**: Advanced extraction for complex layouts (tables, columns)

The system automatically falls back to alternative parsers if the primary method fails.

## 🛡️ Security & Privacy

### Important Medical Disclaimer

⚠️ **This application is for informational purposes only and does not constitute medical advice.**

- Always consult with qualified healthcare professionals for medical concerns
- In case of emergency, call your local emergency number immediately
- Do not delay seeking professional medical advice based on AI responses

### Data Handling

- **No Data Persistence**: Chat conversations are not stored on the server
- **Temporary File Processing**: Uploaded PDFs are processed in-memory and not saved
- **Optional Cloud Storage**: Dropbox integration is opt-in only
- **API Key Security**: Keys are loaded from environment variables, never hardcoded

### Best Practices Implemented

- Input validation on all API endpoints
- CORS configuration for cross-origin requests
- Error handling with appropriate HTTP status codes
- Secure handling of sensitive medical information

## 🧪 Testing

### Manual Testing

1. **Test Chat Functionality**:
   - Open http://localhost:8501
   - Send a health-related question
   - Verify AI response appears in chat

2. **Test PDF Upload**:
   - Upload a sample medical report PDF
   - Verify text extraction and AI analysis
   - Check for proper error handling with invalid files

3. **Test API Endpoints**:
   - Visit http://localhost:8000/docs
   - Try each endpoint with test data
   - Verify response formats

### Test with curl

```bash
# Health check
curl http://localhost:8000/api/health

# Chat query
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are common symptoms of flu?"}'
```

## 🐳 Docker Deployment

### Build Docker Image

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
```

### Run with Docker

```bash
docker build -t health-assistant .
docker run -p 8000:8000 -p 8501:8501 \
  -e GEMINI_API_KEY=your_key \
  -e DROPBOX_ACCESS_TOKEN=your_token \
  health-assistant
```

## 📊 Monitoring & Logging

### Application Logs

Logs are output to stdout/stderr and can be captured by:
- Docker logging drivers
- Systemd journal (Linux)
- Cloud logging services (AWS CloudWatch, GCP Logging, etc.)

### Health Checks

Use the `/api/health` endpoint for:
- Load balancer health checks
- Kubernetes liveness/readiness probes
- Monitoring system alerts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for function signatures
- Write docstrings for public functions and classes

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) - AI model provider
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Streamlit](https://streamlit.io/) - Frontend framework
- [Dropbox API](https://www.dropbox.com/developers) - Cloud storage integration

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review API error messages for troubleshooting

---

**Built with ❤️ for better healthcare accessibility**

*Remember: This tool supplements but never replaces professional medical advice.*
