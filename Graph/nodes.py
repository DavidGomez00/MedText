class node:
    def __init__(self, name, description=None, parents=None, children=None):
        self.name = name
        self.description = description
        self.parents = parents if parents is not None else []
        self.children = children if children is not None else []

    def _add_child(self, child_node):
        self-

    def get_edges(self):
        return self.edges

    def __repr__(self):
        return f"Node({self.value})"