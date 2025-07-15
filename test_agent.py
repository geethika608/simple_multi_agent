#!/usr/bin/env python3
"""
Test script for the Simple Multi-Agent Content Creator with Function Tools
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv

from agent import root_agent

def test_agent():
    """Test the multi-agent system with a sample prompt."""
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY not found in environment variables")
        print("Please create a .env file with your Google API key")
        return False
    
    print("🚀 Starting Simple Multi-Agent Content Creator Test (Function Tools)")
    print("=" * 60)
    
    # Setup session and runner
    session_service = InMemorySessionService()
    session = session_service.create_session("test_app", "test_user", "test_session")
    runner = Runner(agent=root_agent, session_service=session_service)
    
    # Test prompt
    test_prompt = "Create a script about the future of artificial intelligence and its impact on society"
    print(f"📝 Test Prompt: {test_prompt}")
    print()
    
    # Create user message
    content = types.Content(role="user", parts=[types.Part(text=test_prompt)])
    
    try:
        print("🔄 Running the multi-agent workflow...")
        print("-" * 40)
        
        # Run the agent
        events = runner.run(user_id="test_user", session_id="test_session", new_message=content)
        
        # Process events
        for event in events:
            if event.is_final_response():
                print("\n✅ Final Response:")
                print("=" * 40)
                print(event.content.parts[0].text)
                print("=" * 40)
            else:
                # Print intermediate events for debugging
                if hasattr(event, 'content') and event.content and event.content.parts:
                    print(f"📤 {event.author}: {event.content.parts[0].text[:100]}...")
        
        print("\n🎉 Test completed successfully!")
        print("\n📁 Check the 'output/' directory for generated files:")
        
        # List generated files
        output_dir = Path("output")
        if output_dir.exists():
            for item in output_dir.rglob("*"):
                if item.is_file():
                    print(f"   📄 {item}")
        else:
            print("   No output directory found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_function_tool_directly():
    """Test the function tool directly without the agent workflow."""
    
    print("\n🔧 Testing Function Tool Directly")
    print("=" * 40)
    
    try:
        from tools import generate_multiple_images_tool, GenerateMultipleImagesRequest
        
        # Test request
        test_request = GenerateMultipleImagesRequest(
            prompts=[
                "A futuristic robot in a modern laboratory",
                "A beautiful sunset over a city skyline"
            ],
            aspect_ratio="1:1",
            output_prefix="test"
        )
        
        print("📝 Testing with prompts:")
        for i, prompt in enumerate(test_request.prompts, 1):
            print(f"   {i}. {prompt}")
        
        # Call the function directly
        result = generate_multiple_images_tool.function(test_request)
        
        print(f"\n✅ Function Tool Result:")
        print(f"   Success: {result.success}")
        print(f"   Image Paths: {result.image_paths}")
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        return result.success
        
    except Exception as e:
        print(f"❌ Error testing function tool: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Simple Multi-Agent Content Creator - Function Tools Test")
    print("=" * 70)
    
    # Test function tool first
    tool_success = test_function_tool_directly()
    
    if tool_success:
        print("\n" + "="*70)
        # Test full agent workflow
        agent_success = test_agent()
        
        if agent_success:
            print("\n🎊 All tests passed! The function tool approach is working correctly.")
        else:
            print("\n⚠️  Agent workflow test failed, but function tool works.")
    else:
        print("\n❌ Function tool test failed. Please check your API key and Imagen access.") 