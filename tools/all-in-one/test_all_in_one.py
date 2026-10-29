import importlib.util
import pathlib
import tempfile
import unittest
from unittest.mock import patch


MODULE_PATH = pathlib.Path(__file__).with_name('MacroWave_AllInOne.py')
SPEC = importlib.util.spec_from_file_location('macrowave_all_in_one', MODULE_PATH)
app = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(app)


class AllInOneTests(unittest.TestCase):
    def test_contains_all_previous_python_tools(self):
        self.assertEqual(set(app.WORKERS), {'macrowave', 'per_auto', 'twstocktracker', 'bengo'})

    def test_normalizes_stock_ids_and_wait_range(self):
        config = app.normalize_config({
            'stock_ids': '2330\n2330,2317\n../bad',
            'minimum_wait_seconds': 20,
            'maximum_wait_seconds': 5,
            'selected_workers': ['macrowave'],
        })
        self.assertEqual(config['stock_ids'], ['2330', '2317'])
        self.assertEqual(config['maximum_wait_seconds'], 20)

    def test_saves_shared_compatibility_files(self):
        with tempfile.TemporaryDirectory() as directory:
            app.save_config({'fred_api_key': 'configured', 'stock_ids': ['2330']}, directory)
            base = pathlib.Path(directory)
            self.assertTrue((base / app.CONFIG_NAME).exists())
            self.assertIn('configured', (base / 'macrowave_config.json').read_text(encoding='utf-8'))
            self.assertEqual((base / 'stock_id_settings.csv').read_text(encoding='utf-8'), '2330\n')

    def test_source_worker_command_uses_same_entrypoint(self):
        with patch.object(app.sys, 'frozen', False, create=True):
            command = app.worker_command('bengo', pathlib.Path('config.json'), pathlib.Path('worker.log'))
        self.assertIn('--worker', command)
        self.assertIn('bengo', command)
        self.assertTrue(command[1].endswith('MacroWave_AllInOne.py'))


if __name__ == '__main__':
    unittest.main()
