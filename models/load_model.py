from langchain_openai import ChatOpenAI
from langchain_community.llms.ollama import Ollama

def load_model(model_name="gpt-4o", api_key=None, base_url=None, **kwargs):
    if api_key is None and base_url is None:
        model = ChatOpenAI(model_name=model_name, **kwargs)
    elif api_key is not None and base_url is None:
        model = ChatOpenAI(model_name=model_name, api_key=api_key, **kwargs)
    elif api_key is None and base_url is not None:
        model = ChatOpenAI(model_name=model_name, base_url=base_url, **kwargs)
    else:
        model = ChatOpenAI(model_name=model_name, api_key=api_key, base_url=base_url, **kwargs)
    return model

def load_model_ollama(model_name="llama3", **kwargs):
    model = Ollama(model=model_name, **kwargs)
    return model