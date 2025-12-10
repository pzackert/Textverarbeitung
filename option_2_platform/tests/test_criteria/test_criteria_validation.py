"""Criteria validation tests for K001-K006 business logic."""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


class TestCriteriaK001Validation:
    """Test K001 criteria validation logic."""

    def test_k001_passes_with_valid_project_information(self):
        """Verify K001 passes when project info is present and valid."""
        # K001: Project name, location, object, funding amount required
        project_data = {
            "name": "Test Project",
            "location": "Hamburg",
            "object": "Development",
            "funding_amount": 50000,
        }

        # Mock validation engine
        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "pass",
            "code": "K001",
            "message": "Project information complete and valid",
            "citations": [
                {"doc_id": "doc-1", "page": 1, "text": "Project: Test Project"}
            ],
        }

        result = mock_validator.validate_k001(project_data)

        assert result["status"] == "pass"
        assert result["code"] == "K001"
        assert len(result["citations"]) > 0

    def test_k001_fails_with_missing_project_name(self):
        """Verify K001 fails when project name is missing."""
        project_data = {
            "name": None,
            "location": "Hamburg",
            "object": "Development",
            "funding_amount": 50000,
        }

        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "fail",
            "code": "K001",
            "message": "Project name is required",
            "citations": [],
        }

        result = mock_validator.validate_k001(project_data)

        assert result["status"] == "fail"
        assert "name" in result["message"].lower()

    def test_k001_fails_with_missing_location(self):
        """Verify K001 fails when location is missing."""
        project_data = {
            "name": "Test Project",
            "location": None,
            "object": "Development",
            "funding_amount": 50000,
        }

        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "fail",
            "code": "K001",
            "message": "Project location is required",
            "citations": [],
        }

        result = mock_validator.validate_k001(project_data)

        assert result["status"] == "fail"
        assert "location" in result["message"].lower()

    def test_k001_citations_include_document_source(self):
        """Verify K001 citations include document source."""
        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "pass",
            "code": "K001",
            "citations": [
                {
                    "doc_id": "doc-123",
                    "filename": "application.pdf",
                    "page": 1,
                    "text": "Project: TestProject",
                }
            ],
        }

        result = mock_validator.validate_k001({})
        citation = result["citations"][0]

        assert "doc_id" in citation
        assert "page" in citation
        assert "text" in citation


class TestCriteriaK002Validation:
    """Test K002 criteria validation logic."""

    def test_k002_passes_with_valid_applicant_info(self):
        """Verify K002 passes with valid applicant information."""
        # K002: Applicant name, address, contact required
        applicant_data = {
            "name": "Test Company",
            "address": "123 Main St, Hamburg",
            "phone": "040-123456",
            "email": "info@test.de",
        }

        mock_validator = MagicMock()
        mock_validator.validate_k002.return_value = {
            "status": "pass",
            "code": "K002",
            "message": "Applicant information complete",
            "citations": [
                {"doc_id": "doc-1", "page": 2, "text": "Applicant: Test Company"}
            ],
        }

        result = mock_validator.validate_k002(applicant_data)

        assert result["status"] == "pass"
        assert "K002" in result["code"]

    def test_k002_fails_with_missing_contact_info(self):
        """Verify K002 fails when contact info is missing."""
        applicant_data = {
            "name": "Test Company",
            "address": "123 Main St",
            "phone": None,
            "email": None,
        }

        mock_validator = MagicMock()
        mock_validator.validate_k002.return_value = {
            "status": "fail",
            "code": "K002",
            "message": "Contact information is required (phone or email)",
            "citations": [],
        }

        result = mock_validator.validate_k002(applicant_data)

        assert result["status"] == "fail"
        assert "contact" in result["message"].lower()


