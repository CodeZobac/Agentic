#!/bin/bash

# Start the Ollama server
ollama serve &

# Wait for Ollama to start up
echo "Waiting for Ollama server to start..."
sleep 10

# Create the agentic-specialist model
echo "Creating agentic-specialist model..."
ollama create agentic-specialist -f /models/Modelfile

# Keep the container running
echo "Ollama server running with agentic-specialist model"
tail -f /dev/null