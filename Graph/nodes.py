class node::
    def __init__(self, name, description=None, parents=None, children=None):
        self.name = name
        self.description = description
        self.parents = parents if parents is not None else []
        self.children = children if children is not None else []

    def _add_child(self, child_node):
        self.children.append(child_node)

    def get_children(self):
        return self.children
    def __repr__(self):
        return f"Node({self.name})"