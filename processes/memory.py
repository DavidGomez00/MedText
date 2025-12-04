class Memory:
    def __init__(self):
        self.storage = {}
        
    def _add_field(self, field_name, value, process_id):
        '''Adds a new field to memory.'''
        self.storage[field_name] = {
                'value': value,
                'process_id': process_id # Which process updated this field
            }
    
    
    def update_field(self, field_name, value, process_id):
        '''Updates or adds a field in memory. Returns the field dict.'''
        if field_name in self.storage:
            self.storage[field_name]['value'] = value
            self.storage[field_name]['process_id'] = process_id
        else:
            self._add_field(field_name, value, process_id)
        
        return self.storage[field_name]
    
    
    def get(self, field_name):
        '''Gets a field from memory. Returns None if not found.'''
        return self.storage.get(field_name, None)
