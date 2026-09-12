from google import genai
from app.core.config import settings


class DocumentClassifierService:
    """Classifies uploaded documents before extraction."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    def classify(self, document_text: str) -> str:
        prompt = """
You are a financial document classifier.

Return ONLY one of these values:
invoice
balance_sheet
profit_and_loss
cash_flow_statement

No explanation.
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=f"{prompt}\n\nDOCUMENT:\n{document_text[:4000]}"
        )

        return response.text.strip().lower()