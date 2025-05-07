"""
Core agent factory and utilities for creating Crew AI agents.
"""
from typing import Dict, List, Optional, Any, Union, Callable
import os
import json

from crewai import Agent as CrewAgent
from langchain.tools import tool
from langchain_community.llms import Ollama

from backend.core.config import settings
from backend.db.models import Agent, AgentConfig


class AgentFactory:
    """
    Factory for creating CrewAI agents from database models.
    """
    
    @staticmethod
    def create_agent(agent_model: Agent) -> CrewAgent:
        """
        Create a CrewAI agent from a database model.
        
        Args:
            agent_model: Database agent model.
            
        Returns:
            CrewAgent: CrewAI agent instance.
        """
        # Get configuration for the agent
        config = agent_model.config
        
        # Default configuration if none exists
        llm_config = {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
            "temperature": 0.7,
            "verbose": False
        }
        
        # Override with agent-specific config if available
        if config:
            # Only override the model if it's specified and not empty
            if config.model:
                llm_config["model"] = config.model
            llm_config["temperature"] = config.temperature
            llm_config["verbose"] = config.verbose
        
        # Create language model using Ollama
        if llm_config["model"] == "agentic-specialist" or (
            ":" in llm_config["model"] and "ollama" not in llm_config["model"]
        ):
            # For Ollama models, prefix with "ollama/" to help LiteLLM identify the provider
            llm_config["model"] = f"ollama/{llm_config['model']}"
            
        llm = Ollama(**llm_config)
        
        # Create tools list if available
        tools = []
        if config and config.tools:
            tools = config.tools.get("tools", [])
        
        # Create and return crew agent
        crew_agent = CrewAgent(
            role=agent_model.role,
            goal=agent_model.goal,
            backstory=agent_model.backstory or "",
            verbose=llm_config["verbose"],
            llm=llm,
            tools=tools,
            allow_delegation=config.allow_delegation if config else True
        )
        
        return crew_agent


class AgentToolFactory:
    """
    Factory class for creating Langchain tools for Crew AI agents.
    """
    
    @staticmethod
    def get_tool(tool_name: str, tool_config: Dict[str, Any]) -> Optional[Callable]:
        """
        Get a Langchain tool function by name and configuration.
        
        Args:
            tool_name: Name of the tool.
            tool_config: Configuration for the tool.
            
        Returns:
            Optional[Callable]: Configured tool function if found.
        """
        # Implement basic tools
        if tool_name == "search":
            return AgentToolFactory.create_search_tool(tool_config)
        elif tool_name == "calculator":
            return AgentToolFactory.create_calculator_tool(tool_config)
        # Add more tools as needed
        return None
    
    @staticmethod
    def create_search_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a search tool for agents.
        
        Args:
            config: Configuration for the search tool.
            
        Returns:
            Callable: Search tool function.
        """
        @tool
        def search(query: str) -> str:
            """Search the web for information about a topic."""
            # Implement actual search functionality or use a placeholder
            return f"Search results for: {query}"
        
        return search
    
    @staticmethod
    def create_calculator_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a calculator tool for agents.
        
        Args:
            config: Configuration for the calculator tool.
            
        Returns:
            Callable: Calculator tool function.
        """
        @tool
        def calculator(expression: str) -> str:
            """Evaluate a mathematical expression."""
            try:
                # Simple and safe eval for basic calculations
                result = eval(expression, {"__builtins__": {}}, {"abs": abs, "max": max, "min": min, "round": round, "sum": sum})
                return f"Result: {result}"
            except Exception as e:
                return f"Error calculating: {str(e)}"
        
        return calculator