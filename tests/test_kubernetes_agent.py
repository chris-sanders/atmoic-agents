import instructor
import pytest
from unittest.mock import Mock, patch, MagicMock
from atomic_agents.agents.base_agent import BaseAgentConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from tools.kubectl_tool import KubectlTool, KubectlOutputSchema
from agents.kubernetes import KubernetesAgent, KubernetesAgentInputSchema, KubernetesAgentOutputSchema

#@pytest.fixture
#def mock_kubectl_tool():
#    mock_tool = Mock(spec=KubectlTool)
#    mock_tool.run.return_value = KubectlOutputSchema(output="Mock kubectl output", error=None)
#    return mock_tool

@pytest.fixture(autouse=True)
def mock_instructor():
    with patch('agents.kubernetes.instructor.from_openai', autospec=True) as mock_from_openai:
        mock_instructor_instance = MagicMock(spec=instructor.Instructor)
        mock_from_openai.return_value = mock_instructor_instance
        yield mock_instructor_instance

@pytest.fixture(autouse=True)
def mock_kubernetes_openai():
    with patch('agents.kubernetes.OpenAI') as MockOpenAI:
        yield MockOpenAI

#@pytest.fixture
#def kubernetes_agent(mock_kubectl_tool):
#    #config = BaseAgentConfig(
#    #    tools=[mock_kubectl_tool]
#    #)
#    return KubernetesAgent()

def test_kubernetes_agent_initialization():
    kubernetes_agent = KubernetesAgent()
    assert isinstance(kubernetes_agent, KubernetesAgent)
    assert kubernetes_agent.model == "gpt-4o-mini"
    assert len(kubernetes_agent.config.tools) == 1
    assert isinstance(kubernetes_agent.config.tools[0], Mock)  # Because we're using a mock KubectlTool

#def test_kubernetes_agent_run_without_tool_call(kubernetes_agent, mock_openai_client):
#    input_data = KubernetesAgentInputSchema(query="What is Kubernetes?")
#    result = kubernetes_agent.run(input_data)
#
#    assert isinstance(result, KubernetesAgentOutputSchema)
#    assert result.response == "Test response"
#    assert len(result.kubectl_commands) == 0
#    assert len(result.kubectl_outputs) == 0
#    mock_openai_client.chat.completions.create.assert_called_once()
#
#def test_kubernetes_agent_run_with_tool_call(kubernetes_agent, mock_openai_client, mock_kubectl_tool):
#    mock_openai_client.chat.completions.create.return_value.choices[0].message.tool_calls = [
#        Mock(function=Mock(name="kubectl_tool", arguments='{"command": "get pods"}'))
#    ]
#    mock_openai_client.chat.completions.create.return_value.choices[0].message.content = "Pods information"
#
#    input_data = KubernetesAgentInputSchema(query="List all pods")
#    result = kubernetes_agent.run(input_data)
#
#    assert isinstance(result, KubernetesAgentOutputSchema)
#    assert result.response == "Pods information"
#    assert len(result.kubectl_commands) == 1
#    assert result.kubectl_commands[0] == "get pods"
#    assert len(result.kubectl_outputs) == 1
#    assert result.kubectl_outputs[0].output == "Mock kubectl output"
#    mock_kubectl_tool.run.assert_called_once()
#
#def test_kubernetes_agent_run_with_multiple_tool_calls(kubernetes_agent, mock_openai_client, mock_kubectl_tool):
#    # First call with tool use
#    mock_openai_client.chat.completions.create.side_effect = [
#        Mock(choices=[Mock(message=Mock(
#            content="Checking pods",
#            tool_calls=[Mock(function=Mock(name="kubectl_tool", arguments='{"command": "get pods"}'))]
#        ))]),
#        # Second call, asking for more info
#        Mock(choices=[Mock(message=Mock(
#            content="Checking services",
#            tool_calls=[Mock(function=Mock(name="kubectl_tool", arguments='{"command": "get services"}'))]
#        ))]),
#        # Final call, no more tool calls
#        Mock(choices=[Mock(message=Mock(content="Final response", tool_calls=[]))])
#    ]
#
#    input_data = KubernetesAgentInputSchema(query="Describe cluster state")
#    result = kubernetes_agent.run(input_data)
#
#    assert isinstance(result, KubernetesAgentOutputSchema)
#    assert result.response == "Final response"
#    assert len(result.kubectl_commands) == 2
#    assert result.kubectl_commands == ["get pods", "get services"]
#    assert len(result.kubectl_outputs) == 2
#    assert all(output.output == "Mock kubectl output" for output in result.kubectl_outputs)
#    assert mock_kubectl_tool.run.call_count == 2
#
#def test_kubernetes_agent_run_with_kubectl_error(kubernetes_agent, mock_openai_client, mock_kubectl_tool):
#    mock_openai_client.chat.completions.create.return_value.choices[0].message.tool_calls = [
#        Mock(function=Mock(name="kubectl_tool", arguments='{"command": "get pods"}'))
#    ]
#    mock_kubectl_tool.run.return_value = KubectlOutputSchema(output=None, error="Command failed")
#
#    input_data = KubernetesAgentInputSchema(query="List all pods")
#    result = kubernetes_agent.run(input_data)
#
#    assert isinstance(result, KubernetesAgentOutputSchema)
#    assert len(result.kubectl_commands) == 1
#    assert result.kubectl_commands[0] == "get pods"
#    assert len(result.kubectl_outputs) == 1
#    assert result.kubectl_outputs[0].error == "Command failed"
#
#@patch('agents.kubernetes_agent.console.print')
#def test_kubernetes_agent_console_output(mock_console_print, kubernetes_agent, mock_openai_client, mock_kubectl_tool):
#    mock_openai_client.chat.completions.create.return_value.choices[0].message.tool_calls = [
#        Mock(function=Mock(name="kubectl_tool", arguments='{"command": "get pods"}'))
#    ]
#
#    input_data = KubernetesAgentInputSchema(query="List all pods")
#    kubernetes_agent.run(input_data)
#
#    # Check that console.print was called with expected messages
#    mock_console_print.assert_any_call("Generating response...", style="bold blue")
#    mock_console_print.assert_any_call("Executing kubectl command: get pods", style="bold yellow")
#    mock_console_print.assert_any_call("kubectl output:\nMock kubectl output", style="green")
#    mock_console_print.assert_any_call("Generating final response...", style="bold blue")