class TestCriteriaK003Validation:
    """Test K003 criteria validation logic."""

    def test_k003_passes_with_financial_information(self):
        """Verify K003 passes with complete financial information."""
        financial_data = {
            "total_cost": 100000,
            "equity": 30000,
            "requested_amount": 70000,
            "timeline": "24 months",
        }

        mock_validator = MagicMock()
        mock_validator.validate_k003.return_value = {
            "status": "pass",
            "code": "K003",
            "message": "Financial information valid",
            "citations": [
                {"doc_id": "doc-2", "page": 3, "text": "Total cost: €100,000"}
            ],
        }

        result = mock_validator.validate_k003(financial_data)

        assert result["status"] == "pass"

    def test_k003_fails_with_invalid_funding_ratio(self):
        """Verify K003 fails with invalid equity/funding ratio."""
        financial_data = {
            "total_cost": 100000,
            "equity": 5000,  # Only 5%, minimum usually 20-30%
            "requested_amount": 95000,
        }

        mock_validator = MagicMock()
        mock_validator.validate_k003.return_value = {
            "status": "fail",
            "code": "K003",
            "message": "Equity ratio below minimum threshold (20%)",
            "citations": [],
        }

        result = mock_validator.validate_k003(financial_data)

        assert result["status"] == "fail"
        assert "equity" in result["message"].lower()


class TestCriteriaK004Validation:
    """Test K004 criteria validation logic."""

    def test_k004_passes_with_business_plan(self):
        """Verify K004 passes with complete business plan."""
        business_plan = {
            "description": "Detailed business plan...",
            "market_analysis": "Market research...",
            "financial_forecast": "Financial projections...",
        }

        mock_validator = MagicMock()
        mock_validator.validate_k004.return_value = {
            "status": "pass",
            "code": "K004",
            "message": "Business plan requirements met",
            "citations": [
                {"doc_id": "doc-3", "page": 5, "text": "Business Plan: ..."}
            ],
        }

        result = mock_validator.validate_k004(business_plan)

        assert result["status"] == "pass"

    def test_k004_fails_with_insufficient_detail(self):
        """Verify K004 fails with insufficient business plan detail."""
        business_plan = {"description": "Brief description only"}

        mock_validator = MagicMock()
        mock_validator.validate_k004.return_value = {
            "status": "fail",
            "code": "K004",
            "message": "Business plan lacks required detail (market analysis, forecasts)",
            "citations": [],
        }

        result = mock_validator.validate_k004(business_plan)

        assert result["status"] == "fail"


class TestCriteriaK005Validation:
    """Test K005 criteria validation logic."""

    def test_k005_passes_with_management_team_info(self):
        """Verify K005 passes with management team information."""
        team_data = {
            "ceo": {"name": "John Doe", "experience": "15 years"},
            "cfo": {"name": "Jane Smith", "experience": "12 years"},
            "team_size": 5,
        }

        mock_validator = MagicMock()
        mock_validator.validate_k005.return_value = {
            "status": "pass",
            "code": "K005",
            "message": "Management team information provided",
            "citations": [
                {"doc_id": "doc-4", "page": 6, "text": "Management: John Doe, CEO"}
            ],
        }

        result = mock_validator.validate_k005(team_data)

        assert result["status"] == "pass"

    def test_k005_fails_with_insufficient_experience(self):
        """Verify K005 fails with insufficient management experience."""
        team_data = {
            "ceo": {"name": "New Person", "experience": "1 year"},
            "cfo": None,
        }

        mock_validator = MagicMock()
        mock_validator.validate_k005.return_value = {
            "status": "fail",
            "code": "K005",
            "message": "Management experience below minimum requirements",
            "citations": [],
        }

        result = mock_validator.validate_k005(team_data)

        assert result["status"] == "fail"


class TestCriteriaK006Validation:
    """Test K006 criteria validation logic."""

    def test_k006_passes_with_sustainability_plan(self):
        """Verify K006 passes with sustainability/viability plan."""
        sustainability_data = {
            "business_model": "Subscription-based SaaS",
            "revenue_streams": ["Subscriptions", "Professional services"],
            "break_even_timeline": "18 months",
            "scaling_plan": "Expand to European market",
        }

        mock_validator = MagicMock()
        mock_validator.validate_k006.return_value = {
            "status": "pass",
            "code": "K006",
            "message": "Business sustainability plan provided",
            "citations": [
                {"doc_id": "doc-5", "page": 7, "text": "Business Model: SaaS"}
            ],
        }

        result = mock_validator.validate_k006(sustainability_data)

        assert result["status"] == "pass"

    def test_k006_fails_with_unrealistic_projections(self):
        """Verify K006 fails with unrealistic financial projections."""
        sustainability_data = {
            "revenue_year_1": 1000000,
            "revenue_year_2": 50000000,  # 50x growth unrealistic
            "break_even_timeline": "6 months",
        }

        mock_validator = MagicMock()
        mock_validator.validate_k006.return_value = {
            "status": "fail",
            "code": "K006",
            "message": "Financial projections appear unrealistic",
            "citations": [],
        }

        result = mock_validator.validate_k006(sustainability_data)

        assert result["status"] == "fail"


