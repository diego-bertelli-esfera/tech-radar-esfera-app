import base64, pathlib, sys, unittest
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from validate_radar import validate_and_normalize

DATA_FILE = pathlib.Path(__file__).resolve().parents[1] / 'files/radar.csv'
class ValidatorTests(unittest.TestCase):
    def test_real_csv(self):
        result = validate_and_normalize(DATA_FILE.read_bytes())
        self.assertIn(b'Bedrock (IA Corp)', result)
        self.assertIn(b'Snowflake', result)
    def test_reject_bad_headers(self):
        data = DATA_FILE.read_bytes().replace(b'name,ring,quadrant,isNew,description', b'wrong,ring,quadrant,isNew,description', 1)
        with self.assertRaises(ValueError): validate_and_normalize(data)
    def test_reject_incomplete(self):
        data = DATA_FILE.read_bytes().splitlines()
        with self.assertRaises(ValueError): validate_and_normalize(b'\n'.join(data[:2]))
    def test_reject_duplicate(self):
        data = DATA_FILE.read_bytes()
        with self.assertRaises(ValueError): validate_and_normalize(data + data.splitlines()[1] + b'\n')
if __name__ == '__main__': unittest.main()
