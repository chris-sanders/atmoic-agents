import instructor

from typing import Union, Optional
from pydantic import Field
from atomic_agents.agents.base_agent import BaseAgent, BaseAgentConfig, BaseIOSchema
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from tools.kubectl import KubectlInputSchema, KubectlTool
from  openai import OpenAI


class DiagnosisResponse(BaseIOSchema):
    """Final diagnosis response"""
    diagnosis: str = Field(..., description="Analysis of the cluster issue")
    recommended_actions: list[str] = Field(..., description="Recommended steps to resolve")

class DebuggerInput(BaseIOSchema):
    """User input to the debugging agent"""
    question: str = Field(..., description="Description of the kubernetes issue to debug")

ResponseTypes = Union[KubectlInputSchema, DiagnosisResponse]

class KubernetesDebugAgent(BaseAgent):
    input_schema = DebuggerInput
    output_schema = ResponseTypes

    def __init__(self, config: Optional[BaseAgentConfig] = None):
        agent_config = BaseAgentConfig(
            client=config.client if config.client else instructor.from_openai(OpenAI()),
            model=config.model if config.model else "gpt-4o-mini",
            system_prompt_generator=SystemPromptGenerator(
                background=[
                    "You are a Kubernetes expert.",
                    "Your task is to diagnose cluster issues.",
                ],
                steps=[
                    "Analyze the reported issue.",
                    "Either request kubectl information using KubectlInputSchema",
                    "Or provide a final diagnosis using DiagnosisResponse",
                ],
                output_instructions=[
                    "Use KubectlInputSchema when you need cluster information",
                    "Use DiagnosisResponse when you have enough information to diagnose"
                ]
            )
        )
        super().__init__(agent_config)

    def run(self, user_input: DebuggerInput) -> DiagnosisResponse:
        """Run the agent, handling any tool calls until we get a final diagnosis"""
        self.memory.initialize_turn()
        self.current_user_input = user_input
        self.memory.add_message("user", user_input)
    
        while True:
            response = self.get_response(response_model=self.output_schema)
            
            if isinstance(response, KubectlInputSchema):
                # Got a tool call, execute it
                tool = KubectlTool()
                result = tool.run(response)
                # Add tool result to memory
                self.memory.add_message("tool", result)
                continue
                
            if isinstance(response, DiagnosisResponse):
                # Got final diagnosis, return it
                self.memory.add_message("assistant", response)
                return response
