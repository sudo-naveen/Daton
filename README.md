# Daton - AI Data Analyst

Daton is an AI-powered data analyst agent that uses **RAG, SQL, tool calling, and Python** to analyze databases and documents through natural-language queries, generate insights, and create visualizations.

## Features

- **Natural Language Queries** - Ask questions about your data in plain English
- **SQL Tool** - Auto-generates and executes safe, read-only SQL queries
- **RAG System** - Upload documents (PDF, TXT, DOCX, CSV) and query them
- **Python/Pandas Analysis** - Analyze uploaded CSV/Excel datasets
- **Visualization** - Auto-generate bar, line, scatter, histogram, and pie charts
- **Calculator** - Accurate mathematical calculations
- **Conversation Memory** - Multi-turn conversations with context
- **Multi-tool Workflows** - Agent autonomously selects and chains tools

## Architecture

```
User -> LangGraph Agent -> Tool Router
  ├── SQL Tool -> Database (MySQL/SQLite)
  ├── RAG Tool -> ChromaDB (PDF, TXT, DOCX, CSV)
  ├── Python Tool -> Pandas (CSV/Excel analysis)
  ├── Visualization Tool -> Matplotlib (charts)
  └── Calculator Tool -> Math engine
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend API | FastAPI |
| Agent Framework | LangGraph + LangChain |
| LLM | Gemini 2.0 Flash |
| Vector DB | ChromaDB |
| Database | SQLite / MySQL |
| Analysis | Pandas |
| Visualization | Matplotlib |
| Frontend | Streamlit |
| Language | Python 3.11+ |

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/daton.git
cd daton

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Environment Setup

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./data/daton.db
```

## Database Setup

```bash
python data/setup_db.py
```

This creates a SQLite database with sample sales and employee data.

## Running Locally

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

Open http://localhost:8501 in your browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message to the AI agent |
| POST | `/api/documents/upload` | Upload a document for RAG |
| GET | `/api/documents` | List uploaded documents |
| DELETE | `/api/documents/{filename}` | Delete a document |
| POST | `/api/datasets/upload` | Upload a CSV/Excel dataset |
| GET | `/api/datasets` | List uploaded datasets |
| POST | `/api/database/test` | Test database connection |
| POST | `/api/database/connect` | Connect to a database |
| GET | `/api/database/tables` | List database tables |
| GET | `/api/database/schema` | Get full database schema |
| GET | `/health` | Health check |

## Example Queries

### Calculator
```
Calculate 125 * 48.
```
Expected: `6000`

### SQL
```
Show the top 5 products by revenue.
```
Expected: SQL Tool executes query, returns results.

### RAG
Upload a PDF, then ask:
```
What does this report say about revenue?
```
Expected: Answer with source citations.

### Dataset Analysis
Upload a CSV, then ask:
```
What is the average salary for each department?
```
Expected: Pandas analysis with results.

### Visualization
```
Create a bar chart showing revenue by region.
```
Expected: Chart generated from data.

### Conversation Memory
```
Show sales for 2025.
Which month was highest?
```
Expected: Agent understands context.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_calculator.py -v
pytest tests/test_sql_validation.py -v
pytest tests/test_pandas.py -v
pytest tests/test_visualization.py -v
pytest tests/test_api.py -v
pytest tests/test_rag.py -v
```

## Project Structure

```
daton/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py             # Configuration
│   ├── agent/
│   │   ├── graph.py          # LangGraph agent
│   │   ├── state.py          # Agent state
│   │   └── prompts.py        # System prompts
│   ├── tools/
│   │   ├── sql_tool.py       # SQL execution
│   │   ├── rag_tool.py       # Document search
│   │   ├── python_tool.py    # Pandas analysis
│   │   ├── visualization_tool.py  # Chart generation
│   │   └── calculator_tool.py     # Math calculations
│   ├── rag/
│   │   ├── ingestion.py      # Document processing
│   │   ├── embeddings.py     # Embedding models
│   │   ├── chroma_store.py   # ChromaDB operations
│   │   └── retriever.py      # RAG pipeline
│   ├── database/
│   │   ├── connection.py     # DB connections
│   │   └── schema.py         # Schema utilities
│   └── api/
│       ├── chat.py           # Chat endpoint
│       ├── documents.py      # Document management
│       ├── datasets.py       # Dataset management
│       └── database.py       # Database management
├── frontend/
│   └── app.py                # Streamlit UI
├── data/
│   ├── setup_db.py           # DB setup script
│   ├── sample_sales.csv      # Sample data
│   ├── sample_employees.csv  # Sample data
│   └── sample_report.txt     # Sample document
├── tests/
│   ├── test_calculator.py
│   ├── test_sql_validation.py
│   ├── test_pandas.py
│   ├── test_visualization.py
│   ├── test_api.py
│   └── test_rag.py
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Security

- Environment-based secrets (no hardcoded credentials)
- SQL validation blocks destructive operations (DROP, DELETE, UPDATE, INSERT, etc.)
- File type validation and size limits
- Read-only database access by default
- Input validation via Pydantic models

## Known Limitations

- SQLite used by default; MySQL requires additional setup
- Gemini API key required for all AI features
- Large documents may take time to process
- ChromaDB is in-process; not suitable for multi-instance deployments
- Visualization tool generates PNG files stored on disk

## Future Improvements

- User authentication and authorization
- Persistent conversation history in database
- More database drivers (PostgreSQL, BigQuery)
- Advanced anomaly detection
- Scheduled reports and monitoring
- Role-based access control
- WebSocket for real-time streaming
- Multi-language support

