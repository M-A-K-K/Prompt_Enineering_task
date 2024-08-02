# from flask import Flask, request, jsonify
# import os
# import re
# from dotenv import load_dotenv
# from together import Together

# # Initialize Flask app
# app = Flask(__name__)

# # Load environment variables from .env file
# load_dotenv()

# # Get API key from environment variable
# TOGETHER_AI_API_KEY = os.getenv("TOGETHER_API_KEY")
# if not TOGETHER_AI_API_KEY:
#     raise ValueError("API key is not set in the environment variables.")

# # Initialize Together client
# client = Together(api_key=TOGETHER_AI_API_KEY)

# def generate_response(prompt):
#     try:
#         response = client.chat.completions.create(
#             model="codellama/CodeLlama-34b-Python-hf",
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=175
#         )
#         # Print the entire response object for debugging
#         print(f"Response: {response}")

#         # Extract the response content
#         content = response.choices[0].message.content
        
#         # Clean the response content using regular expressions
#         # Remove instructional tags and extra whitespace
#         cleaned_content = re.sub(r'\[INST\]|\[/INST\]', '', content)  # Remove instructional tags
#         cleaned_content = re.sub(r'\s+', ' ', cleaned_content)  # Replace multiple newlines with a single space
#         cleaned_content = cleaned_content.strip()  # Remove leading and trailing whitespace
        
#         return cleaned_content
#     except Exception as e:
#         print(f"Error: {e}")  # Log the error for debugging
#         return "Sorry, there was an error processing your request."

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_input = request.json.get('message', '')
#     if not user_input:
#         return jsonify({'error': 'No message provided'}), 400

#     response_text = generate_response(user_input)
#     return jsonify({'response': response_text})

# if __name__ == '__main__':
#     app.run(debug=True)





from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from together import Together

app = Flask(__name__)

load_dotenv()

# Get API key from environment variable
TOGETHER_AI_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_AI_API_KEY:
    raise ValueError("API key is not set in the environment variables.")

# Initialize Together client
client = Together(api_key=TOGETHER_AI_API_KEY)

# Initialize conversation memory
conversation_memory = []

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_input = data.get("user_input")
    if not user_input:
        return jsonify({"error": "User input is required"}), 400
    
    response, updated_memory = generate_response(user_input)
    
    # Update the global conversation memory
    global conversation_memory
    conversation_memory = updated_memory

    return jsonify({"response": response})

def generate_response(user_input):
    # Create custom prompt with conversation history
    custom_prompt = '''You are an experienced and helpful Lawyer. Your primary goal is to provide users with detailed, accurate, and useful legal advice based on their specific issues or situations. Please adhere to the following guidelines:
    1. Start by saying your name as Kabir, ask the name of user and then thoroughly understanding the user's situation.
    2. Ask one specific, clarifying question at a time to gather detailed information.
    3. Provide legal advices, he user needs.
    4. Avoid asking multiple questions simultaneously to maintain clear and focused communication.
    5. Based on the information gathered, offer informative and relevant legal advice.
    6. Ensure your responses are professional, empathetic, and easy to understand.
    7. Respond in a natural, human-like manner to make the conversation more engaging and relatable.
    7. Try to comfort the user, make user that he is confident in you.
    User's input:'''

    # Combine conversation history with the current user input
    messages = [{"role": "system", "content": custom_prompt}] 
    messages.extend(conversation_memory)
    messages.append({"role": "user", "content": user_input})
    
    # Call the Together API
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        messages=messages,
        stream=False  # Disable streaming
    )
    # Access the content of the response correctly
    response_content = completion.choices[0].message.content
    
    # Update conversation memory
    updated_memory = list(conversation_memory)
    updated_memory.append({"role": "user", "content": user_input})
    updated_memory.append({"role": "assistant", "content": response_content})

    return response_content, updated_memory

if __name__ == "__main__":
    app.run(debug=True)
