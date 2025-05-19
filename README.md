# HealthCare Agent with Streamlit and Gemini

A healthcare assistant application that provides health-related advice using Google's Gemini AI model. Users can ask health-related questions and upload medical reports (PDFs) for personalized advice.

## Features

- 💬 Chat interface for health-related queries
- 📄 PDF upload for medical report analysis
- 🤖 Powered by Google's Gemini 1.5 Flash model
- 🔒 Secure file handling with Dropbox integration
- 🎨 Modern, responsive UI with Streamlit

## Prerequisites

- Python 3.8+
- Google Gemini API key
- Dropbox account (for file storage)
- Node.js (for optional frontend development)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd healthcare-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your API keys
   ```bash
   cp .env.example .env
   ```

4. **Run the FastAPI backend**
   ```bash
   cd app
   uvicorn main:app --reload
   ```

5. **Run the Streamlit frontend** (in a new terminal)
   ```bash
   cd app
   streamlit run streamlit_app.py
   ```

6. **Access the application**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `DROPBOX_ACCESS_TOKEN` | Dropbox API access token | No (required for file uploads) |
| `BACKEND_URL` | Backend API URL | No (default: http://localhost:8000) |

## Project Structure

```
healthcare-agent/
├── app/
│   ├── main.py                # FastAPI application
│   ├── streamlit_app.py       # Streamlit frontend
│   ├── agents/
│   │   ├── gemini_tool.py    # Gemini AI integration
│   │   └── dropbox_tool.py    # Dropbox file handling
│   └── utils/
│       └── (utility functions)
├── .env.example              # Example environment variables
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Security Notes

- Never commit your `.env` file to version control
- The application is designed to handle health information securely
- All file uploads are stored in your personal Dropbox account
- For production use, consider adding authentication and rate limiting

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
