import pytest
import subprocess
from unittest.mock import patch, MagicMock
from tools.kubectl_tool import KubectlTool, KubectlInputSchema, KubectlOutputSchema, KubectlToolConfig

@pytest.fixture
def kubectl_tool():
    return KubectlTool()

def test_kubectl_tool_initialization(kubectl_tool):
    assert isinstance(kubectl_tool, KubectlTool)
    assert kubectl_tool.allowed_commands == ["get", "describe", "logs"]

def test_kubectl_tool_config():
    custom_config = KubectlToolConfig(allowed_commands=["get", "logs"])
    tool = KubectlTool(config=custom_config)
    assert tool.allowed_commands == ["get", "logs"]

@pytest.mark.parametrize("command,expected_output,expected_error", [
    ("kubectl get pods", "No resources found in default namespace.", None),
    ("kubectl describe pod my-pod", "Pod 'my-pod' details", None),
    ("kubectl logs my-pod", "Log output for my-pod", None),
    ("kubectl delete pod my-pod", "", "Command 'delete' is not allowed or invalid."),
])
@patch('subprocess.run')
def test_kubectl_tool_run(mock_run, kubectl_tool, command, expected_output, expected_error):
    mock_result = MagicMock()
    mock_result.stdout = expected_output
    mock_result.stderr = ""
    mock_run.return_value = mock_result

    input_data = KubectlInputSchema(command=command)
    result = kubectl_tool.run(input_data)

    assert isinstance(result, KubectlOutputSchema)
    if expected_error:
        assert result.error == expected_error
        assert result.output == ""
    else:
        assert result.output == expected_output
        assert result.error is None

@patch('subprocess.run')
def test_kubectl_tool_run_subprocess_error(mock_run, kubectl_tool):
    mock_run.side_effect = subprocess.CalledProcessError(1, "kubectl", stderr="Command failed")
    
    input_data = KubectlInputSchema(command="kubectl get pods")
    result = kubectl_tool.run(input_data)
    
    assert isinstance(result, KubectlOutputSchema)
    assert result.error == "Error executing command: Command failed"
    assert result.output == ""

def test_kubectl_tool_invalid_command(kubectl_tool):
    input_data = KubectlInputSchema(command="kubectl invalid_command")
    result = kubectl_tool.run(input_data)
    
    assert isinstance(result, KubectlOutputSchema)
    assert result.error == "Command 'invalid_command' is not allowed or invalid."
    assert result.output == ""