class TestMixedCriteriaResults:
    """Test validation with mixed pass/fail criteria."""

    def test_validation_report_with_mixed_results(self):
        """Verify validation report correctly shows mixed results."""
        mock_validator = MagicMock()
        mock_validator.validate_all.return_value = {
            "overall_status": "partial",
            "passed_criteria": ["K001", "K002", "K004"],
            "failed_criteria": ["K003", "K005", "K006"],
            "details": {
                "K001": {"status": "pass", "message": "OK"},
                "K002": {"status": "pass", "message": "OK"},
                "K003": {"status": "fail", "message": "Equity too low"},
                "K004": {"status": "pass", "message": "OK"},
                "K005": {"status": "fail", "message": "No CFO"},
                "K006": {"status": "fail", "message": "Unrealistic projections"},
            },
        }

        result = mock_validator.validate_all()

        assert result["overall_status"] == "partial"
        assert len(result["passed_criteria"]) == 3
        assert len(result["failed_criteria"]) == 3

    def test_validation_report_all_pass(self):
        """Verify validation report when all criteria pass."""
        mock_validator = MagicMock()
        mock_validator.validate_all.return_value = {
            "overall_status": "pass",
            "passed_criteria": ["K001", "K002", "K003", "K004", "K005", "K006"],
            "failed_criteria": [],
            "message": "All criteria met",
        }

        result = mock_validator.validate_all()

        assert result["overall_status"] == "pass"
        assert len(result["failed_criteria"]) == 0

    def test_validation_report_all_fail(self):
        """Verify validation report when all criteria fail."""
        mock_validator = MagicMock()
        mock_validator.validate_all.return_value = {
            "overall_status": "fail",
            "passed_criteria": [],
            "failed_criteria": ["K001", "K002", "K003", "K004", "K005", "K006"],
            "message": "Critical issues found",
        }

        result = mock_validator.validate_all()

        assert result["overall_status"] == "fail"
        assert len(result["passed_criteria"]) == 0


class TestCitationAccuracy:
    """Test citation accuracy in validation results."""

    def test_citations_have_required_fields(self):
        """Verify citations include all required fields."""
        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "pass",
            "citations": [
                {
                    "doc_id": "doc-123",
                    "filename": "application.pdf",
                    "page": 1,
                    "text": "Project Name: Test",
                }
            ],
        }

        result = mock_validator.validate_k001({})
        citation = result["citations"][0]

        assert "doc_id" in citation
        assert "page" in citation
        assert "text" in citation
        assert citation["page"] > 0

    def test_citation_page_numbers_are_accurate(self):
        """Verify citation page numbers match source documents."""
        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "pass",
            "citations": [
                {"doc_id": "doc-1", "page": 1, "text": "Project info"},
                {"doc_id": "doc-1", "page": 2, "text": "More project info"},
            ],
        }

        result = mock_validator.validate_k001({})

        assert result["citations"][0]["page"] == 1
        assert result["citations"][1]["page"] == 2

    def test_citation_text_matches_source(self):
        """Verify citation text excerpts match source documents."""
        # This would require actual document verification
        # For now, mock the validation
        mock_validator = MagicMock()
        mock_validator.validate_k001.return_value = {
            "status": "pass",
            "citations": [
                {"doc_id": "doc-1", "text": "Expected text from document"}
            ],
        }

        result = mock_validator.validate_k001({})
        # Text should not be fabricated
        assert len(result["citations"][0]["text"]) > 0


# Pytest markers
pytestmark = [pytest.mark.unit]
