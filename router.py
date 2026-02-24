from langgraph.graph import END
from state import ChatState

def should_continue(state: ChatState):
    """Check if conversation should continue"""
    if state["user_input"] == "QUIT":
        return "end"
    return "continue"

def route_response(state: ChatState):
    """Route based on response type"""
    val = state["ai_response"]
    if "CONTENT_REQUEST:" in val:
        return "research"
    elif val in ["SELECT_BEST", "EDIT_CONTENT", "PROVIDE_REFERENCES"]:
        return val.lower()
    elif "ASK_TYPE:" in val:
        return "ask_type"
    else:
        return "display"
