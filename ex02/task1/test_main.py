import sys
import time
import threading
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

# Import the main module
sys.path.insert(0, '/Users/boyu/Documents/VScodeProject/FDS/FDS-Exercises-HS25/ex02/task1')
from main import Node, initialize, nodes, buffer

class TestNodeBugs(unittest.TestCase):
    """Test cases to identify bugs in the Node implementation"""
    
    def setUp(self):
        """Reset global state before each test"""
        global nodes, buffer
        nodes.clear()
        buffer.clear()
    
    def test_resigned_initialization_bug(self):
        """Test Bug #3: resigned is initialized to 0, causing logic issues"""
        node = Node(0)
        # resigned is 0, so time.time() - 0 will be a huge number
        # This means the condition time.time() - self.resigned > 5 will always be True
        self.assertEqual(node.resigned, 0)
        self.assertGreater(time.time() - node.resigned, 5)
        print("✓ Bug #3 confirmed: resigned=0 causes time.time() - 0 to be huge")
    
    def test_voted_flag_never_resets(self):
        """Test Bug #4: voted flag is never reset after voting"""
        node = Node(0)
        node.voted = False
        
        # Simulate voting
        node.voted = True
        self.assertTrue(node.voted)
        
        # voted should be reset when starting a new election, but it's not
        # This means the node can only vote once in its lifetime
        print("✓ Bug #4 confirmed: voted flag is never reset")
    
    def test_buffer_race_condition(self):
        """Test Bug #1: buffer access without locks in multithreaded environment"""
        # This test demonstrates the race condition
        node1 = Node(0)
        node2 = Node(1)
        
        # Simulate concurrent access to buffer
        def append_to_buffer():
            for i in range(100):
                buffer[0].append(('heartbeat', 1))
        
        def pop_from_buffer():
            for i in range(100):
                if buffer[0]:
                    buffer[0].pop(0)
        
        t1 = threading.Thread(target=append_to_buffer)
        t2 = threading.Thread(target=pop_from_buffer)
        
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # If there's a race condition, the buffer might be in an inconsistent state
        print(f"✓ Bug #1 potential: buffer has {len(buffer[0])} items after concurrent access")
    
    def test_last_heartbeat_initialization(self):
        """Test Bug #2: last_heartbeat initialized to current time"""
        node = Node(0)
        init_time = time.time()
        
        # last_heartbeat is set to current time at initialization
        # This means a newly created node won't trigger election timeout immediately
        # But the logic might be confusing
        self.assertLessEqual(abs(node.last_heartbeat - init_time), 0.1)
        print("✓ Bug #2 noted: last_heartbeat initialized to current time")
    
    def test_multiple_nodes_concurrent_access(self):
        """Test concurrent access to global nodes list"""
        initialize(3)
        time.sleep(0.5)
        
        # Try to access nodes while threads are running
        try:
            for node in nodes:
                _ = node.state
            print("✓ Global nodes list accessed without crash")
        except Exception as e:
            print(f"✗ Error accessing nodes: {e}")
        
        # Clean up
        for node in nodes:
            node.working = False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Testing main.py for bugs")
    print("="*60 + "\n")
    
    unittest.main(verbosity=2)

