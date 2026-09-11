import logging
import json
from typing import Dict, Any

from google import genai
from app.core.config import settings

logger = logging.getLogger(__name__)


class ExtractionService:
    """Extract structured data from documents using Gemini."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    def extract_fields(
        self,
        document_text: str,
        document_type: str,
        page_count: int
    ) -> Dict[str, Any]:
        """Extract all fields from document text using Gemini."""

        prompt = self._build_extraction_prompt(document_type, page_count)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=f"{prompt}\n\n=== DOCUMENT TEXT ===\n{document_text}"
            )

            return self._parse_extraction_response(response.text)

        except Exception as e:
            logger.error(f"Gemini extraction error: {e}")
            return {}

    def _build_extraction_prompt(self, document_type: str, page_count: int) -> str:
        base_prompt = f"""
You are an expert financial document extraction system.

Document Type: {document_type}
Pages: {page_count}

Rules:
- Return ONLY valid JSON.
- No markdown.
- No explanation.
- Do not hallucinate values.
- If a value is missing, return null.
- Extract ALL visible fields, totals, tables and line items.
- Include page_number for fields whenever possible.
"""

        prompts = {
            "invoice": """
Extract:
invoice_number, invoice_date, vendor_name, customer_name,
currency, subtotal, tax_amount, discount, total_amount,
payment_terms, due_date,
line_items (description, quantity, unit_price, amount),
and every other visible field.
""",
            "balance_sheet": """
Extract:
company_name, reporting_period, currency,
total_assets, total_liabilities, total_equity,
every visible asset, liability and equity line item,
comparative period values.
""",
            "profit_and_loss": """
Extract:
company_name, reporting_period, currency,
revenue, cost_of_sales, gross_profit,
operating_expenses, operating_profit,
tax, net_profit,
every income/expense line item,
comparative period values.
""",
            "cash_flow_statement": """
Extract:
company_name, reporting_period, currency,
operating_cash_flow,
investing_cash_flow,
financing_cash_flow,
opening_cash,
net_change_in_cash,
closing_cash,
fx_translation_adjustments,
every visible cash-flow line item,
comparative period values.
"""
        }

        return base_prompt + prompts.get(document_type, "")

    @staticmethod
    def _parse_extraction_response(response: str) -> Dict[str, Any]:
        """Safely parse Gemini JSON response."""

        try:
            response = response.strip()

            if response.startswith("```"):
                response = (
                    response.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            start = response.find("{")
            end = response.rfind("}")

            if start != -1 and end != -1:
                response = response[start:end + 1]

            return json.loads(response)

        except Exception as e:
            logger.error(f"JSON parsing error: {e}")
            return {}