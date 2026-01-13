# Binary Search Trees

## Definition

A Binary Search Tree (BST) is a binary tree data structure where:
- Each node has at most two children (left and right)
- Left subtree contains only nodes with values less than parent
- Right subtree contains only nodes with values greater than parent
- Both subtrees are also BSTs

## Properties

### BST Property
For every node n:
- All values in left subtree ≤ n.value
- All values in right subtree > n.value

### Time Complexity
| Operation | Average | Worst Case |
|-----------|---------|------------|
| Search    | O(log n)| O(n)       |
| Insert    | O(log n)| O(n)       |
| Delete    | O(log n)| O(n)       |

## Implementation

### Node Structure
```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
```

### Search Operation
```python
def search(root, target):
    if root is None or root.value == target:
        return root

    if target < root.value:
        return search(root.left, target)
    else:
        return search(root.right, target)
```

### Insert Operation
```python
def insert(root, value):
    if root is None:
        return TreeNode(value)

    if value < root.value:
        root.left = insert(root.left, value)
    else:
        root.right = insert(root.right, value)

    return root
```

### Delete Operation
Three cases to handle:
1. **Leaf node**: Simply remove
2. **One child**: Replace with child
3. **Two children**: Replace with inorder successor

```python
def delete(root, value):
    if root is None:
        return root

    if value < root.value:
        root.left = delete(root.left, value)
    elif value > root.value:
        root.right = delete(root.right, value)
    else:
        # Node found - handle three cases
        if root.left is None:
            return root.right
        elif root.right is None:
            return root.left

        # Two children: get inorder successor
        successor = find_min(root.right)
        root.value = successor.value
        root.right = delete(root.right, successor.value)

    return root
```

## Traversals

### Inorder (Left-Root-Right)
Produces sorted output:
```python
def inorder(root):
    if root:
        inorder(root.left)
        print(root.value)
        inorder(root.right)
```

### Preorder (Root-Left-Right)
```python
def preorder(root):
    if root:
        print(root.value)
        preorder(root.left)
        preorder(root.right)
```

### Postorder (Left-Right-Root)
```python
def postorder(root):
    if root:
        postorder(root.left)
        postorder(root.right)
        print(root.value)
```

## Balancing

Unbalanced trees degrade to O(n) operations. Solutions:
- **AVL Trees**: Height-balanced BST
- **Red-Black Trees**: Self-balancing BST
- **Splay Trees**: Self-adjusting BST

## Common Applications

1. **Database indexing**
2. **File system organization**
3. **Expression parsing**
4. **Priority queues**
5. **Symbol tables in compilers**

## Practice Problems

- Validate BST
- Find kth smallest element
- Lowest common ancestor
- Convert sorted array to BST
- Serialize and deserialize BST
