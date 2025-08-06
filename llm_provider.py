from abc import ABC, abstractmethod
from groq import Groq
from openai import OpenAI
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv()

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, prompt: str, context: str) -> str:
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        try:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            self.use_real_api = True
            print("OpenAI client initialized successfully.")
        except ImportError:
            print("OpenAI library not installed. Using mock responses.")
            self.use_real_api = False
        except Exception as e:
            print(f"Error initializing OpenAI client: {e}. Using mock responses.")
            self.use_real_api = False
    
    def generate(self, prompt: str, context: str) -> str:
        enhanced_prompt = f"Context: {context}\n\nUser Query: {prompt}\n\nPlease provide a helpful response based on the context."
        
        if self.use_real_api:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    temperature=0.1,
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error calling OpenAI API: {e}")
                return f"Error generating response. Mock response for: {prompt}"
        else:
            return f"Mock response based on context for: {prompt}"


class GeminiProvider(LLMProvider):
    """ChatGoogleGenerativeAI provider implementation"""
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model
        try:
            self.client = ChatGoogleGenerativeAI(model=self.model, temperature=0,api_key=os.getenv("GEMINI_API_KEY"))
            self.use_real_api = True
            print("ChatGoogleGenerativeAI client initialized successfully.")
        except ImportError:
            print("ChatGoogleGenerativeAI library not installed. Using mock responses.")
            self.use_real_api = False
        except Exception as e:
            print(f"Error initializing ChatGoogleGenerativeAI client: {e}. Using mock responses.")
            self.use_real_api = False

    def generate(self, prompt: str, context: str) -> str:
        enhanced_prompt = f"Context: {context}\n\nUser Query: {prompt}\n\nPlease provide a helpful response based on the context."
        
        if self.use_real_api:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        ("system", "You are a helpful assistant that answers questions based on provided context."),
                        ("user", enhanced_prompt)
                    ],
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error calling ChatGoogleGenerativeAI API: {e}")
                return f"Error generating response. Mock response for: {prompt}"
        else:
            return f"Mock response based on context for: {prompt}"
        
class LlamaProvider(LLMProvider):
    def __init__(self, model: str ="llama3-8b-8192"):
        self.model = model
        try:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            self.use_real_api = True
            print("Groq client initialized successfully.")
        except ImportError:
            print("Groq library not installed. Using mock responses.")
            self.use_real_api = False
        except Exception as e:
            print(f"Error initializing Groq client: {e}. Using mock responses.")
            self.use_real_api = False

    def generate(self, prompt: str, context: str) -> str:
        enhanced_prompt = f"Context: {context}\n\nUser Query: {prompt}\n\nPlease provide a helpful response based on the context."
        
        if self.use_real_api:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based on provided context."},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Error calling Groq API: {e}")
                return f"Error generating response. Mock response for: {prompt}"
        else:
            return f"Mock response based on context for: {prompt}"