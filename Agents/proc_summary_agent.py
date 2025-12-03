import requests
import os


class agent:
    '''Base class for agents.'''
    def __init__(self):
        self.name = "base_agent"
        self.prompt = None
        
    def get_name(self):
        return self.name
    
    def set_prompt(self, prompt):
        self.prompt = prompt
        
    def __call__(self, *args, **kwds):
        pass


class proc_summary_agent(agent):
    '''Agent for process summary generation.'''
    def __init__(self):
        self.name = "proc_summary_agent"
        
        with open("proc_summary_prompt.txt", "r") as file:
            self.set_prompt(file.read())
        
    def get_prompt(self):
        return self.prompt
    
    def set_prompt(self, new_prompt):
        self.prompt = new_prompt
        
    def __call__(self, text_chunk):
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": text_chunk }
        ]
        
        response = requests.post(
            url=os.getenv("OLLAMA_API_URL") + "/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "model": "llama3.1:8b",
                "messages": messages,
                "stream": False,
                "options": {
                    "max_tokens": 1000,
                    "temperature": 0.5
                }
            }
        ).json()
        
        return response['message']['content']
        

if __name__ == "__main__":
    # Example usage
    agent_instance = proc_summary_agent()
    
    # Load a text chunk for testing
    with open(os.path.join("json", "NCCN-guide.json"), "r") as f:
        chunks = json.load(f)   
    
    used_chunk = chunks['chunk_10']  # For example, using the 10th chunk
    
    # Call the agent
    summary = agent_instance(used_chunk)
    
    print("Generated Process Summary:")
    print(summary)
        