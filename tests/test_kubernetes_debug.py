# tests/test_kubernetes_debug.py
import pytest
from agents.kubernetes.debug import KubernetesDebugAgent, DiagnosisResponse
from tools.kubectl import KubectlInputSchema
from atomic_agents.agents.base_agent import BaseAgentConfig
import instructor
from openai import OpenAI
from unittest.mock import MagicMock

@pytest.fixture
def mock_client(mocker):
    client = MagicMock(spec=instructor.Instructor)
    return client

def test_debug_agent_tool_response(mock_client):
    agent = KubernetesDebugAgent(
        BaseAgentConfig(
            client=mock_client,
            model="gpt-4",
            system_prompt="You are a Kubernetes expert..."
        )
    )
    
    # Mock a response that would be a kubectl command
    mock_response = {
        "command": "kubectl get pods -n default"
    }
    mock_client.chat.completions.create.return_value = mock_response
    
    response = agent.get_response()
    pytest.fail(f"""
        Response type: {type(response)}
        Response content: {response}
        Expected either KubectlInputSchema or DiagnosisResponse
    """)

def test_debug_agent_response_types(mock_client):
    agent = KubernetesDebugAgent(
        BaseAgentConfig(
            client=mock_client,
            model="gpt-4",
            system_prompt="You are a Kubernetes expert..."
        )
    )
    
    # Let's see what schemas are available
    print("\nAgent schemas:")
    print(f"Input schema: {agent.input_schema}")
    print(f"Output schema: {agent.output_schema}")
    
    # Try to understand how the Union type is handled
    if hasattr(agent.output_schema, 'openai_schema'):
        print("\nOpenAI schema:")
        print(agent.output_schema.openai_schema)
    assert True
