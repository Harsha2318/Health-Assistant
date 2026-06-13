# Health-Assistant Application

A production-ready healthcare assistant application that provides AI-powered health-related advice using Google's Gemini 1.5 Flash model. Users can ask health-related questions and upload medical reports (PDFs) for personalized, context-aware advice.

## 🌟 Features

- 💬 **Chat Interface**: Modern, responsive chat UI for health-related queries
- 📄 **PDF Analysis**: Upload medical reports for AI-powered analysis and insights
- 🤖 **AI-Powered**: Powered by Google's Gemini 1.5 Flash model with healthcare-specific prompting
- 🔒 **Secure Storage**: Optional Dropbox integration for secure file storage
- 🎨 **Modern UI**: Beautiful, dark-themed Streamlit interface
- 📊 **API Documentation**: Interactive API docs with FastAPI Swagger UI
- ⚠️ **Safety First**: Built-in safety guidelines and medical disclaimers

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│    FastAPI       │────▶│  Google Gemini  │
│   Frontend      │     │    Backend       │     │  1.5 Flash API  │
│   (Port 8501)   │◀────│   (Port 8000)    │     └─────────────────┘
└─────────────────┘     └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │    Dropbox API   │
                        │  (Optional)      │
                        └──────────────────┘
```

## 📁 Project Structure

```
health-assistant/
├── app/
│   ├── __init__.py              # Package initializer
│   ├── main.py                  # FastAPI application with all endpoints
│   ├── streamlit_app.py         # Streamlit frontend
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── gemini_tool.py       # Gemini AI integration with healthcare prompts
│   │   └── dropbox_tool.py      # Dropbox SDK integration
│   └── utils/
│       ├── __init__.py
│       └── helpers.py           # PDF parsing, text processing utilities
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── run.py                       # Backend launcher script
├── run_streamlit.py             # Frontend launcher script
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Google Gemini API key ([Get it here](https://aistudio.google.com/app/apikey))
- Dropbox access token (optional, for file storage)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health-assistant
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_actual_gemini_api_key
   DROPBOX_ACCESS_TOKEN=your_actual_dropbox_token  # Optional
   BACKEND_URL=http://localhost:8000
   ```

5. **Start the FastAPI backend**
   ```bash
   python run.py
   # Or alternatively:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Start the Streamlit frontend** (in a new terminal)
   ```bash
   streamlit run app/streamlit_app.py
   # Or alternatively:
   python run_streamlit.py
   ```

7. **Access the application**
   - **Frontend**: http://localhost:8501
   - **API Docs**: http://localhost:8000/docs
   - **Alternative API Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### `GET /`
Root endpoint with API information.

### `GET /api/health`
Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "health-assistant-api",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### `POST /api/chat`
Send a health query without file upload.

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
  "response": "Diabetes symptoms include frequent urination, increased thirst...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### `POST /api/upload`
Upload a medical document (PDF) and get AI analysis.

**Request:**
- `query` (form field): User's health question
- `file` (file upload): PDF medical document

**Response:** Same as `/api/chat`

### `POST /api/health-advice`
Legacy endpoint supporting both chat and file upload.

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `DROPBOX_ACCESS_TOKEN` | Dropbox API access token | No | - |
| `BACKEND_URL` | Backend API URL | No | `http://localhost:8000` |

### Getting API Keys

#### Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and add it to your `.env` file

#### Dropbox Access Token (Optional)
1. Visit [Dropbox Developers](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose "Scoped access" → "Full Dropbox"
4. Name your app and create it
5. In the settings, generate an access token
6. Copy the token and add it to your `.env` file

## 🧪 Testing

### Test the Backend

1. **Using curl:**
   ```bash
   # Health check
   curl http://localhost:8000/api/health
   
   # Chat query
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What are common symptoms of flu?"}'
   ```

2. **Using the Swagger UI:**
   - Open http://localhost:8000/docs
   - Try out the endpoints interactively

### Test the Frontend

1. Start both backend and frontend
2. Open http://localhost:8501 in your browser
3. Try these test scenarios:
   - Ask a simple health question
   - Upload a sample PDF medical report
   - Check the sidebar tips and status indicators

## 🛡️ Security & Privacy

### Data Handling
- All health queries are processed securely via HTTPS (in production)
- Medical documents are optionally stored in your personal Dropbox
- No data is retained on our servers beyond the session

### Important Disclaimers
⚠️ **This application:**
- Does NOT diagnose medical conditions
- Does NOT prescribe medications
- Does NOT replace professional medical advice
- Should NOT be used for medical emergencies

**For emergencies, always call 911 or your local emergency number.**

## 🚀 Production Deployment

### Docker Deployment (Recommended)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 & streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"]
```

### Environment Variables for Production
```bash
GEMINI_API_KEY=your_production_key
DROPBOX_ACCESS_TOKEN=your_production_token
BACKEND_URL=https://your-domain.com/api
```

### Security Best Practices
1. Use HTTPS in production
2. Implement authentication if handling sensitive data
3. Add rate limiting to prevent abuse
4. Enable CORS only for trusted domains
5. Store secrets in a secure vault (e.g., AWS Secrets Manager, HashiCorp Vault)

## 📝 Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style
```bash
# Install linting tools
pip install black flake8 isort

# Format code
black .
isort .

# Lint code
flake8 .
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for the powerful language model
- [Streamlit](https://streamlit.io/) for the beautiful frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the high-performance backend
- [Dropbox](https://www.dropbox.com/developers) for secure file storage

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review API error messages for troubleshooting

---

**Built with ❤️ for better healthcare accessibility**
