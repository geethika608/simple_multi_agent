import logging
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.tools import google_search

from .util import load_instruction_from_file
from .tools import generate_multiple_images_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Sub-agent 1: Script Writer
scriptwriter_agent = LlmAgent(
    name="ScriptWriter",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("scriptwriter_instruction.txt"),
    description="Creates engaging scripts for short-form content",
    output_key="generated_script"
)

# Sub-agent 2: Image Prompt Generator
image_prompt_agent = LlmAgent(
    name="ImagePromptGenerator",
    model="gemini-2.0-flash-001",
    instruction=load_instruction_from_file("image_prompt_instruction.txt"),
    description="Converts scripts into detailed image prompts",
    output_key="image_prompts"
)

# Sub-agent 3: Image Generator (using function tool)
image_generator_agent = LlmAgent(
    name="ImageGenerator",
    model="gemini-2.0-flash-001",
    instruction="""You are an image generation specialist. Your task is to generate images from the provided image prompts.

When you receive image prompts from the session state, use the generate_multiple_images tool to create the images.

**Instructions:**
1. Extract the image prompts from the session state (look for 'image_prompts' key)
2. Parse the prompts if they're in JSON format with markdown code blocks
3. Use the generate_multiple_images tool with the prompts
4. Report the results back to the user

**Important:** Always use the generate_multiple_images tool when you have image prompts to process.

**Example workflow:**
- If you see image prompts in the session state, call generate_multiple_images with those prompts
- The tool will return success status and image paths
- Report the results to the user""",
    description="Generates images from prompts using Imagen 3.0 via function tools",
    tools=[generate_multiple_images_tool],
    output_key="generated_images"
)

# Sub-agent 4: Formatter (Optional - combines script and image info)
formatter_agent = LlmAgent(
    name="ContentFormatter",
    model="gemini-2.0-flash-001",
    instruction="""Create a final summary combining the script from 'state['generated_script']' and the generated images from 'state['generated_images']'. 
    
    Format the output as:
    
    # Generated Content Summary
    
    ## Script
    [Include the full script here]
    
    ## Generated Images
    [List the image files that were created]
    
    ## Usage Instructions
    - The script can be used for voiceover or text content
    - Images are saved locally and can be used for visual content
    - All files are organized in the output directory""",
    description="Formats the final content summary",
    output_key="final_content_summary"
)

# Loop Agent Workflow
content_creator_agent = LoopAgent(
    name="content_creator_agent",
    max_iterations=3,  # Maximum 3 iterations to prevent infinite loops
    sub_agents=[scriptwriter_agent, image_prompt_agent, image_generator_agent, formatter_agent],
    description="Creates scripts, generates corresponding images, and provides a final summary"
)

# Root agent for ADK web interface
root_agent = content_creator_agent 