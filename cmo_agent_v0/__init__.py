"""
CMO (Chief Marketing Orchestrator) Agent
콘텐츠 생성, 평가, 발행을 조율하는 마케팅 오케스트레이터

Usage:
    from google.adk.runners import InMemoryRunner
    from google.genai import types
    import asyncio
    from cmo_agent import root_agent
    
    async def run():
        runner = InMemoryRunner(agent=root_agent, app_name="cmo_agent")
        # ... see agent.py for full example
    
    asyncio.run(run())
"""

from cmo_agent.agent import root_agent

__all__ = ['root_agent']

