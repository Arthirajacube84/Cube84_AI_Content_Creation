from flask import Flask, render_template, request, jsonify
from workflow import app as graph_app
import os

# Define base directory explicitly to avoid path issues
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))

# Store state in memory for simplicity (restarts will clear history)
# In production, use a database or session
chat_history = []
current_state = {
    "messages": [],
    "user_input": "",
    "ai_response": "",
    "topic": None,
    "content_type": None,
    "research_data": None
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global current_state
    
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    # Update input in state
    current_state["user_input"] = user_input
    
    try:
        # Run the LangGraph workflow
        # invoke returns the final state
        result = graph_app.invoke(current_state)
        
        # Update our global state with the result
        current_state = result
        
        # Get the AI response from the state
        ai_response = current_state.get("ai_response", "I'm not sure how to respond.")
        
        return jsonify({
            "response": ai_response,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
