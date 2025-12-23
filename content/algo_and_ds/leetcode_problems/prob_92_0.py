# Deinition for singly-linked list
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_linked_list(head: ListNode, left: int, right: int) -> ListNode:
     # 1. Initialize Dummy Node
    dummy = ListNode(0)
    dummy.next = head
    
    # 2. Find the Predecessor of the Rerversal Section
    prev = dummy
    for _ in range(left - 1):
        prev = prev.next

    # current -> will point to the first node to be reversed
    current = prev.next

    # 3. Perform the Reversal
    for _ in range(right - left):
        # 1. Isolate the node to be moved
        temp_next = current.next

        # 2. Reverse the link
        current.next = temp_next.next

        # 3. Re-link: Insert the isolated node
        temp_next.next = prev.next
        prev.next = temp_next

    # 4. Return the new head of the list
    return dummy.next

def list_to_linked_list(lst_):
    if not lst_:
        return None

    # 1. CReate a dummy head
    dummy = ListNode(0)
    current_node = dummy

    # 2. Iterate through the array and link the nodes
    for el in lst_:
        current_node.next = ListNode(el)
        current_node = current_node.next

    # The actual head of the list is the node after the dummy
    return dummy.next

def print_linked_list(head: ListNode) -> list:
    values = []
    current = head
    while current:
        values.append(current.val)
        current = current.next

    print(values)
    return values

left = 2
right = 4
head = list_to_linked_list([1, 2, 3, 4, 5])
print_linked_list(head)
rev_lk_lst = reverse_linked_list(head, left, right)
print_linked_list(rev_lk_lst)
