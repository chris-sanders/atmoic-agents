import subprocess
from typing import Optional
from pydantic import Field
from atomic_agents.agents.base_agent import BaseIOSchema
from atomic_agents.lib.base.base_tool import BaseTool, BaseToolConfig

class KubectlInputSchema(BaseIOSchema):
    """Input schema for kubectl commands"""
    command: str = Field(..., description="The kubectl command to execute")

class KubectlOutputSchema(BaseIOSchema):
    """Output schema for kubectl execution results"""
    output: str = Field("", description="Command output if successful")
    error: Optional[str] = Field(None, description="Error message if command failed")

class KubectlToolConfig(BaseToolConfig):
    """Configuration for kubectl tool"""
    allowed_commands: list[str] = Field(
        default=["get", "describe", "logs"],
        description="List of allowed kubectl commands"
    )

class KubectlTool(BaseTool):
    """Tool for executing kubectl commands"""
    input_schema = KubectlInputSchema
    output_schema = KubectlOutputSchema

    def __init__(self, config: KubectlToolConfig = KubectlToolConfig()):
        super().__init__(config)
        self.allowed_commands = config.allowed_commands

    def run(self, params: KubectlInputSchema) -> KubectlOutputSchema:
        command_parts = params.command.split()
        if command_parts[0] == "kubectl":
            command_parts = command_parts[1:]
        
        if not command_parts or command_parts[0] not in self.allowed_commands:
            return KubectlOutputSchema(
                error=f"Command '{command_parts[0]}' is not allowed. Allowed commands: {self.allowed_commands}"
            )

        try:
            result = subprocess.run(
                ["kubectl"] + command_parts,
                capture_output=True,
                text=True,
                check=True
            )
            return KubectlOutputSchema(output=result.stdout.strip())
        except subprocess.CalledProcessError as e:
            return KubectlOutputSchema(error=str(e.stderr))
