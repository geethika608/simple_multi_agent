#!/usr/bin/env python3
"""
Test script for the Simple Multi-Agent Content Creator
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
    
    print("🚀 Starting Simple Multi-Agent Content Creator Test")
    print("=" * 50)
    
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
        print("🤖 Running agents...")
        print("-" * 30)
        
        # Run the agent
        events = runner.run(user_id="test_user", session_id="test_session", new_message=content)
        
        # Process events
        for event in events:
            if hasattr(event, 'content') and event.content and event.content.parts:
                message = event.content.parts[0].text
                print(f"[{event.author}]: {message}")
                
                if event.is_final_response():
                    print()
                    print("✅ Agent workflow completed successfully!")
                    
                    # Check session state for outputs
                    state = session.state.to_dict()
                    print("\n📊 Session State Summary:")
                    print(f"   - Script: {'✅' if 'generated_script' in state else '❌'}")
                    print(f"   - Image Prompts: {'✅' if 'image_prompts' in state else '❌'}")
                    print(f"   - Generated Images: {'✅' if 'generated_images' in state else '❌'}")
                    print(f"   - Final Summary: {'✅' if 'final_content_summary' in state else '❌'}")
                    
                    # Show script if available
                    if 'generated_script' in state:
                        print(f"\n📄 Generated Script:")
                        print("-" * 20)
                        print(state['generated_script'])
                    
                    # Show image paths if available
                    if 'generated_images' in state:
                        print(f"\n🖼️  Generated Images:")
                        print("-" * 20)
                        for i, img_path in enumerate(state['generated_images'], 1):
                            print(f"   {i}. {img_path}")
                    
                    # Show final summary if available
                    if 'final_content_summary' in state:
                        print(f"\n📋 Final Content Summary:")
                        print("-" * 20)
                        print(state['final_content_summary'])
                    
                    return True
        
        print("❌ No final response received")
        return False
        
    except Exception as e:
        print(f"❌ Error during agent execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_agent()
    if success:
        print("\n🎉 Test completed successfully!")
        print("You can now use 'adk web' to start the web interface")
    else:
        print("\n💥 Test failed. Please check the error messages above.")
        sys.exit(1) 