import requests
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, TAVILY_API_KEY, MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS
from state import ChatState

# Initialize LLM
llm = ChatGroq(
    model=MODEL_NAME, 
    groq_api_key=GROQ_API_KEY,
    temperature=TEMPERATURE,
    max_tokens=MAX_OUTPUT_TOKENS
)

def get_user_input(state: ChatState):
    """Get input from user - Placeholder for Logic Node, actual input comes from external source usually"""
    # In a scripted/web env, user_input is already in the state when passed in
    # But for CLI, we might input here. 
    # For a unified graph, we usually assume 'user_input' is set before invoking or updated via interaction
    # For compatibility with the previous CLI design where this was a node:
    
    # NOTE: In a real graph designed for API usage, input usually comes into the graph state
    # rather than being asked for inside a node. 
    # However, to keep logic identical to original for now:
    return state

def check_content_request(state: ChatState):
    """Check if user wants content creation and what type"""
    if state["user_input"] == "QUIT":
        return {**state, "ai_response": "Goodbye! Have a great day!"}
    
    # Check if this is a follow-up response to content type question
    user_input_lower = state["user_input"].lower().strip()
    if state.get("topic") and ("blog" in user_input_lower or "email" in user_input_lower or "video" in user_input_lower):
        if "blog" in user_input_lower:
            content_type = "BLOG"
        elif "email" in user_input_lower:
            content_type = "EMAIL"
        elif "video" in user_input_lower:
            content_type = "VIDEO"
        else:
            content_type = "BLOG" # Default fallback
        
        return {**state, "ai_response": f"CONTENT_REQUEST: {state['topic']} | {content_type}"}
    
    prompt = f"""Analyze this user message: "{state["user_input"]}"
    
    Look for keywords that indicate CONTENT CREATION: create, write, make, generate, develop, produce, draft, compose, build, design, give me + content/blog/email/video/script/post/article
    
    RULES:
    1. If user mentions specific type (blog/email/video): "CONTENT_REQUEST: [topic] | [TYPE]"
       - "give blog for salesforce" -> "CONTENT_REQUEST: Salesforce | BLOG" (Type must be BLOG, EMAIL, or VIDEO)
       - If type is similar to video (e.g. youtube), map to VIDEO.
       - If type is similar to email (e.g. newsletter), map to EMAIL.
    2. If user wants content but no specific type: "ASK_TYPE: [topic]"
       - "create content for project manager" -> "ASK_TYPE: project manager"
    3. If user says a greeting (hi, hello, hey, etc.): "GREETING: Hello! I can help you create blogs, emails, and video scripts. What would you like to create today?"
    4. If user asks to PICK or SELECT from previous results (e.g. "get the best blog", "which is best", "choose one"): "SELECT_BEST: [user_input]"
    5. If user asks to EDIT, ADJUST, REVISE, or MODIFY the previously generated content: "EDIT_CONTENT: [user_input]"
    6. If user asks for RESEARCH REFERENCES, SOURCES, or LINKS from the previous topic: "PROVIDE_REFERENCES: [user_input]"
    7. If user says thanks, thank you, or acknowledges the content: "GREETING: I am glad I could help! Is there anything else I can assist you with regarding content creation?"
    8. If not about content creation: "I apologize, but I can only assist with content creation. How can I help you create content today?"
    
    Respond with EXACTLY one of the formats above.
    """
    
    response = llm.invoke(prompt)
    ai_response = response.content.strip()
    
    if ai_response.startswith("GREETING: "):
        ai_response = ai_response.replace("GREETING: ", "")
        return {**state, "ai_response": ai_response}
        
    if ai_response.startswith("SELECT_BEST: "):
        return {**state, "ai_response": "SELECT_BEST"} # Marker for next step
        
    if ai_response.startswith("EDIT_CONTENT: "):
        return {**state, "ai_response": "EDIT_CONTENT"}
        
    if ai_response.startswith("PROVIDE_REFERENCES: "):
        return {**state, "ai_response": "PROVIDE_REFERENCES"}
    
    print(f"[DEBUG] LLM Response: {ai_response}")
    
    return {**state, "ai_response": ai_response}

def ask_content_type(state: ChatState):
    """Ask user to specify content type"""
    if "ASK_TYPE:" not in state["ai_response"]:
        return state
    
    topic = state["ai_response"].replace("ASK_TYPE: ", "")
    response = f"I'd be happy to help you create content about {topic}! What type of content would you like me to create?\n\n1. Blog post\n2. Email\n3. Video script\n\nPlease specify which type you'd prefer."
    
    return {**state, "ai_response": response, "topic": topic}

