# tests/test_kubectl.py
import pytest
import subprocess
from tools.kubectl import KubectlTool, KubectlInputSchema, KubectlToolConfig

@pytest.fixture
def kubectl_tool():
    return KubectlTool(config=KubectlToolConfig())

def test_kubectl_disallows_invalid_commands(kubectl_tool):
    result = kubectl_tool.run(KubectlInputSchema(command="kubectl delete pod test"))
    assert result.error is not None
    assert "not allowed" in result.error

def test_kubectl_allows_valid_commands(kubectl_tool, mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.stdout = "pod/test-pod running"
    mock_run.return_value.stderr = ""
    
    result = kubectl_tool.run(KubectlInputSchema(command="kubectl get pod test-pod"))
    assert result.error is None
    assert "test-pod running" in result.output

def test_kubectl_handles_errors(kubectl_tool, mocker):
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = subprocess.CalledProcessError(1, [], stderr="pod not found")
    
    result = kubectl_tool.run(KubectlInputSchema(command="kubectl get pod nonexistent"))
    assert result.error is not None
    assert "pod not found" in result.error

def test_custom_allowed_commands():
    config = KubectlToolConfig(allowed_commands=["get"])
    tool = KubectlTool(config=config)
    
    result = tool.run(KubectlInputSchema(command="kubectl describe pod test"))
    assert result.error is not None
    assert "not allowed" in result.error
