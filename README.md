# Document Intelligence Platform

AI-powered document extraction, validation & REST API platform for financial documents (invoices, balance sheets, P&L, cash flow statements).

## 📋 Overview

This platform extracts structured financial data from PDF, JPG, and PNG documents using:
- **OCR/Text Extraction**: PyPDF2 for native PDFs, OCR.Space API for scanned images
- **AI Extraction**: Anthropic Claude API (or Gemini) for field extraction using advanced prompting
- **Financial Validation**: Automated validation of financial calculations and relationships
- **REST API**: FastAPI for document processing and retrieval
- **Web Dashboard**: HTML5 frontend for document upload and result visualization
- **Database**: PostgreSQL for production, SQLite for local development

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend UI   │ (HTML5/JS dashboard)
└────────┬────────┘
         │
┌────────▼────────────────────────────┐
│      FastAPI REST Backend            │
├──────────────────────────────────────┤
│  POST /api/v1/documents/process      │
│  GET  /api/v1/documents              │
│  GET  /api/v1/documents/{name}       │
│  GET  /api/v1/health                 │
└────────┬──────────────────────────────┘
         │
    ┌────┴──────────────────────────┐
    │                               │
    ▼                               ▼
┌─────────────┐            ┌────────────────┐
│  Services   │            │    Database    │
├─────────────┤            ├────────────────┤
│ Validation  │            │  PostgreSQL    │
│ OCR         │            │  SQLite (dev)  │
│ Extraction  │            └────────────────┘
│ Validation  │
└─────────────┘
    │
    ├─ PyPDF2 (PDF parsing)
    ├─ Pillow (Image handling)
    ├─ OCR.Space API (Scanned images)
    ├─ Anthropic Claude API (Field extraction)
    └─ SQLAlchemy (ORM)
```

## 📁 Project Structure

```
project-root/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── documents.py          # Document processing endpoints
│   │   │   └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py                 # Settings & configuration
│   │   │   ├── database.py               # SQLAlchemy setup
│   │   │   ├── logging.py                # Logging configuration
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── document.py               # SQLAlchemy Document model
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── extraction.py             # Pydantic response schemas
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── document_validation_service.py  # File validation
│   │   │   ├── ocr_service.py                  # Text extraction
│   │   │   ├── extraction_service.py           # Claude extraction
│   │   │   ├── financial_validation_service.py # Calc validation
│   │   │   └── __init__.py
│   │   ├── repositories/
│   │   │   ├── document_repository.py    # Database access
│   │   │   └── __init__.py
│   │   ├── main.py                       # FastAPI app initialization
│   │   └── __init__.py
│   ├── requirements.txt
│   └── wsgi.py                           # Production WSGI entry point
│
├── frontend/
│   ├── templates/
│   │   └── dashboard.html                # Main web interface
│   └── static/
│       ├── css/                          # Stylesheets
│       └── js/                           # JavaScript
│
├── tests/
│   ├── test_validation.py                # File validation tests
│   ├── test_extraction.py                # Extraction logic tests
│   └── test_api.py                       # API endpoint tests
│
├── docs/
│   ├── architecture.md                   # Detailed architecture
│   └── api_examples.md                   # API usage examples
│
├── sample_outputs/
│   ├── invoice_sample.json               # Sample JSON responses
│   ├── balance_sheet_sample.json
│   ├── profit_loss_sample.json
│   └── cash_flow_sample.json
│
├── .env.example                          # Environment template
├── .gitignore
├── README.md                             # This file
└── docker-compose.yml                    # Docker setup (optional)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+ (or SQLite for dev)
- API key: Anthropic Claude (sk-ant-...) OR Google Gemini

### Local Setup (SQLite)

1. **Clone & Setup**
   ```bash
   cd document_intelligence
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r backend/requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   # DATABASE_URL=sqlite:///./document_intelligence.db (for dev)
   ```

