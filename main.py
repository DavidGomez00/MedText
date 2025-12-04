from processes.memory import Memory
from processes.process import Process
import json

if __name__ == "__main__":
    
    with open('processes/processes.json', 'r') as f:
        processes_data = json.load(f)
    
    memory = Memory()
    main_process = Process(processes_data, memory)
    main_process()