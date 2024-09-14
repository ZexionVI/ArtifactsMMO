import sys

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class SearchTree:
    def __init__(self):
        self.root = None

    def add(self, value):
        if self.root == None:
            self.root = Node(value)
        else:
            self._add_recursive(self.root, value)

    def _add_recursive(self, node, value):
        if value == node.value:
            return
        elif value < node.value:
            if node.left is None:
                node.left = Node(value)
            else:
                self._add_recursive(node.left, value)
        else:
            if node.right is None:
                node.right = Node(value)
            else:
                self._add_recursive(node.right, value)

    def height(self):
        return self._height_recursive(self.root)

    def _height_recursive(self, node):
        if node is None:
            return 0
        left_height = self._height_recursive(node.left)
        right_height = self._height_recursive(node.right)
        return max(left_height, right_height) + 1


def main():
    bst = SearchTree()
    values = list(map(int, input().split()))
    for value in values:
        if value == 0:
            break
        bst.add(value)

    # Вывод высоты дерева
    print(bst.height())
    
    pass


if __name__ == '__main__':
    main()

#Вводить надо числа подряд в одну строку. Ноль заканчивает ввод чисел. Выводит высоту дерева