3. **Run Backend**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access Dashboard**
   - Frontend: http://localhost:8000/static/templates/dashboard.html
   - API Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/api/v1/health

### Docker Setup (PostgreSQL)

```bash
docker-compose up -d
# Postgres: localhost:5432
# API: http://localhost:8000
```

## 📊 Supported Document Types

### Invoice
**Extracts**: invoice_number, invoice_date, vendor_name, customer_name, currency, subtotal, tax_amount, discount, total_amount, line_items (description, quantity, unit_price, amount), payment_terms, due_date

**Validates**: 
- Line item calculations (qty × price ≈ amount)
- Invoice total (subtotal + tax - discount = total)

### Balance Sheet
**Extracts**: company_name, reporting_period, currency, total_assets, total_liabilities, total_equity, all line items (Assets, Liabilities, Equity), comparative periods

**Validates**:
- Balance sheet equation: Assets = Liabilities + Equity
- Section subtotals and totals for each period

### Profit & Loss
**Extracts**: revenue, cost_of_sales, gross_profit, operating_expenses, operating_profit, tax, net_profit, all line items, comparative periods

**Validates**:
- Gross Profit = Revenue - COGS
- Operating Profit = Gross Profit - Operating Expenses
- Net Profit calculations

### Cash Flow Statement
**Extracts**: operating_cash_flow, investing_cash_flow, financing_cash_flow, opening_cash, net_change_in_cash, closing_cash, FX adjustments, comparative periods

**Validates**:
- Net Change = Operating CF + Investing CF + Financing CF
- Closing Cash = Opening Cash + Net Change

## 🔌 API Endpoints

### Process Document
```http
POST /api/v1/documents/process
Content-Type: multipart/form-data

file: <document.pdf|.jpg|.png>
document_type: invoice | balance_sheet | profit_and_loss | cash_flow_statement
```

**Response**:
```json
{
  "document_name": "invoice_123.pdf",
  "document_type": "invoice",
  "processing_status": "PASS",
  "file_validation": {
    "file_type": "pdf",
    "is_supported": true,
    "is_readable": true,
    "page_count": 1,
    "status": "PASS"
  },
  "extracted_data": {
    "invoice_number": {"value": "INV-123", "page_number": 1},
    "invoice_date": {"value": "2026-01-15", "page_number": 1},
    "total_amount": {"value": 5000.00, "page_number": 1},
    "line_items": [
      {"description": "Service A", "quantity": 1, "unit_price": 5000, "amount": 5000}
    ]
  },
  "validation": {
    "checks": [
      {
        "name": "invoice_total_check",
        "formula": "subtotal + tax_amount - discount",
        "operands": {"subtotal": 5000, "tax_amount": 0, "discount": 0},
        "calculated_value": 5000.00,
        "reported_value": 5000.00,
        "variance": 0.00,
        "status": "PASS"
      }
    ],
    "overall_status": "PASS",
    "issues": []
  },
  "overall_confidence": 0.95,
  "processing_metadata": {
    "ocr_used": false,
    "processed_at": "2026-09-11T12:00:00Z",
    "processing_time_ms": 2840
  }
}
```

### Get Document by Name
```http
GET /api/v1/documents/invoice_123.pdf
```

### List Documents
```http
GET /api/v1/documents?limit=50&offset=0
```

### Health Check
```http
GET /api/v1/health
```

## 🔐 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/document_intelligence

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxx...
GEMINI_API_KEY=xxx...  # Alternative to Claude

# OCR
OCR_SPACE_API_KEY=K87899142591  # Free tier

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

## 🧪 Testing

### Run Tests
```bash
cd backend
pytest tests/
```

### Test Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Manual Testing
1. Use frontend dashboard to upload test documents
2. Check `/docs` Swagger UI for API testing
3. Review extracted data and validation results

