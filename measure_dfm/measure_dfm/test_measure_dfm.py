import unittest
import measure_dfm

class test_measure_dfm(unittest.TestCase):
	def test_dump_to_file(self):
		measure_dfm.dump_to_file("C:\\Users\\Uri\\Desktop\\test.txt", "test")
		self.assertEqual(True, True)

	def test_pretty_xml(self):
		expected = u'<?xml version="1.0" ?>\n<parent>\n\t<child>x</child>\n</parent>\n'
		actual = measure_dfm.pretty_xml("<parent><child>x</child></parent>")
		self.assertEqual(actual, expected)

	def test_pretty_json(self):
		expected = '"{ \'parent\' : { \'child\' : \'x\' } }"'
		actual = measure_dfm.pretty_json("{ 'parent' : { 'child' : 'x' } }")
		print actual
		self.assertEqual(actual, expected)

if __name__ == '__main__':
	unittest.main()
