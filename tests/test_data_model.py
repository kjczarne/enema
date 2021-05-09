import unittest
from enema.data_model import get_joined_nodes_and_subsystems, with_auth


class TestDataModel(unittest.TestCase):

    def test_get_joined_nodes_and_subsystems(self):
        df = get_joined_nodes_and_subsystems()
        print(df.to_dict('records'))
    
    def test_api_auth(self):
        resp = {}


if __name__ == "__main__":
    unittest.main()