## 🛠️ Technology Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| **API Framework** | FastAPI | Modern, fast, auto-documentation |
| **ORM** | SQLAlchemy | Database-agnostic, production-ready |
| **Database** | PostgreSQL | Scalable, JSONB support for nested data |
| **AI Extraction** | Anthropic Claude | Superior accuracy for financial data |
| **OCR** | OCR.Space + PyPDF2 | Free tier, native PDF support |
| **Frontend** | HTML5 + Vanilla JS | Lightweight, no build step required |
| **Server** | Uvicorn | ASGI, production-ready |
| **Deployment** | Docker + Railway/Render | Container-based, easy scaling |

## 📈 Deployment

### Railway (Recommended)
```bash
# Push to GitHub
git push origin main

# Connect GitHub repo to Railway
# Set environment variables in Railway dashboard
# Automatic deployment on push
```

### Render.com
```bash
# Create new Web Service from GitHub
# Set build command: pip install -r backend/requirements.txt
# Set start command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
# Add PostgreSQL database
# Set DATABASE_URL in environment
```

### Koyeb
1. Push to GitHub
2. Connect Koyeb to repo
3. Set environment variables
4. Deploy

## 📝 Key Features Implemented

✅ Document validation (file type, size, page count, corruption check)
✅ OCR + native PDF text extraction
✅ Claude API integration for field extraction
✅ Financial calculation validation with configurable tolerance
✅ Structured JSON output with evidence/page numbers
✅ Database persistence (PostgreSQL/SQLite)
✅ RESTful API with proper HTTP status codes
✅ Web dashboard with upload/search/view
✅ Comprehensive error handling & logging
✅ Production-ready code structure

## 🎯 Design Decisions

**PostgreSQL over SQLite**: Scalability, JSONB support, concurrent connections for production
**Claude over Gemini**: Superior accuracy on financial documents, consistent API
**OCR.Space**: Free tier sufficient for MVP, scalable if needed
**Service-based architecture**: Separation of concerns, testable, reusable components
**Pydantic schemas**: Type safety, automatic validation, OpenAPI docs
**Structured extraction**: Key-value pairs + tables, not free-form text

## 🚦 Performance

- Document processing: 2-5 seconds per page (depends on Claude API latency)
- Database queries: <100ms (indexed on file_name)
- Frontend load: <1s (lightweight HTML/JS)
- API throughput: 100+ concurrent requests (Uvicorn + Gunicorn scaling)

## 📚 Known Limitations

1. **Max 3 pages per document** - Configurable in settings
2. **PDF text extraction** - Relies on native PDF text (OCR for scanned docs via API)
3. **Financial line items** - Assumes standard accounting formats
4. **Tolerance** - 1% numerical tolerance for validations (configurable)
5. **Concurrent uploads** - Limited by Claude API rate limits

## 🔄 Production Improvements

1. **Caching**: Redis for extraction results and validation rules
2. **Async Processing**: Celery for background document processing
3. **Batch Operations**: Support bulk document uploads
4. **ML Confidence**: Train custom model for document type auto-classification
5. **Export Formats**: CSV, Excel, PDF report generation
6. **Audit Trail**: Track all extractions and validations with user attribution
7. **Webhook Notifications**: Notify external systems when processing complete
8. **Multi-language OCR**: Support non-English documents
9. **API Rate Limiting**: Token bucket for fair usage
10. **Monitoring**: Prometheus metrics + Grafana dashboards

## 📖 AI/Tools Used

This project was built with assistance from:
- **Claude (Anthropic)**: Code generation, architecture design, prompt engineering
- **ChatGPT (OpenAI)**: Testing, documentation review
- **GitHub Copilot**: Code completion suggestions

## 📄 License

MIT License - See LICENSE file

## 👥 Support

For issues or questions:
1. Check existing GitHub issues
2. Review documentation in `/docs`
3. Check API examples in `/sample_outputs`
4. Submit new issue with:
   - Document type
   - Error message/logs
   - Environment details
   - Steps to reproduce

---

**Version**: 1.0.0  
**Last Updated**: September 2026  
**Status**: Production-Ready for MVP
