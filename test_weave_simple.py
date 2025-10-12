"""
Simple test to verify OpenTelemetry traces are sent to Weave
"""
import asyncio
from google.adk.runners import InMemoryRunner
from google.genai import types

# Import cmo_agent (this sets up OpenTelemetry automatically)
from cmo_agent import root_agent

async def test_simple():
    print("\n" + "="*60)
    print("🧪 Testing CMO Agent with OpenTelemetry Weave")
    print("="*60)
    
    # Set up runner
    runner = InMemoryRunner(agent=root_agent, app_name="cmo_agent")
    session_service = runner.session_service
    
    # Create a session
    user_id = "test_user"
    session_id = "test_session_simple"
    await session_service.create_session(
        app_name="cmo_agent",
        user_id=user_id,
        session_id=session_id,
    )
    
    print("\n📝 Sending message to agent...")
    print("   Message: 'Hello, what can you do?'")
    print("   (This should trigger tool calls and create traces)\n")
    
    # Run the agent with a simple message
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(
            role="user",
            parts=[types.Part(text="Hello, what can you do? Just give me a brief overview.")]
        ),
    ):
        if event.is_final_response() and event.content:
            response = event.content.parts[0].text.strip()
            print("✅ Response received:")
            print(f"\n{response}\n")
    
    print("="*60)
    print("🐝 Check Weave dashboard for traces:")
    print("   URL: https://wandb.ai/mason-choi-storika/mason-test")
    print("   Look for:")
    print("   - Agent execution traces")
    print("   - Tool invocations")
    print("   - LLM calls")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_simple())

