import os
import subprocess
from typing import Optional

from pydantic import Field
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig

class KubectlInputSchema(BaseIOSchema):
    """
    Captures the full kubectl command for execution.
    """
    command: str = Field(..., description="The full kubectl command to execute.")

class KubectlOutputSchema(BaseIOSchema):
    """
    Represents the output of a kubectl command execution.
    """
    output: str = Field("", description="The output of the kubectl command.")
    error: Optional[str] = Field(None, description="Error message if the command failed.")

class KubectlToolConfig(BaseToolConfig):
    """
    Configuration for the KubectlTool.
    """
    allowed_commands: list[str] = Field(
        default=["get", "describe", "logs"],
        description="List of allowed kubectl commands."
    )

class KubectlTool(BaseTool):
    """
    Tool for executing kubectl commands in a Kubernetes cluster.
    """

    input_schema = KubectlInputSchema
    output_schema = KubectlOutputSchema

    def __init__(self, config: KubectlToolConfig = KubectlToolConfig()):
        super().__init__(config)
        self.allowed_commands = config.allowed_commands

    def run(self, params: KubectlInputSchema) -> KubectlOutputSchema:
        """
        Executes the kubectl command and returns the output.
        """
        command_parts = params.command.split()
        if command_parts[0] == "kubectl":
            command_parts = command_parts[1:]
        
        if not command_parts or command_parts[0] not in self.allowed_commands:
            return KubectlOutputSchema(error=f"Command '{command_parts[0]}' is not allowed or invalid.")

        full_command = ["kubectl"] + command_parts

        try:
            result = subprocess.run(
                full_command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=dict(os.environ, KUBECONFIG=os.getenv("KUBECONFIG", ""))
            )
            return KubectlOutputSchema(output=result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return KubectlOutputSchema(error=f"Error executing command: {e.stderr.strip()}")

if __name__ == "__main__":
    from rich.console import Console

    console = Console()
    kubectl_tool = KubectlTool()

    input_data = KubectlInputSchema(command="kubectl get pods -A")

    try:
        output = kubectl_tool.run(input_data)
        if output.error:
            console.print(f"[red]Error:[/red] {output.error}")
        else:
            console.print(f"[green]Output:[/green]\n{output.output}")
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
