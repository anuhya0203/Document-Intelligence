# API Examples & Usage Guide

## Processing Documents

### Upload Invoice

```bash
curl -X POST http://localhost:8000/api/v1/documents/process \
  -F "file=@invoice.pdf" \
  -F "document_type=invoice"
```

### Upload Balance Sheet

```bash
curl -X POST http://localhost:8000/api/v1/documents/process \
  -F "file=@balance_sheet.pdf" \
  -F "document_type=balance_sheet"
```

### Upload Scanned Invoice (JPG/PNG)

```bash
curl -X POST http://localhost:8000/api/v1/documents/process \
  -F "file=@scanned_invoice.jpg" \
  -F "document_type=invoice"
```

## Retrieving Results

### Get Document by Name

```bash
curl -X GET http://localhost:8000/api/v1/documents/invoice_123.pdf
```

### List All Documents

```bash
curl -X GET "http://localhost:8000/api/v1/documents?limit=100&offset=0"
```

### Check Health

```bash
curl -X GET http://localhost:8000/api/v1/health
```

## Response Examples

### Invoice Processing Response

```json
{
  "document_name": "invoice_001.pdf",
  "document_type": "invoice",
  "processing_status": "PASS",
  "overall_confidence": 0.95,
  "file_validation": {
    "file_type": "pdf",
    "is_supported": true,
    "is_readable": true,
    "page_count": 1,
    "status": "PASS"
  },
  "extracted_data": {
    "invoice_number": {
      "value": "INV-2026-001234",
      "page_number": 1
    },
    "invoice_date": {
      "value": "2026-09-15",
      "page_number": 1
    },
    "vendor_name": {
      "value": "ABC Technologies Inc.",
      "page_number": 1
    },
    "customer_name": {
      "value": "XYZ Corporation",
      "page_number": 1
    },
    "currency": {
      "value": "USD",
      "page_number": 1
    },
    "subtotal": {
      "value": 50000.00,
      "page_number": 1
    },
    "tax_amount": {
      "value": 5000.00,
      "page_number": 1
    },
    "discount": {
      "value": 0.00,
      "page_number": 1
    },
    "total_amount": {
      "value": 55000.00,
      "page_number": 1
    },
    "line_items": [
      {
        "description": "Software Development Services - Q3",
        "quantity": 1,
        "unit_price": 50000.00,
        "amount": 50000.00,
        "page_number": 1
      }
    ],
    "payment_terms": {
      "value": "Net 30",
      "page_number": 1
    },
    "due_date": {
      "value": "2026-10-15",
      "page_number": 1
    }
  },
  "validation": {
    "checks": [
      {
        "name": "invoice_total_check",
        "formula": "subtotal + tax_amount - discount",
        "operands": {
          "subtotal": 50000.00,
          "tax_amount": 5000.00,
          "discount": 0.00
        },
        "calculated_value": 55000.00,
        "reported_value": 55000.00,
        "variance": 0.00,
        "status": "PASS"
      },
      {
        "name": "line_items_reconciliation",
        "formula": "quantity × unit_price ≈ amount",
        "status": "PASS"
      }
    ],
    "overall_status": "PASS",
    "issues": []
  },
  "processing_metadata": {
    "ocr_used": false,
    "processed_at": "2026-09-15T10:30:00Z",
    "processing_time_ms": 3245
  }
}
```

### Balance Sheet Response

