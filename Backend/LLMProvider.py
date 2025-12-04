"""
LLM Provider Abstraction Layer
Supports multiple AI providers: Groq, OpenAI, Anthropic, Cohere
"""
from pathlib import Path
from dotenv import dotenv_values
import os

BASE_DIR = Path(__file__).resolve().parent.parent
env_vars = dotenv_values(BASE_DIR / ".env")

# Get provider preference (defaults to "groq")
PROVIDER = env_vars.get("LLM_PROVIDER", "groq").lower()

class LLMClient:
    """Unified interface for different LLM providers"""
    
    def __init__(self):
        self.provider = PROVIDER
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider"""
        if self.provider == "groq":
            from groq import Groq
            api_key = env_vars.get("GROQ_API_KEY") or env_vars.get("GroqAPIKey")
            if api_key:
                self.client = Groq(api_key=api_key)
            else:
                print("[Warning] Groq API key not found. Set GROQ_API_KEY or GroqAPIKey in .env")
        
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = env_vars.get("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    print("[Warning] OpenAI API key not found. Set OPENAI_API_KEY in .env")
            except ImportError:
                print("[Error] OpenAI package not installed. Run: pip install openai")
        
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                api_key = env_vars.get("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = Anthropic(api_key=api_key)
                else:
                    print("[Warning] Anthropic API key not found. Set ANTHROPIC_API_KEY in .env")
            except ImportError:
                print("[Error] Anthropic package not installed. Run: pip install anthropic")
        
        elif self.provider == "cohere":
            try:
                import cohere
                api_key = env_vars.get("COHERE_API_KEY") or env_vars.get("CohereAPIKey")
                if api_key:
                    self.client = cohere.Client(api_key=api_key)
                else:
                    print("[Warning] Cohere API key not found. Set COHERE_API_KEY in .env")
            except ImportError:
                print("[Error] Cohere package not installed. Run: pip install cohere")
        
        else:
            print(f"[Error] Unknown provider: {self.provider}. Supported: groq, openai, anthropic, cohere")
    
    def get_model_name(self, default_model: str = None):
        """Get appropriate model name based on provider"""
        model_map = {
            "groq": {
                "default": "llama-3.1-8b-instant",
                "large": "llama-3.3-70b-versatile"
            },
            "openai": {
                "default": "gpt-3.5-turbo",
                "large": "gpt-4"
            },
            "anthropic": {
                "default": "claude-3-haiku-20240307",
                "large": "claude-3-opus-20240229"
            },
            "cohere": {
                "default": "command",
                "large": "command"
            }
        }
        
        if default_model:
            # If specific model provided, use it
            return default_model
        
        # Map Groq model names to provider equivalents
        if "70b" in str(default_model):
            return model_map.get(self.provider, {}).get("large", default_model)
        else:
            return model_map.get(self.provider, {}).get("default", default_model)
    
    def create_completion(self, model: str, messages: list, max_tokens: int = 2048, 
                         temperature: float = 0.7, top_p: float = 1, stream: bool = True, stop=None):
        """
        Create a chat completion using the configured provider
        Returns a streaming generator compatible with Groq's interface
        """
        if not self.client:
            raise ValueError(f"No client initialized for provider: {self.provider}")
        
        model_name = self.get_model_name(model)
        
        if self.provider == "groq":
            return self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=stream,
                stop=stop
            )
        
        elif self.provider == "openai":
            completion = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=stream,
                stop=stop
            )
            return completion
        
        elif self.provider == "anthropic":
            # Anthropic uses different message format
            system_msg = None
            conversation = []
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    conversation.append(msg)
            
            if stream:
                stream_obj = self.client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    system=system_msg if system_msg else "",
                    messages=conversation,
                    stream=True
                )
                # Convert Anthropic stream to Groq-like format
                return self._convert_anthropic_stream(stream_obj)
            else:
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    system=system_msg if system_msg else "",
                    messages=conversation
                )
                # Convert to Groq-like format
                class FakeChunk:
                    def __init__(self, content):
                        self.choices = [type('obj', (object,), {'delta': type('obj', (object,), {'content': content})()})()]
                return [FakeChunk(response.content[0].text)]
        
        elif self.provider == "cohere":
            # Cohere uses different API structure
            prompt = self._messages_to_cohere_prompt(messages)
            if stream:
                response = self.client.chat_stream(
                    model=model_name,
                    message=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    p=top_p
                )
                return self._convert_cohere_stream(response)
            else:
                response = self.client.chat(
                    model=model_name,
                    message=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    p=top_p
                )
                class FakeChunk:
                    def __init__(self, content):
                        self.choices = [type('obj', (object,), {'delta': type('obj', (object,), {'content': content})()})()]
                return [FakeChunk(response.text)]
        
        else:
            raise ValueError(f"Provider {self.provider} not implemented")
    
    def _convert_anthropic_stream(self, stream_obj):
        """Convert Anthropic stream to Groq-like format"""
        class StreamWrapper:
            def __init__(self, stream):
                self.stream = stream
            
            def __iter__(self):
                return self
            
            def __next__(self):
                chunk = next(self.stream)
                class FakeChunk:
                    def __init__(self, content):
                        self.choices = [type('obj', (object,), {'delta': type('obj', (object,), {'content': content})()})()]
                
                if hasattr(chunk, 'delta') and chunk.delta and hasattr(chunk.delta, 'text'):
                    return FakeChunk(chunk.delta.text)
                elif hasattr(chunk, 'type') and chunk.type == 'content_block_delta':
                    return FakeChunk(chunk.delta.text)
                else:
                    return FakeChunk("")
        
        return StreamWrapper(stream_obj)
    
    def _convert_cohere_stream(self, stream_obj):
        """Convert Cohere stream to Groq-like format"""
        class StreamWrapper:
            def __init__(self, stream):
                self.stream = stream
            
            def __iter__(self):
                return self
            
            def __next__(self):
                try:
                    chunk = next(self.stream)
                    class FakeChunk:
                        def __init__(self, content):
                            self.choices = [type('obj', (object,), {'delta': type('obj', (object,), {'content': content})()})()]
                    
                    if hasattr(chunk, 'text'):
                        return FakeChunk(chunk.text)
                    elif hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        return FakeChunk(chunk.delta.text)
                    else:
                        return FakeChunk("")
                except StopIteration:
                    raise
        
        return StreamWrapper(stream_obj)
    
    def _messages_to_cohere_prompt(self, messages):
        """Convert messages format to Cohere prompt"""
        prompt = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt += f"System: {content}\n\n"
            elif role == "user":
                prompt += f"User: {content}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n\n"
        return prompt

# Create a global client instance
llm_client = LLMClient()

