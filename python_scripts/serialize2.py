import pickle
import pickletools

class Node:
    def __init__(self, data):
        self.data = data
        self.children = []

    def add_child(self, obj):
        self.children.append(obj)

    def __reduce__(self):
        return (self.__class__, (self.data, ))    

node = Node({"int": 1, "float": 2.0})
#data = pickle.dumps(node)
#print data
# Get state using protocol 3
constructor, _, state, _, _ = node.__reduce__()
# create an empty instance
# or node = Node.__new__(Node)
node = constructor(Node)
# replace instance's dictionary
instance_dict = node.__dict__
for k, v in state.items():
    instance_dict[k] = v
print(node.data)