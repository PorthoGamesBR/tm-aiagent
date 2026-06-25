class ChatService {
    def __init__(self, agent):
        self.agent = agent

    async def send_message(self, message, chat_id, user_id):
        # LOG: 25-06-2026 20:10 Porto
        #   I'm using FastAPI dependecy injection so the chat service receive the agent without the endpoint knowing about it.

        reply = self.agent.send_message(message)

        return {"reply": reply}

    async def create_chat(self, user_id):
        # TODO: Implement dependency to access the chat repository and create a new chat for the user
        pass

    async def get_chat_history(self, user_id, chat_id):
        # TODO: Implement dependency to access the chat repository and retrieve the chat by user_id and chat_id
        pass

}