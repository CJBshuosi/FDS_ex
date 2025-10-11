
class CLS:
    def __init__(self):
        self.items = set()

    def add(self, item):
        pass

    def remove(self, item):
        pass

    def contains(self, item):
        pass

    def mutual_sync(self, other_lists):
        pass

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
    pass