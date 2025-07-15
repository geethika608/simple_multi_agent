# Simple Multi-Agent Content Creator

A streamlined multi-agent system using Google ADK that creates scripts and generates corresponding images based on user input. This project demonstrates the use of **Function Tools** for image generation, providing a cleaner and more maintainable approach.

## Features

- **Script Writer Agent**: Creates engaging, concise scripts for short-form content
- **Image Prompt Generator**: Converts scripts into detailed image prompts
- **Image Generator**: Uses Imagen 3.0 via Function Tools to generate images from prompts
- **Loop Agent**: Orchestrates the workflow sequentially
- **Function Tools**: Clean, reusable tools for image generation
- **Local Storage**: Saves all outputs locally in organized folders

## Project Structure

```
simple_multi_agent/
├── __init__.py                    # Exports root_agent
├── agent.py                       # Main agent definitions
├── tools.py                       # Function tools for image generation
├── util.py                        # Utility functions
├── requirements.txt               # Dependencies
├── scriptwriter_instruction.txt   # Script writer instructions
├── image_prompt_instruction.txt   # Image prompt generator instructions
└── README.md                      # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

**Important**: Your Google API key needs access to:
- Gemini 2.0 Flash (for script and prompt generation)
- Imagen 3.0 (for image generation)

### 3. Verify API Access

Make sure your Google API key has the necessary permissions for:
- `gemini-2.0-flash-001` (or similar Gemini model)
- `models/imagen-3.0-generate-002`

## Usage

### Method 1: ADK Web Interface (Recommended)

1. **Start the ADK web server**:
   ```bash
   adk web
   ```

2. **Open your browser** and go to `http://localhost:8000`

3. **Select your agent** from the dropdown

4. **Enter your prompt** and watch the agents work!

### Method 2: Programmatic Usage

```python
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from simple_multi_agent import root_agent

# Setup session and runner
session_service = InMemorySessionService()
session = session_service.create_session("test_app", "user1", "session1")
runner = Runner(agent=root_agent, session_service=session_service)

# Create user message
content = types.Content(role="user", parts=[types.Part(text="Create a script about artificial intelligence")])

# Run the agent
events = runner.run(user_id="user1", session_id="session1", new_message=content)

# Process events
for event in events:
    if event.is_final_response():
        print("Final Response:", event.content.parts[0].text)
```

## Workflow

1. **User Input** → User provides a topic or description
2. **Script Generation** → ScriptWriter agent creates an engaging script
3. **Image Prompts** → ImagePromptGenerator converts script into visual prompts
4. **Image Generation** → ImageGenerator creates images using Imagen 3.0
5. **Output** → Script and images saved to `output/` directory

## Output Structure

```
output/
├── images/
│   ├── image_1.jpg
│   ├── image_2.jpg
│   └── ...
└── (other generated files)
```

## Agent Details

### ScriptWriter Agent
- **Model**: Gemini 2.0 Flash
- **Purpose**: Creates engaging, concise scripts
- **Output**: Plain text script in session state

### ImagePromptGenerator Agent
- **Model**: Gemini 2.0 Flash
- **Purpose**: Converts scripts into image prompts
- **Output**: JSON with image_prompts array

### ImageGenerator Agent
- **Model**: Gemini 2.0 Flash + Function Tools
- **Purpose**: Generates images from prompts using Imagen 3.0
- **Tools**: `generate_multiple_images_tool`
- **Output**: Image files saved locally, paths in session state

## Function Tools

### generate_multiple_images_tool
- **Purpose**: Generate multiple images from a list of prompts
- **Input**: List of text prompts, aspect ratio, output prefix
- **Output**: Success status and list of generated image paths
- **Features**: Error handling, local file saving, configurable parameters, session state integration

### session_info_tool
- **Purpose**: Get information about the current session state
- **Input**: ToolContext (automatically provided by ADK)
- **Output**: String representation of session data
- **Features**: Shows scripts, prompts, and generated image paths

### ToolContext Integration
All function tools use ADK's `ToolContext` for:
- **Session State Access**: Store and retrieve data across agent interactions
- **State Persistence**: Maintain context throughout the workflow
- **Debugging**: Monitor the state of the multi-agent system

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your `GOOGLE_API_KEY` is set correctly
2. **Imagen Access**: Verify your API key has Imagen 3.0 access
3. **Model Not Found**: Check if the model IDs are correct for your region
4. **Permission Errors**: Ensure write permissions for the output directory

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Customization

### Modify Instructions

Edit the instruction files to customize agent behavior:
- `scriptwriter_instruction.txt` - Script writing style and format
- `image_prompt_instruction.txt` - Image prompt generation style

### Change Models

Update model IDs in `agent.py`:
```python
model="gemini-2.0-flash-001"  # Change to your preferred model
```

### Adjust Image Settings

Modify the Imagen configuration in `SimpleImagenAgent`:
```python
self.config = {
    "number_of_images": 1,        # Images per prompt
    "aspect_ratio": "1:1",        # Image aspect ratio
    "output_mime_type": "image/jpeg"
}
```

## License

This project uses Google ADK and follows Google's terms of service for API usage. 