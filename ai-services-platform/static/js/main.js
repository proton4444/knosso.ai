document.addEventListener('DOMContentLoaded', () => {
    // Elements for image generation
    const workflowSelect = document.getElementById('workflow-select');
    const imageForm = document.getElementById('image-generation-form');
    const workflowParams = document.getElementById('workflow-params');
    const imageResult = document.getElementById('image-result');
    const generatedImage = document.getElementById('generated-image');
    const downloadBtn = document.getElementById('download-btn');
    const newImageBtn = document.getElementById('new-image-btn');
    
    // Load available workflows
    async function loadWorkflows() {
        try {
            const response = await fetch('/api/workflows');
            const data = await response.json();
            
            if (data.workflows && data.workflows.length > 0) {
                workflowSelect.innerHTML = '';
                workflowSelect.innerHTML = '<option value="">Select a workflow</option>';
                
                data.workflows.forEach(workflow => {
                    const option = document.createElement('option');
                    option.value = workflow.id;
                    option.textContent = workflow.name;
                    workflowSelect.appendChild(option);
                });
            } else {
                workflowSelect.innerHTML = '<option value="">No workflows available</option>';
            }
        } catch (error) {
            console.error('Error loading workflows:', error);
            workflowSelect.innerHTML = '<option value="">Error loading workflows</option>';
        }
    }
    
    // Load workflow details when selected
    workflowSelect.addEventListener('change', async () => {
        const workflowId = workflowSelect.value;
        
        if (!workflowId) {
            imageForm.classList.add('hidden');
            return;
        }
        
        try {
            const response = await fetch(`/api/workflows/${workflowId}`);
            const data = await response.json();
            
            if (data.workflow) {
                // Store the workflow data
                imageForm.dataset.workflow = JSON.stringify(data.workflow);
                
                // For now, we'll just show the form without custom parameters
                workflowParams.innerHTML = '<p>This workflow is ready to use. Click Generate to create an image.</p>';
                imageForm.classList.remove('hidden');
            }
        } catch (error) {
            console.error('Error loading workflow details:', error);
            alert('Error loading workflow details. Please try again.');
        }
    });
    
    // Handle image generation form submission
    imageForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const workflow = JSON.parse(imageForm.dataset.workflow || '{}');
        
        if (!workflow || Object.keys(workflow).length === 0) {
            alert('Please select a valid workflow');
            return;
        }
        
        // Show loading state
        const submitBtn = imageForm.querySelector('button[type="submit"]');
        const spinner = submitBtn.querySelector('.spinner');
        const btnText = submitBtn.querySelector('.btn-text');
        
        submitBtn.disabled = true;
        spinner.classList.remove('hidden');
        btnText.textContent = 'Generating...';
        
        try {
            const response = await fetch('/api/image-generation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ workflow })
            });
            
            const data = await response.json();
            
            if (data.success && data.image_paths && data.image_paths.length > 0) {
                // Display the first image
                generatedImage.src = data.image_paths[0];
                imageResult.classList.remove('hidden');
                
                // Set up download button
                downloadBtn.addEventListener('click', () => {
                    const a = document.createElement('a');
                    a.href = data.image_paths[0];
                    a.download = data.image_paths[0].split('/').pop();
                    document.body.appendChild(a);
                    a.click();
                    document.body.removeChild(a);
                });
            } else {
                alert(data.error || 'Failed to generate image');
            }
        } catch (error) {
            console.error('Error generating image:', error);
            alert('Error communicating with the server. Please try again.');
        } finally {
            // Reset button state
            submitBtn.disabled = false;
            spinner.classList.add('hidden');
            btnText.textContent = 'Generate Image';
        }
    });
    
    // New image button
    newImageBtn.addEventListener('click', () => {
        imageResult.classList.add('hidden');
    });
    
    // Load workflows when page loads
    loadWorkflows();
});