def research_topic(state: ChatState):
    """Research topic using Tavily API"""
    if "CONTENT_REQUEST:" not in state["ai_response"]:
        return state
    
    # Parse topic and content type
    parts = state["ai_response"].replace("CONTENT_REQUEST: ", "").split("|")
    if len(parts) < 2:
        print(f"[DEBUG] Error parsing response: {state['ai_response']}")
        return state
    
    topic = parts[0].strip()
    content_type_raw = parts[1].strip().upper()
    
    # Map raw content type to standard types
    if "BLOG" in content_type_raw:
        content_type = "BLOG"
    elif "EMAIL" in content_type_raw:
        content_type = "EMAIL"
    elif "VIDEO" in content_type_raw or "YOUTUBE" in content_type_raw:
        content_type = "VIDEO"
    else:
        content_type = "BLOG" # Default
    
    print(f"\n[DEBUG] Tavily is researching topic: {topic} | Type: {content_type}")
    
    # Research using Tavily
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": f"{topic} latest information trends facts",
        "search_depth": "basic",
        "include_answer": True,
        "max_results": 5
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            research_data = data.get('answer', '') + "\n\n"
            for result in data.get('results', [])[:3]:
                research_data += f"- {result.get('title', '')} (URL: {result.get('url', 'N/A')}): {result.get('content', '')}\n"
            print(f"[DEBUG] Tavily research completed successfully")
        else:
            research_data = "Research data unavailable"
            print(f"[DEBUG] Tavily API error: {response.status_code}")
    except Exception as e:
        research_data = "Research data unavailable"
        print(f"[DEBUG] Tavily request failed: {e}")
    
    return {**state, "topic": topic, "content_type": content_type, "research_data": research_data}

def create_content(state: ChatState):
    """Create content based on research"""
    if state["ai_response"] == "SELECT_BEST":
        # Handle "Select best" request using local context/history
        prompt = f"""Review the user's request: "{state['user_input']}"
        
        Previous conversation context:
        {state.get('messages', [])[-4:]}  
        
        The user is asking to pick the best option or select one from previous results.
        Analyze the previous options discussed and recommend the best one with a clear justification.
        """
        response = llm.invoke(prompt)
        return {**state, "ai_response": response.content, "topic": None, "content_type": None}
        
    if state["ai_response"] == "EDIT_CONTENT":
        prompt = f"""Review the user's request to edit or adjust the content: "{state['user_input']}"
        
        Previous conversation context:
        {state.get('messages', [])[-4:]}  
        
        Please provide the edited or adjusted content based on the user's instructions. Keep the same format as the original content unless requested otherwise.
        """
        response = llm.invoke(prompt)
        return {**state, "ai_response": response.content, "topic": None, "content_type": None}
        
    if state["ai_response"] == "PROVIDE_REFERENCES":
        research_context = state.get("research_data", "No recent research data available.")
        prompt = f"""The user is asking for research references, sources, or links for the previous topic.
        User request: "{state['user_input']}"
        
        Here is the most recent research data containing sources and URLs:
        {research_context}
        
        Please provide a polite response sharing the reference URLs and sources from the research data above. Do not hallucinate links not present in the research data.
        """
        response = llm.invoke(prompt)
        return {**state, "ai_response": response.content, "topic": None, "content_type": None}

    if "CONTENT_REQUEST:" not in state["ai_response"]:
        return state
    
    content_type = state["content_type"]
    topic = state["topic"]
    research_data = state["research_data"]
    
    # [FIX] Clear topic and content_type from state for the next turn, 
    # but keep them local for this function execution.
    # This prevents the "follow-up" logic in check_content_request from triggering incorrectly on the next turn.
    # We return the AI response, but we can set topic/content_type to None in the returned state if valid.
    # However, LangGraph usually merges state. 
    # A safer way: The check_content_request needs to be smarter about "what is a follow up".
    
    if content_type == "BLOG":
        prompt = f"""Create a comprehensive blog post about {topic}.
        
        Research Data:
        {research_data}
        
        Include:
        - Engaging title
        - Introduction
        - 3-4 main sections with subheadings
        - Conclusion
        - Use the research data to make it current and accurate
        """
    elif content_type == "EMAIL":
        prompt = f"""Create a professional email about {topic}.
        
        Research Data:
        {research_data}
        
        Include:
        - Subject line
        - Professional greeting
        - Clear and concise body with key points
        - Call to action
        - Professional closing
        - Use the research data for accuracy
        """
    elif content_type == "VIDEO":
        prompt = f"""Create a video script about {topic}.
        
        Research Data:
        {research_data}
        
        Include:
        - Hook (first 10 seconds)
        - Introduction
        - Main content points (3-4 key points)
        - Conclusion with call to action
        - Estimated timing for each section
        - Use the research data for current information
        """
    else:
        prompt = f"Create content about {topic}"
    
    response = llm.invoke(prompt)
    
    # [FIX] Reset state so the next unrelated query doesn't inherit old topic
    return {**state, "ai_response": response.content, "topic": None, "content_type": None}

def display_response(state: ChatState):
    """Display AI response and update conversation history"""
    # In CLI this prints, in Web it just updates state
    print(f"\nAI: {state['ai_response']}")
    
    # Update conversation history
    new_messages = state["messages"] + [
        f"User: {state['user_input']}",
        f"AI: {state['ai_response']}"
    ]
    
    return {**state, "messages": new_messages}
