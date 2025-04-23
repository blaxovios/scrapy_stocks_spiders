import unittest
import tempfile
import os
from stocks_spider.exporters import PolarsParquetItemExporter


class TestPolarsParquetItemExporter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init(self):
        file_path = os.path.join(self.temp_dir.name, 'test.parquet')
        exporter = PolarsParquetItemExporter(file_path)
        self.assertEqual(exporter._file, file_path)
        self.assertEqual(exporter._rows, [])

    def test_export_item(self):
        file_path = os.path.join(self.temp_dir.name, 'test.parquet')
        exporter = PolarsParquetItemExporter(file_path)
        item = {'key': 'value'}
        exporter.export_item(item)
        self.assertEqual(exporter._rows, [item])

    def test_finish_exporting(self):
        file_path = os.path.join(self.temp_dir.name, 'test.parquet')
        exporter = PolarsParquetItemExporter(file_path)
        item = {'key': 'value'}
        exporter.export_item(item)
        exporter.finish_exporting()
        self.assertTrue(os.path.exists(file_path))

    def test_finish_exporting_empty(self):
        file_path = os.path.join(self.temp_dir.name, 'test.parquet')
        exporter = PolarsParquetItemExporter(file_path)
        exporter.finish_exporting()
        self.assertFalse(os.path.exists(file_path))

    def test_export_item_multiple(self):
        file_path = os.path.join(self.temp_dir.name, 'test.parquet')
        exporter = PolarsParquetItemExporter(file_path)
        item1 = {'key': 'value1'}
        item2 = {'key': 'value2'}
        exporter.export_item(item1)
        exporter.export_item(item2)
        self.assertEqual(exporter._rows, [item1, item2])


if __name__ == '__main__':
    unittest.main()