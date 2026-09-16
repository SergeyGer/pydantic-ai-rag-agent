from src.agent import agent
from src.models import SearchResult


def test_agent_uses_structured_output():
    # Regression guard: the agent must return SearchResult, not a plain string.
    assert agent.output_type is SearchResult


def test_agent_registers_expected_tools():
    tools = set(agent._function_toolset.tools.keys())
    assert {
        "get_company_info",
        "get_policy",
        "get_faq",
        "get_product_data",
        "load_web_content",
    } <= tools
