import json
from typing import Optional, List
import instructor
from openai import OpenAI
from pydantic import Field
from atomic_agents.agents.base_agent import BaseIOSchema, BaseAgent, BaseAgentConfig
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from tools.kubectl_tool import KubectlTool, KubectlInputSchema, KubectlOutputSchema
from rich.console import Console

console = Console()

class KubernetesAgentInputSchema(BaseIOSchema):
    """This schema defines the input for the KubernetesAgent"""
    query: str = Field(..., description="A query about the Kubernetes cluster.")

class KubernetesAgentOutputSchema(BaseIOSchema):
    """This schema defines the output for the KubernetesAgent"""
    response: str = Field(..., description="The processed, human-readable response to the Kubernetes query.")
    kubectl_commands: List[str] = Field(default_factory=list, description="The kubectl commands used, if any.")
    kubectl_outputs: List[KubectlOutputSchema] = Field(default_factory=list, description="The raw outputs of the kubectl commands, if used.")

class KubernetesAgent(BaseAgent):
    def create_default_config(cls):
        return BaseAgentConfig(
            client=instructor.from_openai(OpenAI()),
            model="gpt-4o-mini",
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "You are a Kubernetes expert.",
                    "Your task is to help users explore and fix Kubernetes clusters.",
                ],
                steps=[
                    "You will receive a query about a Kubernetes cluster.",
                    "Use the kubectl tool to gather information about the cluster.",
                    "Provide a clear and concise response, focus on primary failure conditions",
                ],
                output_instructions=[
                    "Ensure your response is directly relevant to the query.",
                    "If you used kubectl, include the command and its output in your response.",
                    "Explain your reasoning for any recommendations referencing data you observed.",
                ],
            ),
            input_schema=KubernetesAgentInputSchema,
            output_schema=KubernetesAgentOutputSchema,
            tools=[KubectlTool()],
        )
    def __init__(self, config: Optional[BaseAgentConfig] = None):
        if config:
            merged_config = BaseAgentConfig(**{
                **self.create_default_config.dict(),
                **config.dict(exclude_unset=True)
            })
        else:
            merged_config = self.create_default_config()

        super().__init__(merged_config)

    def run(self, input_data: KubernetesAgentInputSchema) -> KubernetesAgentOutputSchema:
        messages = [
            {"role": "system", "content": self.config.system_prompt_generator.generate()},
            {"role": "user", "content": input_data.query}
        ]
        kubectl_commands = []
        kubectl_outputs = []

        while True:
            console.print("Generating response...", style="bold blue")
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages
            )

            content = response.choices[0].message.content
            tool_calls = response.choices[0].message.tool_calls

            if not tool_calls:
                break  # No more tool calls, we're done

            messages.append({"role": "assistant", "content": content})

            for tool_call in tool_calls:
                if tool_call.function.name == "kubectl_tool":
                    kubectl_command = json.loads(tool_call.function.arguments).get("command")
                    if kubectl_command:
                        console.print(f"Executing kubectl command: {kubectl_command}", style="bold yellow")
                        kubectl_tool = next(tool for tool in self.config.tools if isinstance(tool, KubectlTool))
                        kubectl_result: KubectlOutputSchema = kubectl_tool.run(KubectlInputSchema(command=kubectl_command))

                        kubectl_commands.append(kubectl_command)
                        kubectl_outputs.append(kubectl_result)

                        messages.append({
                            "role": "function",
                            "name": "kubectl_tool",
                            "content": f"Command: {kubectl_command}\nOutput: {kubectl_result.output}\nError: {kubectl_result.error}"
                        })
                        console.print(f"kubectl output:\n{kubectl_result.output}", style="green")
                        if kubectl_result.error:
                            console.print(f"kubectl error:\n{kubectl_result.error}", style="red")

            #messages.append({"role": "user", "content": "Based on the kubectl output, do you need any more information or can you provide a final response?"})

        console.print("Generating final response...", style="bold blue")
        return KubernetesAgentOutputSchema(
            response=content,
            kubectl_commands=kubectl_commands,
            kubectl_outputs=kubectl_outputs
        )
