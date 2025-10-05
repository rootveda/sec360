#!/usr/bin/env python3
"""
Ollama Integration for Sec360 Security Analysis
Provides offline LLM capabilities using local Ollama models
"""

import requests
import json
import time
import subprocess
import os
import platform
from typing import Dict, List, Optional, Generator
import threading
import queue

# Import Mac Silicon optimizer if available
try:
    from .mac_silicon_optimizer import MacSiliconOptimizer
    MAC_SILICON_OPTIMIZER_AVAILABLE = True
except ImportError:
    MAC_SILICON_OPTIMIZER_AVAILABLE = False

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.current_model = None
        self.is_running = False
        
        # Initialize Mac Silicon optimizer if available
        if MAC_SILICON_OPTIMIZER_AVAILABLE and platform.machine() == "arm64":
            self.optimizer = MacSiliconOptimizer()
            self.optimizer.optimize_system_settings()
        else:
            self.optimizer = None
        
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.is_running = True
                return True
        except requests.exceptions.RequestException:
            pass
        
        self.is_running = False
        return False
    
    def start_ollama(self) -> bool:
        """Start Ollama service"""
        try:
            # Try to start Ollama service
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for service to start
            for _ in range(30):  # Wait up to 30 seconds
                if self.check_ollama_status():
                    return True
                time.sleep(1)
            
            return False
        except Exception as e:
            print(f"Error starting Ollama: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        if not self.check_ollama_status():
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
                return self.available_models
        except Exception as e:
            print(f"Error getting models: {e}")
        
        return []
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model from Ollama registry"""
        if not self.check_ollama_status():
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                stream=True
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if data.get("status") == "success":
                            return True
                        elif data.get("error"):
                            print(f"Error pulling model: {data['error']}")
                            return False
        except Exception as e:
            print(f"Error pulling model {model_name}: {e}")
        
        return False
    
    def set_model(self, model_name: str) -> bool:
        """Set the current model"""
        if model_name in self.available_models:
            self.current_model = model_name
            return True
        return False
    
    def generate_response(self, prompt: str, stream: bool = False) -> Optional[str]:
        """Generate response from the current model"""
        if not self.current_model or not self.check_ollama_status():
            return None
        
        try:
            payload = {
                "model": self.current_model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": 0.0,  # Set to 0 for deterministic results
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "seed": 42  # Fixed seed for reproducibility
                }
            }
            
            # Add Mac Silicon optimizations if available
            if self.optimizer:
                optimized_config = self.optimizer.optimize_ollama_config()
                payload.update(optimized_config)
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return self._handle_stream_response(response)
                else:
                    data = response.json()
                    # Return full response data for token counting and timing info
                    return data
        except Exception as e:
            print(f"Error generating response: {e}")
        
        return None
    
    def _handle_stream_response(self, response) -> Generator[str, None, None]:
        """Handle streaming response"""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode('utf-8'))
                    if "response" in data:
                        yield data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
    
    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> tuple[Optional[str], Optional[Dict]]:
        """Chat with the model using conversation format"""
        if not self.current_model or not self.check_ollama_status():
            return None, None
        
        try:
            payload = {
                "model": self.current_model,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": 0.0,  # Set to 0 for deterministic results
                    "top_p": 0.9,
                    "repeat_penalty": 1.1,
                    "seed": 42  # Fixed seed for reproducibility
                }
            }
            
            # Add Mac Silicon optimizations if available
            if self.optimizer:
                optimized_config = self.optimizer.optimize_ollama_config()
                payload.update(optimized_config)
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=stream
            )
            
            if response.status_code == 200:
                if stream:
                    return self._handle_stream_response(response), None
                else:
                    data = response.json()
                    content = data.get("message", {}).get("content", "")
                    # Extract token usage and performance metrics
                    token_info = {
                        "prompt_tokens": data.get("prompt_eval_count", 0),
                        "completion_tokens": data.get("eval_count", 0),
                        "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
                        "eval_duration": data.get("eval_duration", 0),
                        "load_duration": data.get("load_duration", 0),
                        "total_duration": data.get("total_duration", 0),
                        "model": self.current_model
                    }
                    return content, token_info
        except Exception as e:
            print(f"Error in chat: {e}")
        
        return None, None

class LLMSafetyTrainer:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.conversation_history = []
        self.current_session_id = None
        self.session_start_time = None
        
    def start_practice_session(self, user_id: str, model_name: str = "llama2") -> bool:
        """Start a new practice session"""
        # Check if Ollama is running
        if not self.ollama_client.check_ollama_status():
            print("Starting Ollama service...")
            if not self.ollama_client.start_ollama():
                print("Failed to start Ollama service")
                return False
        
        # Get available models
        models = self.ollama_client.get_available_models()
        if not models:
            print("No models available. Please pull a model first.")
            return False
        
        # Set model
        if model_name not in models:
            print(f"Model {model_name} not found. Available models: {models}")
            return False
        
        self.ollama_client.set_model(model_name)
        self.current_session_id = f"session_{user_id}_{int(time.time())}"
        self.conversation_history = []
        
        # Record session start time
        self.session_start_time = time.time()
        
        print(f"Practice session started with model: {model_name}")
        return True
    
    def send_message(self, message: str, user_id: str) -> tuple[str, Optional[Dict]]:
        """Send a message to the LLM and get response"""
        if not self.current_session_id:
            return "No active session. Please start a practice session first.", None
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # Add system prompt if not already present
        if not self.conversation_history or self.conversation_history[0]["role"] != "system":
            system_prompt = """You are an AI Security Mentor helping users learn secure coding practices. 

Your role is to:
1. Analyze code for potential data leaks (API keys, PII, medical records, internal infrastructure)
2. Explain what was detected and why it's a security risk
3. Provide specific, actionable fixes for the identified issues
4. Teach secure coding practices and best practices
5. Keep responses concise, clear, and educational

When analyzing code:
- Point out specific lines or patterns that contain sensitive data
- Explain the security risk clearly
- Provide concrete examples of how to fix the issues
- Focus on practical solutions

Be helpful, educational, and security-focused in all responses."""
            
            self.conversation_history.insert(0, {"role": "system", "content": system_prompt})
        
        # Generate response
        response, token_info = self.ollama_client.chat(self.conversation_history)
        
        if response:
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            return response, token_info
        else:
            return "Error generating response. Please check Ollama service.", None
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the current conversation history"""
        return self.conversation_history
    
    def end_session(self) -> Dict:
        """End the current practice session"""
        if not self.current_session_id:
            return {"error": "No active session"}
        
        # Record session end time
        session_end_time = time.time()
        
        # Calculate session duration
        session_duration = session_end_time - getattr(self, 'session_start_time', session_end_time)
        
        session_data = {
            "session_id": self.current_session_id,
            "conversation_history": self.conversation_history,
            "start_time": getattr(self, 'session_start_time', session_end_time),
            "end_time": session_end_time,
            "duration_seconds": session_duration,
            "duration_minutes": session_duration / 60.0
        }
        
        self.current_session_id = None
        self.conversation_history = []
        self.session_start_time = None
        
        return session_data

def setup_recommended_models():
    """Setup recommended models for practice - optimized for Mac Silicon"""
    import platform
    
    client = OllamaClient()
    
    if not client.check_ollama_status():
        print("Starting Ollama service...")
        if not client.start_ollama():
            print("Failed to start Ollama service")
            return False
    
            # Mac Silicon optimized models (smaller, faster, more efficient)
            if platform.machine() == "arm64":  # Mac Silicon
                recommended_models = [
                    "llama3.2:3b"      # Optimized for Mac Silicon, fast and efficient
                ]
                print("Setting up Mac Silicon optimized model...")
            else:
                # Fallback for Intel Macs
                recommended_models = [
                    "llama2:7b"        # Good balance of performance and resource usage
                ]
                print("Setting up standard model...")
    
    print("Setting up recommended models...")
    for model in recommended_models:
        print(f"Pulling model: {model}")
        if client.pull_model(model):
            print(f"Successfully pulled {model}")
        else:
            print(f"Failed to pull {model}")
    
    return True

if __name__ == "__main__":
    # Test Ollama integration
    client = OllamaClient()
    
    # Check status
    if client.check_ollama_status():
        print("Ollama is running")
        
        # Get available models
        models = client.get_available_models()
        print(f"Available models: {models}")
        
        if models:
            # Set a model
            client.set_model(models[0])
            
            # Test generation
            response = client.generate_response("Hello, how are you?")
            print(f"Response: {response}")
    else:
        print("Ollama is not running")
        print("Please install Ollama and start the service:")
        print("1. Install Ollama from https://ollama.ai")
        print("2. Run: ollama serve")
        print("3. Pull a model: ollama pull llama2")
