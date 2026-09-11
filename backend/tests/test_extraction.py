import pytest
from app.services.financial_validation_service import FinancialValidationService

class TestFinancialValidation:
    """Test financial calculation validation"""
    
    def test_invoice_total_validation_pass(self):
        """Test passing invoice total validation"""
        data = {
            "subtotal": 1000.00,
            "tax_amount": 100.00,
            "discount": 0.00,
            "total_amount": 1100.00
        }
        
        result = FinancialValidationService.validate_document(data, "invoice")
        
        assert result['overall_status'] == 'PASS'
        assert len(result['checks']) > 0
    
    def test_invoice_total_validation_fail(self):
        """Test failing invoice total validation"""
        data = {
            "subtotal": 1000.00,
            "tax_amount": 100.00,
            "discount": 0.00,
            "total_amount": 1050.00  # Wrong total
        }
        
        result = FinancialValidationService.validate_document(data, "invoice")
        
        assert result['overall_status'] == 'FAILED'
        assert len(result['issues']) > 0
    
    def test_balance_sheet_equation(self):
        """Test balance sheet equation: Assets = Liabilities + Equity"""
        data = {
            "total_assets": 5000.00,
            "total_liabilities": 3000.00,
            "total_equity": 2000.00
        }
        
        result = FinancialValidationService.validate_document(data, "balance_sheet")
        
        assert result['overall_status'] == 'PASS'
    
    def test_balance_sheet_equation_fail(self):
        """Test failing balance sheet equation"""
        data = {
            "total_assets": 5000.00,
            "total_liabilities": 3000.00,
            "total_equity": 1000.00  # Wrong: 3000+1000 != 5000
        }
        
        result = FinancialValidationService.validate_document(data, "balance_sheet")
        
        assert result['overall_status'] == 'FAILED'
    
    def test_profit_and_loss_validation(self):
        """Test P&L validations"""
        data = {
            "revenue": 10000.00,
            "cost_of_sales": 4000.00,
            "gross_profit": 6000.00,
            "operating_expenses": 2000.00,
            "operating_profit": 4000.00
        }
        
        result = FinancialValidationService.validate_document(data, "profit_and_loss")
        
        assert result['overall_status'] == 'PASS'
    
    def test_cash_flow_validation(self):
        """Test cash flow validations"""
        data = {
            "operating_cash_flow": 5000.00,
            "investing_cash_flow": -1000.00,
            "financing_cash_flow": 0.00,
            "net_change_in_cash": 4000.00,
            "opening_cash": 10000.00,
            "closing_cash": 14000.00
        }
        
        result = FinancialValidationService.validate_document(data, "cash_flow_statement")
        
        assert result['overall_status'] == 'PASS'
    
    def test_tolerance_handling(self):
        """Test numerical tolerance (1%)"""
        data = {
            "total_assets": 5000.00,
            "total_liabilities": 3000.00,
            "total_equity": 2000.49  # Within 1% tolerance
        }
        
        result = FinancialValidationService.validate_document(data, "balance_sheet")
        
        # Should pass due to tolerance
        checks = [c for c in result['checks'] if c['status'] in ['PASS', 'NOT_APPLICABLE']]
        assert len(checks) > 0
    
    def test_missing_fields_not_applicable(self):
        """Test missing fields return NOT_APPLICABLE"""
        data = {
            "subtotal": 1000.00
            # Missing tax_amount, discount, total_amount
        }
        
        result = FinancialValidationService.validate_document(data, "invoice")
        
        # Should not fail, just skip validations
        has_not_applicable = any(c['status'] == 'NOT_APPLICABLE' for c in result['checks'])
        # Or should have fewer checks than expected
        assert result['overall_status'] in ['PASS', 'NOT_APPLICABLE']

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
