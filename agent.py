import logging
import json
from pathlib import Path
from typing import Any, AsyncGenerator, Dict

from google.adk.agents import LlmAgent, LoopAgent, BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from pydantic import Field
from typing_extensions import override

from .util import load_instruction_from_file, get_client, text2event, save_image_from_bytes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleImagenAgent(BaseAgent):
    """
    A simplified Imagen agent that generates images from prompts and saves them locally.
    """
    
    # Class attributes (not Pydantic fields)
    client: Any = None
    config: dict = None
    
    # Pydantic fields
    name: str = Field(default="SimpleImageGenerator")
    description: str = Field(default="Generates images from prompts using Imagen")
    input_key: str = Field(default="image_prompts")
    output_key: str = Field(default="generated_images")
    
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        # Initialize client and config after super().__init__
        self.client = get_client()
        self.config = {
            "number_of_images": 1,
            "aspect_ratio": "1:1",  # Square for simplicity
            "output_mime_type": "image/jpeg",
            "person_generation": "ALLOW_ADULT"
        }
    
    @override
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Generates images from prompts in session state."""
        logger.info(f"[{self.name}] Starting image generation.")
        
        # Get prompts from session state
        prompts_data = ctx.session.state.get(self.input_key)
        if not prompts_data:
            error_msg = f"Input key '{self.input_key}' not found in session state."
            logger.error(f"[{self.name}] {error_msg}")
            yield text2event(self.name, error_msg)
            return
        
        # Handle both string and dict formats
        if isinstance(prompts_data, str):
            try:
                prompts_data = json.loads(prompts_data)
            except json.JSONDecodeError:
                error_msg = "Invalid JSON format for image prompts."
                logger.error(f"[{self.name}] {error_msg}")
                yield text2event(self.name, error_msg)
                return
        
        prompts = prompts_data.get("image_prompts", [])
        if not prompts:
            error_msg = "No image prompts found in the data."
            logger.error(f"[{self.name}] {error_msg}")
            yield text2event(self.name, error_msg)
            return
        
        logger.info(f"[{self.name}] Received {len(prompts)} prompt(s) for image generation.")
        
        # Create output directory
        output_dir = Path("output/images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_paths = []
        
        try:
            for i, prompt in enumerate(prompts):
                logger.info(f"[{self.name}] Generating image {i+1}/{len(prompts)}: '{prompt[:50]}...'")
                yield text2event(self.name, f"Generating image {i+1}/{len(prompts)}...")
                
                # Generate image using Imagen
                result = self.client.models.generate_images(
                    model="models/imagen-3.0-generate-002",
                    prompt=prompt,
                    config=self.config
                )
                
                if not result.generated_images:
                    error_msg = f"Image generation failed for prompt {i+1}."
                    logger.error(f"[{self.name}] {error_msg}")
                    yield text2event(self.name, error_msg)
                    continue
                
                # Save the first generated image
                image_bytes = result.generated_images[0].image.image_bytes
                image_path = output_dir / f"image_{i+1}.jpg"
                save_image_from_bytes(image_bytes, str(image_path))
                image_paths.append(str(image_path))
                
                logger.info(f"[{self.name}] Image {i+1} saved to '{image_path}'")
            
            # Store image paths in session state
            ctx.session.state[self.output_key] = image_paths
            
            final_message = f"Successfully generated {len(image_paths)} images in '{output_dir}'"
            yield text2event(self.name, final_message)
            
        except Exception as e:
            error_msg = f"An error occurred during image generation: {e}"
            logger.error(f"[{self.name}] {error_msg}", exc_info=True)
            yield text2event(self.name, error_msg)


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

# Sub-agent 3: Image Generator
image_generator_agent = SimpleImagenAgent(
    name="ImageGenerator",
    description="Generates images from prompts using Imagen",
    input_key="image_prompts",
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