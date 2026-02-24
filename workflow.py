from langgraph.graph import StateGraph, END
from state import ChatState
from nodes import (
    get_user_input,
    check_content_request,
    handle_missing_info,
    research_topic,
    create_content,
    display_response
)
from router import route_response, should_continue

# Build LangGraph workflow
workflow = StateGraph(ChatState)

# Add nodes
workflow.add_node("get_input", get_user_input)
workflow.add_node("check_request", check_content_request)
workflow.add_node("ask_type", handle_missing_info)
workflow.add_node("research", research_topic)
workflow.add_node("create_content", create_content)
workflow.add_node("display", display_response)

# Set entry point
# In the CLI main.py, we invoke with user_input already populated in state
# But 'get_input' is the start. 
# get_input in nodes.py just returns state now.
workflow.set_entry_point("get_input")

# Add edges
workflow.add_edge("get_input", "check_request")
workflow.add_conditional_edges(
    "check_request",
    route_response,
    {
        "research": "research",
        "select_best": "create_content",
        "edit_content": "create_content",
        "provide_references": "create_content",
        "ask_type": "ask_type",
        "display": "display"
    }
)
workflow.add_edge("ask_type", "display")
workflow.add_edge("research", "create_content")
workflow.add_edge("create_content", "display")
workflow.add_conditional_edges(
    "display",
    should_continue,
    {
        "continue": END, # In a single turn request-response cycle, we end after display
        "end": END
    }
)

# Note: The original loop was `display -> should_continue -> get_input`.
# But for a StateGraph aimed at being "invoked" once per turn (like in a web app), 
# it effectively ends after display. The looping happens in the external runner (while loop or web server).
# Modified logic: display -> END. 
# The external runner will call app.invoke() again with new input.

# Compile the graph
app = workflow.compile()
