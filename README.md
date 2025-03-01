# AI Services Platform

A platform for accessing AI text generation services using OpenAI's powerful language models.

## Features

* **Text Generation:** Generate human-like text using OpenAI's API.
* **Easy to use**: Simple web interface
* **Free**: Use it for free

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your_username>/<your_repo_name>.git
   ```

2. **Install dependencies:**
   ```bash
   cd ai-services-platform
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   Create a .env file with the following content and add your API keys:
   ```properties
   # Flask application settings
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here

   # API Keys
   OPENAI_API_KEY=your-openai-api-key-here

   # Server Configuration
   DEBUG=True
   HOST=0.0.0.0
   PORT=5000
   ```

4. **Run the app:**
   ```bash
   cd ai-services-platform
   python app.py
   ```

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Use the web interface to generate text using OpenAI's API

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or feedback, please open an issue in the GitHub repository.