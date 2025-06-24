from .agent_tools import ChatAgent


def main() -> None:
    agent = ChatAgent()
    print("Start chatting with the agent. Type 'exit' to quit.")
    try:
        while True:
            msg = input("You: ")
            if msg.lower() in {"exit", "quit"}:
                break
            agent.user_message(msg)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
