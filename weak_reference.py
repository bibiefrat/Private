import gc
import weakref

class Node(object):
    def __init__(self, val):
        self.val = val
        self._left = None
        self._right = None
        self.parent = None

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, new_left_child):
        self._left = new_left_child
        self._left.parent = weakref.proxy(self)

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, new_left_child):
        self._right = new_left_child
        self._right.parent = weakref.proxy(self)


def main():
    root = Node(10)
    root.left = Node(20)
    root.left.left = Node(30)
    root.left.right = Node('hello')
    print('>>>> {} <<<< '.format(len(gc.get_objects())))
    # print(root.left.parent.val)

# how many objects in memory
print(len(gc.get_objects()))
main()
print(len(gc.get_objects()))






