import processes.system as system


class Process:
    def __init__(self, dict, memory):
        self.name = dict.get('name')
        self.process_id = dict.get('process_id')
        self.required = dict.get('required', None)
        self.obtained = dict.get('obtained', None)
        self.next_step = dict.get('next_step', None)
        self.inner_processes = [Process(p_dict, memory) for p_dict in dict.get('processes', [])]
        
        self.dict = dict
        self.memory = memory
        
        self.status = "unknown"
    
    
    def _start(self):
        # If no required fields (None or empty), start immediately
        if not self.required:
            self.status = "started"
            return None

        # Otherwise ensure each required field is available
        for required_field in self.required:
            if not self._check_field_in_memory(required_field):
                return required_field

        self.status = "started"
        return None
    
    
    def _complete(self):
        # Check all obtained fields
        obtained_fields = self.dict['obtained']
        for obtained_field in obtained_fields:
            try:
                field = self._check_field_in_memory(obtained_field)
            except ValueError:
                print(f"Error: Field '{obtained_field}' could not be found or obtained in data.")
            
            if not field:
                return obtained_field
        
        self.status = "completed"
        return None
    
    
    def _check_field_in_memory(self, field):
        found_field = self.memory.get(field) # This is either None or the field found
        if found_field is None:
            value = system.find_field(field) # Try to find the field via an agent
            if value is None:
                raise ValueError(f"Field '{field}' not found in data.")
            # store found value in memory and continue
            self.memory.update_field(field, value, self.process_id)
        
        # TODO: Implement logic based on last_update_id if needed
        found_field = self.memory.get(field)
        last_update_id = found_field['process_id'] 

        return found_field
    
    
    def get_inner_processes(self):
        return self.inner_processes
    
    def __call__(self):
        if self.status == "unknown":
            missing_field = self._start()
            if missing_field is not None:
                return f"Process '{self.name}', ID {self.process_id} waiting for required field '{missing_field}.'"
        
        if self.status == "started":
            for process in self.inner_processes:
                result = process()
            missing_field = self._complete()
            if missing_field is not None:
                return f"Process '{self.name}', ID {self.process_id} waiting for obtained field '{missing_field}.'"
        
        if self.status == "completed":
            return f"Process '{self.name}' is completed."
        
        return f"Process '{self.name}' is in status '{self.status}'."