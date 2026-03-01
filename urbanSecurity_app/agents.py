# security/agents.py
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI  # Or Ollama for local
# from .utils import RolePredictor
from .utils.RoleLSTM import RolePredictor


def get_role_agent():
    llm = OpenAI(temperature=0.3)  # Or Ollama('llama3')
    tools = [Tool(name="DL_Role_Predict", func=RolePredictor.predict, description="Predict role change from context vector")]
    agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description")
    return agent

def adapt_role(agent, user_context_str):
    response = agent.run(f"Adapt role based on: {user_context_str}. Use DL tool if needed.")
    return response  # e.g., "Elevate to Engineer"