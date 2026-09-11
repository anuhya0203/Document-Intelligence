import logging
from typing import Dict, Any, List
from app.core.config import settings

logger = logging.getLogger(__name__)


class FinancialValidationService:
    """Validate extracted financial document data."""

    TOLERANCE = settings.NUMERIC_TOLERANCE

    @staticmethod
    def validate_document(
        extracted_data: Dict[str, Any],
        document_type: str
    ) -> Dict[str, Any]:
        """Run validations based on document type."""

        if not extracted_data:
            return {
                "checks": [],
                "overall_status": "FAILED",
                "issues": ["No extracted data available for validation"]
            }

        document_type = document_type.lower()
        checks: List[Dict[str, Any]] = []
        issues: List[str] = []

        try:
            if document_type == "invoice":
                checks.extend(
                    FinancialValidationService._validate_invoice(extracted_data)
                )

            elif document_type == "balance_sheet":
                checks.extend(
                    FinancialValidationService._validate_balance_sheet(extracted_data)
                )

            elif document_type == "profit_and_loss":
                checks.extend(
                    FinancialValidationService._validate_profit_and_loss(extracted_data)
                )

            elif document_type == "cash_flow_statement":
                checks.extend(
                    FinancialValidationService._validate_cash_flow(extracted_data)
                )

        except Exception as e:
            logger.error(f"Financial validation error: {e}")
            issues.append(str(e))

        if any(check["status"] == "FAIL" for check in checks):
            overall_status = "FAILED"
        elif issues:
            overall_status = "FAILED"
        else:
            overall_status = "PASS"

        return {
            "checks": checks,
            "overall_status": overall_status,
            "issues": issues
        }

    # ------------------------------------------------------------------
    # Invoice Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_invoice(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        checks = []

        line_items = data.get("line_items", [])

        reconciliation_issues = []

        for item in line_items:
            qty = item.get("quantity") or 0
            unit_price = item.get("unit_price") or 0
            amount = item.get("amount") or 0

            calculated = round(qty * unit_price, 2)

            if abs(calculated - amount) > FinancialValidationService.TOLERANCE:
                reconciliation_issues.append({
                    "item": item.get("description") or item.get("item_description"),
                    "expected": calculated,
                    "reported": amount
                })

        checks.append({
            "name": "line_items_reconciliation",
            "formula": "quantity × unit_price ≈ amount",
            "status": "PASS" if not reconciliation_issues else "FAIL",
            "issues": reconciliation_issues if reconciliation_issues else None
        })

        subtotal = float(data.get("subtotal") or 0)
        tax = float(data.get("tax_amount") or 0)
        discount = float(data.get("discount") or 0)
        total = float(data.get("total_amount") or 0)

        calculated_total = round(subtotal + tax - discount, 2)
        variance = round(abs(calculated_total - total), 2)

        checks.append({
            "name": "invoice_total_check",
            "formula": "subtotal + tax_amount - discount",
            "operands": {
                "subtotal": subtotal,
                "tax_amount": tax,
                "discount": discount
            },
            "calculated_value": calculated_total,
            "reported_value": total,
            "variance": variance,
            "status": "PASS"
            if variance <= FinancialValidationService.TOLERANCE
            else "FAIL"
        })

        return checks

    # ------------------------------------------------------------------
    # Balance Sheet Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_balance_sheet(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        checks = []

        liabilities_total = (
            data.get("capital_and_liabilities", {})
                .get("total", {})
                .get("as_at_31_mar_18")
        )

        assets_total = (
            data.get("assets", {})
                .get("total", {})
                .get("as_at_31_mar_18")
        )

        if liabilities_total is not None and assets_total is not None:
            variance = abs(assets_total - liabilities_total)

            checks.append({
                "name": "balance_sheet_equation",
                "formula": "Total Assets = Total Capital and Liabilities",
                "reported_assets": assets_total,
                "reported_liabilities": liabilities_total,
                "variance": variance,
                "status": "PASS"
                if variance <= FinancialValidationService.TOLERANCE
                else "FAIL"
            })

        asset_items = data.get("assets", {}).get("line_items", [])
        asset_sum = sum(
            float(item.get("as_at_31_mar_18") or 0)
            for item in asset_items
        )

        if assets_total is not None:
            variance = abs(asset_sum - assets_total)

            checks.append({
                "name": "assets_sum_check",
                "formula": "Sum(asset line items) = Total Assets",
                "calculated_value": asset_sum,
                "reported_value": assets_total,
                "variance": variance,
                "status": "PASS"
                if variance <= FinancialValidationService.TOLERANCE
                else "FAIL"
            })

        liability_items = (
            data.get("capital_and_liabilities", {})
                .get("line_items", [])
        )

        liability_sum = sum(
            float(item.get("as_at_31_mar_18") or 0)
            for item in liability_items
        )

        if liabilities_total is not None:
            variance = abs(liability_sum - liabilities_total)

            checks.append({
                "name": "liabilities_sum_check",
                "formula": "Sum(capital/liability line items) = Total Capital and Liabilities",
                "calculated_value": liability_sum,
                "reported_value": liabilities_total,
                "variance": variance,
                "status": "PASS"
                if variance <= FinancialValidationService.TOLERANCE
                else "FAIL"
            })

        return checks

    # ------------------------------------------------------------------
    # Profit & Loss Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_profit_and_loss(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        checks = []

        revenue = float(data.get("revenue") or 0)
        cost = float(data.get("cost_of_sales") or 0)
        gross_profit = data.get("gross_profit")

        if gross_profit is not None:
            calculated = round(revenue - cost, 2)
            variance = abs(calculated - float(gross_profit))

            checks.append({
                "name": "gross_profit_check",
                "formula": "Revenue - Cost of Sales",
                "calculated_value": calculated,
                "reported_value": gross_profit,
                "variance": variance,
                "status": "PASS"
                if variance <= FinancialValidationService.TOLERANCE
                else "FAIL"
            })

        return checks

    # ------------------------------------------------------------------
    # Cash Flow Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_cash_flow(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        checks = []

        opening = float(data.get("opening_cash") or 0)
        operating = float(data.get("operating_cash_flow") or 0)
        investing = float(data.get("investing_cash_flow") or 0)
        financing = float(data.get("financing_cash_flow") or 0)
        fx = float(data.get("fx_translation_adjustments") or 0)

        reported_closing = data.get("closing_cash")

        if reported_closing is not None:
            calculated = round(
                opening + operating + investing + financing + fx,
                2
            )

            variance = abs(calculated - float(reported_closing))

            checks.append({
                "name": "cash_flow_reconciliation",
                "formula": "Opening + Operating + Investing + Financing + FX = Closing",
                "calculated_value": calculated,
                "reported_value": reported_closing,
                "variance": variance,
                "status": "PASS"
                if variance <= FinancialValidationService.TOLERANCE
                else "FAIL"
            })

        return checks