"""
Basic File Sync v0.1.0

Description:
Cross-platform File Sync program that copies source file/directory (from file) to the destination file/directory (to file) when changes are detected.
This is a hugely basic, quickly written version that needs some serious improving.  It's currently limited to working
only with single files or directories.

In future I hope to support:
- Multiple to & from files 
- menu for saving and loading configuration and an application
- maintained, user accessible log.

Author:
James Barnden

License:
MIT

"""

import unittest

class TestValidation(unittest.TestCase):
    """
    Tests for the application paths validation method
    """
    pass

class TestOperations(unittest.TestCase):
    """
    Tests all basic application methods around
    configuration and widget creation.
    """
    def test_save_config(self):
        pass
    
    def test_load_config(self):
        pass
    
    def test_store_path(self):
        pass

    def test_create_widgets(self):
        pass

class TestFileHandler(unittest.Testcase):
    """
    Tests file handler functionality but not the lister its self
    (not testing library code)
    """
    def test_update_dir(self):
        pass
    
    def test_update_file(self):
        pass

if __name__ == '__main__':
    unittest.main()