"""
Implement causal length set (CLS) with add, remove, contains and mutual_sync methods.
In the set we represent each item with a counter. The counter represents if the item is in the set or not:
    counter is even -> item is not in the set
    counter is odd -> item is in the set
"""
class CLS:
    # We store items in a dictionary with counters
    def __init__(self):
        self.cart = {}

    """
    Add item to the set
    If item is not in the set, add it with counter 1
    If item is in the set with even counter, increment counter by 1 (making it odd -> in the set now)
    """
    def add(self, item):
        if item not in self.cart:
            self.cart[item] = 1
        elif self.cart[item] % 2 == 0:
            self.cart[item] += 1

    """
    Remove item from the set
    If item is in the set with odd counter, increment counter by 1 (making it even -> not in the set anymore)
    """
    def remove(self, item):
        if item in self.cart and self.cart[item] % 2 == 1:
            self.cart[item] += 1

    """
    Check if item is in the set
    If item is in the set with odd counter, return True
    """
    def contains(self, item):
        return item in self.cart and self.cart[item] % 2 == 1

    """
    Synchronize all CLS 
    """
    def mutual_sync(self, other_carts):
        mutual_cart = self.cart.copy()
        for other in other_carts:
            for item, counter in other.cart.items():
                if item in mutual_cart:
                    mutual_cart[item] = max(mutual_cart[item], counter)
                else:
                    mutual_cart[item] = counter
        
        self.cart = mutual_cart
        for other in other_carts:
            other.cart = mutual_cart


if __name__ == "__main__":
    # Test cases from exercise description
    alice_list = CLS()
    bob_list = CLS()

    alice_list.add('Milk')
    alice_list.add('Potato')
    alice_list.add('Eggs')

    bob_list.add('Sausage')
    bob_list.add('Mustard')
    bob_list.add('Coke')
    bob_list.add('Potato')
    bob_list.mutual_sync([alice_list])

    alice_list.remove('Sausage')
    alice_list.add('Tofu')
    alice_list.remove('Potato')
    alice_list.mutual_sync([bob_list])

    print("Bob's list contains 'Potato'?", bob_list.contains('Potato'))