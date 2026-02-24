from typing import TypedDict, List, Optional

class ChatState(TypedDict):
    messages: List[str]
    user_input: str
    ai_response: str
    topic: Optional[str]
    content_type: Optional[str]
    research_data: Optional[str]
