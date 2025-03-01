import json
import uuid
import websocket
import urllib.request
import urllib.parse
from PIL import Image
import io
import os
from requests_toolbelt import MultipartEncoder

class ComfyUIAPI:
    def __init__(self, server_address='10.0.10.223:8080'):
        self.server_address = server_address
        
    def open_websocket_connection(self):
        """Establish a websocket connection to ComfyUI"""
        client_id = str(uuid.uuid4())
        ws = websocket.WebSocket()
        ws.connect(f"ws://{self.server_address}/ws?clientId={client_id}")
        return ws, client_id
    
    def queue_prompt(self, prompt, client_id):
        """Send a workflow to ComfyUI"""
        p = {"prompt": prompt, "client_id": client_id}
        data = json.dumps(p).encode('utf-8')
        req = urllib.request.Request(
            f"http://{self.server_address}/prompt",
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        response = urllib.request.urlopen(req).read()
        return json.loads(response)
    
    def get_image(self, filename, subfolder, folder_type):
        """Get an image from ComfyUI"""
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(f"http://{self.server_address}/view?{url_values}") as response:
            return response.read()
    
    def get_history(self, prompt_id):
        """Get generation history for a prompt"""
        with urllib.request.urlopen(f"http://{self.server_address}/history/{prompt_id}") as response:
            return json.loads(response.read())
    
    def upload_image(self, input_path, name, image_type="input", overwrite=False):
        """Upload an image to ComfyUI"""
        with open(input_path, 'rb') as file:
            multipart_data = MultipartEncoder(
                fields={
                    'image': (name, file, 'image/png'),
                    'type': image_type,
                    'overwrite': str(overwrite).lower()
                }
            )
            
            headers = {'Content-Type': multipart_data.content_type}
            request = urllib.request.Request(
                f"http://{self.server_address}/upload/image",
                data=multipart_data,
                headers=headers
            )
            with urllib.request.urlopen(request) as response:
                return response.read()
    
    def track_progress(self, ws, prompt_id):
        """Track the progress of generation by listening to websocket messages"""
        while True:
            out = ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                
                # Progress updates for K-Sampler
                if message['type'] == 'progress':
                    data = message['data']
                    progress = {
                        'value': data['value'],
                        'max': data['max']
                    }
                    yield ('progress', progress)
                
                # Execution completed
                if message['type'] == 'executing' and \
                   message['data']['node'] is None and \
                   message['data']['prompt_id'] == prompt_id:
                    break
        
        yield ('complete', None)
    
    def get_images_from_history(self, prompt_id):
        """Get all output images from generation history"""
        output_images = []
        
        history = self.get_history(prompt_id)[prompt_id]
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            
            if 'images' in node_output:
                for image in node_output['images']:
                    if image['type'] == 'output':
                        image_data = self.get_image(
                            image['filename'], 
                            image['subfolder'], 
                            image['type']
                        )
                        
                        output_images.append({
                            'image_data': image_data,
                            'filename': image['filename'],
                            'subfolder': image['subfolder'],
                            'type': image['type']
                        })
        
        return output_images
    
    def generate_image(self, workflow, output_dir="static/generated"):
        """Complete workflow to generate an image using ComfyUI"""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Open WebSocket connection
        ws, client_id = self.open_websocket_connection()
        
        try:
            # Queue prompt for execution
            response = self.queue_prompt(workflow, client_id)
            prompt_id = response['prompt_id']
            
            # Track progress
            for update_type, update_data in self.track_progress(ws, prompt_id):
                if update_type == 'progress':
                    print(f"Progress: {update_data['value']}/{update_data['max']}")
            
            # Get output images
            images = self.get_images_from_history(prompt_id)
            
            # Save and return image paths
            saved_paths = []
            for i, img_data in enumerate(images):
                # Create a PIL Image from binary data
                image = Image.open(io.BytesIO(img_data['image_data']))
                
                # Save the image
                save_path = os.path.join(output_dir, img_data['filename'])
                image.save(save_path)
                
                # Add path for web access
                web_path = f"/generated/{img_data['filename']}"
                saved_paths.append(web_path)
            
            return saved_paths
        
        finally:
            ws.close()