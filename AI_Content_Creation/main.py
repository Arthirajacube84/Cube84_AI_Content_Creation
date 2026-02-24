from workflow import app

def main():
    print("=== Content Creation Assistant ===")
    print("I can help you create BLOGS, EMAILS, and VIDEO scripts.")
    print("Type 'quit', 'exit', or 'bye' to end.")
    
    # Initial state
    state = {
        "messages": [],
        "user_input": "",
        "ai_response": "",
        "topic": None,
        "content_type": None,
        "research_data": None
    }
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        state["user_input"] = user_input
        
        # Invoke the graph
        # The graph runs from get_input -> ... -> display -> END
        result = app.invoke(state)
        
        # Update state for next turn (keep history)
        state = result

if __name__ == "__main__":
    main()
