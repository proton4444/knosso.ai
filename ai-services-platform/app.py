from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
import openai

# Load environment variables
load_dotenv()

# Configure OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Configure app settings from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

@app.route('/')
def index():
    return render_template('index.html')

# Text generation route
@app.route('/api/text-generation', methods=['POST'])
def generate_text():
    try:
        data = request.json
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
            
        # Generate text using OpenAI
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        generated_text = response.choices[0].text.strip()
        
        return jsonify({
            "text": generated_text,
            "success": True
        })
    except Exception as e:
        print(f"Error generating text: {str(e)}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

# Route for health check
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000))
    )