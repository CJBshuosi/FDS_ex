"""
Causal Length Set (CLS) - A CRDT (Conflict-free Replicated Data Type)
Counter-based set membership representation:
    - Odd counter (1, 3, 5, ...) = item IS in the set
    - Even counter (0, 2, 4, ...) = item is NOT in the set

Example: Item 'Milk' with counter progression:
    add('Milk') -> counter=1 (odd, in set)
    remove('Milk') -> counter=2 (even, not in set)
    add('Milk') -> counter=3 (odd, in set again)
"""

class CLS:  # Causal Length Set implementation
    def __init__(self):
        self.cart = {}

    def add(self, item):  # Add item to the set
        if item not in self.cart:
            self.cart[item] = 1  # Create with counter=1 (odd, in set)
        elif self.cart[item] % 2 == 0:
            self.cart[item] += 1  # Increment to make it odd (add to set)

    def remove(self, item):  # Remove item from the set
        if item in self.cart and self.cart[item] % 2 == 1:
            self.cart[item] += 1  # Increment to make it even (remove from set)

    def contains(self, item):
        return item in self.cart and self.cart[item] % 2 == 1  # Return True if counter is odd

    def mutual_sync(self, other_carts):  # Synchronize with other CLS replicas
        mutual_cart = self.cart.copy()

        # Merge all other carts by taking maximum counter for each item
        for other in other_carts:
            for item, counter in other.cart.items():  # For each item in other replica
                if item in mutual_cart:  # If item already in merged cart
                    mutual_cart[item] = max(mutual_cart[item], counter)  # Take maximum counter
                else:
                    mutual_cart[item] = counter  # Add item with its counter

        # Update all replicas with merged state
        self.cart = mutual_cart
        for other in other_carts:
            other.cart = mutual_cart


if __name__ == "__main__":

    alice_list = CLS()
    bob_list = CLS()

    # Step 1: Alice adds items to her list, Add somthing: counter 1 (odd, in set)
    alice_list.add('Milk')
    alice_list.add('Potato')
    alice_list.add('Eggs')

    # Step 2: Bob adds items to his list (independently)
    bob_list.add('Sausage')
    bob_list.add('Mustard')
    bob_list.add('Coke')
    bob_list.add('Potato')

    # Step 3: Bob syncs with Alice (merge their lists)
    bob_list.mutual_sync([alice_list])

    # Step 4: Alice makes changes to her list
    alice_list.remove('Sausage')  # Remove Sausage: counter 1->2 (even, not in set)
    alice_list.add('Tofu')
    alice_list.remove('Potato')


    # Step 5: Alice syncs with Bob (merge again)
    alice_list.mutual_sync([bob_list])  # Take max counters for each item
  

    # Step 6: Check if Potato is in Bob's list
    print("Bob's list contains 'Potato'?", bob_list.contains('Potato'))