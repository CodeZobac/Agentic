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
        elif tool_name == "file_writer":
            return AgentToolFactory.create_file_writer_tool(tool_config)
        elif tool_name == "file_reader":
            return AgentToolFactory.create_file_reader_tool(tool_config)
        elif tool_name == "directory_reader":
            return AgentToolFactory.create_directory_reader_tool(tool_config)
        elif tool_name == "serper_dev_tool":
            return AgentToolFactory.create_serper_dev_tool(tool_config)
        elif tool_name == "website_search_tool":
            return AgentToolFactory.create_website_search_tool(tool_config)
        # Add more tools as needed
        return None

    @staticmethod
    def create_serper_dev_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a SerperDevTool for agents (placeholder).
        Requires SERPER_API_KEY environment variable.
        Args:
            config: Configuration for the SerperDevTool.
        Returns:
            Callable: SerperDevTool function.
        """
        @tool
        def serper_dev_tool(query: str) -> str:
            """Search the web using Serper API for up-to-date information.
            Args:
                query (str): The search query.
            """
            # WIP this would use the SerperDevTool from crewai_tools
            # and require a SERPER_API_KEY environment variable.
            api_key = os.getenv("SERPER_API_KEY")
            if not api_key:
                return "Error: SERPER_API_KEY not set. This tool requires an API key for serper.dev."
            return f"SerperDevTool search results for: {query} (API Key: {api_key[:4]}...)"
        return serper_dev_tool

    @staticmethod
    def create_website_search_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a WebsiteSearchTool for agents (placeholder).
        Args:
            config: Configuration for the WebsiteSearchTool.
        Returns:
            Callable: WebsiteSearchTool function.
        """
        @tool
        def website_search_tool(website_url: str, query: str) -> str:
            """Search a specific website for information.
            Args:
                website_url (str): The URL of the website to search.
                query (str): The search query.
            """
            # WIP this would use the WebsiteSearchTool from crewai_tools.
            return f"WebsiteSearchTool results for '{query}' on {website_url}"
        return website_search_tool

    @staticmethod
    def create_directory_reader_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a directory reader tool for agents.

        Args:
            config: Configuration for the directory reader tool.

        Returns:
            Callable: Directory reader tool function.
        """
        @tool
        def directory_reader(directory_path: str) -> str:
            """Read and list contents of a specified directory.
            Args:
                directory_path (str): The path to the directory.
            """
            try:
                if not os.path.exists(directory_path):
                    return f"Error: Directory not found at {directory_path}"
                if not os.path.isdir(directory_path):
                    return f"Error: Path is not a directory {directory_path}"
                
                items = os.listdir(directory_path)
                return f"Contents of {directory_path}:\n" + "\n".join(items)
            except Exception as e:
                return f"Error reading directory {directory_path}: {str(e)}"
        return directory_reader

    @staticmethod
    def create_file_writer_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a file writer tool for agents.

        Args:
            config: Configuration for the file writer tool.

        Returns:
            Callable: File writer tool function.
        """
        @tool
        def file_writer(file_path: str, content: str) -> str:
            """Write content to a specified file.
            Args:
                file_path (str): The path to the file where content will be written.
                content (str): The content to write to the file.
            """
            try:
                # Ensure directory exists
                directory = os.path.dirname(file_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return f"Successfully wrote to {file_path}"
            except Exception as e:
                return f"Error writing to file {file_path}: {str(e)}"
        return file_writer

    @staticmethod
    def create_file_reader_tool(config: Dict[str, Any]) -> Callable:
        """
        Create a file reader tool for agents.

        Args:
            config: Configuration for the file reader tool.

        Returns:
            Callable: File reader tool function.
        """
        @tool
        def file_reader(file_path: str) -> str:
            """Read content from a specified file.
            Args:
                file_path (str): The path to the file to be read.
            """
            try:
                if not os.path.exists(file_path):
                    return f"Error: File not found at {file_path}"
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"Error reading file {file_path}: {str(e)}"
        return file_reader
    
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
