from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import requests
import openai
import json

# Import our ComfyUI integration
from comfy_integration import ComfyUIAPI

# Load environment variables
load_dotenv()

# Configure OpenAI
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Initialize ComfyUI API
comfy_api = ComfyUIAPI(server_address='10.0.10.223:8080')

# Initialize Flask app
app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Create a directory for generated images
os.makedirs('static/generated', exist_ok=True)

# Configure app settings from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'

# NEW: API route for image generation using ComfyUI
@app.route('/api/image-generation', methods=['POST'])
def generate_image():
    try:
        # Get workflow from request
        data = request.json
        workflow = data.get('workflow')
        
        if not workflow:
            return jsonify({"error": "No workflow provided"}), 400
        
        # Generate image using ComfyUI
        image_paths = comfy_api.generate_image(workflow, output_dir="static/generated")
        
        if not image_paths:
            return jsonify({"error": "No images were generated"}), 500
        
        return jsonify({
            "image_paths": image_paths,
            "success": True
        })
    except Exception as e:
        print(f"Error generating image: {str(e)}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

# Load a workflow from file
@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    workflow_dir = "workflows"
    if not os.path.exists(workflow_dir):
        os.makedirs(workflow_dir)
    
    workflow_files = [f for f in os.listdir(workflow_dir) if f.endswith('.json')]
    workflows = []
    
    for file in workflow_files:
        with open(os.path.join(workflow_dir, file), 'r') as f:
            try:
                # Just read enough to get some metadata, not the whole workflow
                workflow_data = json.load(f)
                workflows.append({
                    "id": file.replace('.json', ''),
                    "name": file.replace('.json', '').replace('_', ' ').title(),
                    "file": file
                })
            except json.JSONDecodeError:
                continue
    
    return jsonify({"workflows": workflows})

@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    workflow_path = f"workflows/{workflow_id}.json"
    
    if not os.path.exists(workflow_path):
        return jsonify({"error": "Workflow not found"}), 404
    
    with open(workflow_path, 'r') as f:
        workflow = json.load(f)
    
    return jsonify({"workflow": workflow})

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

# Serve static files
@app.route('/generated/<path:filename>')
def serve_generated_image(filename):
    return send_from_directory('static/generated', filename)

if __name__ == '__main__':
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000))
    )