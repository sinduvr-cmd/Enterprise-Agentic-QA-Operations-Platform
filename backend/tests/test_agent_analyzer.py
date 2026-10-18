"""
Unit tests for Agent 1: Requirement Analyzer Agent.
"""
from backend.app.agents.requirement_analyzer import RequirementAnalyzerAgent


def test_requirement_analyzer_extraction():
    analyzer = RequirementAnalyzerAgent()
    title = "Stripe 3DS2 Challenge Step-Up"
    description = "As a cardholder, when initiating an online transaction over $250, I must complete a 3DS challenge."
    criteria = [
        "Transactions over $250 trigger OTP prompt",
        "Valid OTP authorizes charge",
        "Invalid OTP after 3 tries declines"
    ]

    result = analyzer.analyze(title=title, description=description, acceptance_criteria=criteria)

    assert result.sufficiency_score >= 6.0
    assert result.is_sufficient_for_test_generation is True
    assert len(result.functional_requirements) >= 1
    assert len(result.positive_scenarios) >= 1
    assert len(result.negative_scenarios) >= 1
    assert len(result.boundary_scenarios) >= 1
    assert len(result.edge_scenarios) >= 1
    assert "SCEN-01" in [s.scenario_id for s in result.positive_scenarios]
