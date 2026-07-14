from langchain.agents import create_agent
from .model import Model
import json

# NOTE Porto 30/06/2026 23:13 Does this class add anything useful? It seems like a wrapper around langchain
# Awnser: There is something usefull about this class. It minimizes the complexity of langchain into easy to use functions for the rest of the project

# NOTE Porto 04/07/2026 18:55 From now on this class only serves as a base for other agents, like an interface without being one itself (because python
# dont like interfaces).

# NOTE Porto 04/07/2026 19:03 And for instantiating simple agents too.

class Agent:
    
    def __init__(self, model: Model, system_prompt="", tools=[], checkpointer=None):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
        self.checkpointer = checkpointer
        self.agent = self._instantiate_agent()

                
    def _instantiate_agent(self):
        if self.checkpointer:
            agent = create_agent(self.model.llm, tools=self.tools, system_prompt=self.system_prompt, checkpointer=self.checkpointer)
        else:
            agent = create_agent(self.model.llm, tools=self.tools, system_prompt=self.system_prompt)
        return agent
    
    def send_message(self, message, message_history = [], thread_id: str = ""):
        if self.checkpointer and thread_id.strip():
            config = {"configurable": {"thread_id": thread_id}}
            result = self.agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config
        )
        else:
            result = self.agent.invoke(
                {"messages": message_history + [{"role": "user", "content": message}]}
            )
        
        return result['messages'][-1].content

    def stream_message(self, message, message_history=[], thread_id: str = ""):
        if self.checkpointer and thread_id.strip():
            config = {"configurable": {"thread_id": thread_id}}
            input_data = {"messages": [{"role": "user", "content": message}]}
        else:
            config = {}
            input_data = {"messages": message_history + [{"role": "user", "content": message}]}

        seen_ids = set()

        for event in self.agent.stream(input_data, config=config, stream_mode="values"):
            messages = event.get("messages", [])
            if not messages:
                continue

            last_msg = messages[-1]
            msg_id = getattr(last_msg, "id", None) or id(last_msg)
            if msg_id in seen_ids:
                continue
            seen_ids.add(msg_id)

            msg_type = last_msg.__class__.__name__

            if msg_type == "AIMessage":
                tool_calls = getattr(last_msg, "tool_calls", None)
                if tool_calls:
                    for tc in tool_calls:
                        yield {
                            "type": "tool_call",
                            "content": f"{tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})"
                        }
                elif last_msg.content:
                    yield {"type": "final", "content": last_msg.content}

            elif msg_type == "ToolMessage":
                yield {"type": "tool_result", "content": str(last_msg.content)}
    
        