```json
{
  "document_name": "balance_sheet_2025.pdf",
  "document_type": "balance_sheet",
  "processing_status": "PASS",
  "overall_confidence": 0.92,
  "file_validation": {
    "file_type": "pdf",
    "is_supported": true,
    "is_readable": true,
    "page_count": 2,
    "status": "PASS"
  },
  "extracted_data": {
    "company_name": {
      "value": "Global Finance Corp.",
      "page_number": 1
    },
    "reporting_period": {
      "value": "December 31, 2025",
      "page_number": 1
    },
    "currency": {
      "value": "USD",
      "page_number": 1
    },
    "total_assets": {
      "value": 1000000.00,
      "page_number": 1
    },
    "total_liabilities": {
      "value": 600000.00,
      "page_number": 1
    },
    "total_equity": {
      "value": 400000.00,
      "page_number": 1
    },
    "assets": [
      {
        "name": "Cash and Cash Equivalents",
        "value": 150000.00,
        "page_number": 1
      },
      {
        "name": "Accounts Receivable",
        "value": 250000.00,
        "page_number": 1
      },
      {
        "name": "Inventory",
        "value": 200000.00,
        "page_number": 1
      },
      {
        "name": "Fixed Assets",
        "value": 400000.00,
        "page_number": 1
      }
    ],
    "liabilities": [
      {
        "name": "Accounts Payable",
        "value": 150000.00,
        "page_number": 2
      },
      {
        "name": "Short-term Debt",
        "value": 200000.00,
        "page_number": 2
      },
      {
        "name": "Long-term Debt",
        "value": 250000.00,
        "page_number": 2
      }
    ]
  },
  "validation": {
    "checks": [
      {
        "name": "balance_sheet_equation",
        "formula": "total_liabilities + total_equity",
        "operands": {
          "total_liabilities": 600000.00,
          "total_equity": 400000.00
        },
        "calculated_value": 1000000.00,
        "reported_value": 1000000.00,
        "variance": 0.00,
        "status": "PASS"
      }
    ],
    "overall_status": "PASS",
    "issues": []
  },
  "processing_metadata": {
    "ocr_used": false,
    "processed_at": "2026-09-15T10:35:00Z",
    "processing_time_ms": 4120
  }
}
```

### Validation Failure Example

```json
{
  "document_name": "suspect_invoice.pdf",
  "document_type": "invoice",
  "processing_status": "PASS",
  "overall_confidence": 0.65,
  "file_validation": {
    "status": "PASS"
  },
  "extracted_data": {
    "invoice_number": {"value": "INV-999"},
    "subtotal": {"value": 1000.00},
    "tax_amount": {"value": 100.00},
    "discount": {"value": 0.00},
    "total_amount": {"value": 1150.00}  // Incorrect: should be 1100
  },
  "validation": {
    "checks": [
      {
        "name": "invoice_total_check",
        "formula": "subtotal + tax_amount - discount",
        "operands": {
          "subtotal": 1000.00,
          "tax_amount": 100.00,
          "discount": 0.00
        },
        "calculated_value": 1100.00,
        "reported_value": 1150.00,
        "variance": 50.00,
        "status": "FAILED"
      }
    ],
    "overall_status": "FAILED",
    "issues": ["invoice_total_check"]
  }
}
```

## Error Handling

### Unsupported File Type

```json
{
  "error": {
    "code": "UNSUPPORTED_FILE_TYPE",
    "message": "Only PDF / JPG / PNG documents are supported."
  }
}
```

### File Too Large

```json
{
  "error": {
    "code": "FILE_TOO_LARGE",
    "message": "File exceeds max size of 50MB"
  }
}
```

### Processing Error

```json
{
  "error": {
    "code": "PROCESSING_ERROR",
    "message": "Internal processing error: [specific error details]"
  }
}
```

## Python Integration Example

```python
import requests
import json

API_BASE = "http://localhost:8000/api/v1"

# Process document
with open('invoice.pdf', 'rb') as f:
    files = {'file': f}
    data = {'document_type': 'invoice'}
    response = requests.post(f'{API_BASE}/documents/process', files=files, data=data)

result = response.json()
print(f"Status: {result['processing_status']}")
print(f"Invoice Number: {result['extracted_data']['invoice_number']['value']}")

# Get validation results
for check in result['validation']['checks']:
    print(f"{check['name']}: {check['status']}")

# Retrieve later
response = requests.get(f'{API_BASE}/documents/invoice.pdf')
stored_result = response.json()
```

## JavaScript/Frontend Integration

```javascript
const API_BASE = '/api/v1';

async function processDocument(file, documentType) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    
    const response = await fetch(`${API_BASE}/documents/process`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) throw new Error('Processing failed');
    
    return await response.json();
}

async function getDocument(fileName) {
    const response = await fetch(`${API_BASE}/documents/${encodeURIComponent(fileName)}`);
    return await response.json();
}

// Usage
try {
    const result = await processDocument(fileInput.files[0], 'invoice');
    console.log('Extracted data:', result.extracted_data);
    console.log('Validations:', result.validation.checks);
} catch (error) {
    console.error('Error:', error.message);
}
```

## Performance Tips

1. **Single-page documents** process faster (1-2 seconds)
2. **Batch uploads** - Process documents sequentially, not parallel (API rate limits)
3. **Caching** - Store results for repeated queries on same document
4. **Compression** - JPEG compression reduces file size but may hurt OCR quality
