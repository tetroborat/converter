import threading
import time
import unittest
from decimal import Decimal
from http.server import HTTPServer
from urllib import request
from xml.dom import minidom

import requests as requests

import server


test_currency = minidom.parse('TEST_CURRENCY.xml').getElementsByTagName('Valute')


class Tests(unittest.TestCase):

    def test_get_currency(self):
        currency = server.get_rate_in_rubles('USD', test_currency)
        self.assertIsNotNone(currency)

    def test_get_create_file_name(self):
        true_result = 'TEST.xml'
        current_result = server.create_file_name('http://www.asdagvax.ru/asfafsaf/asdasd/TEST.asp')
        self.assertEqual(true_result, current_result)

    def test_error_currency(self):
        currency = server.get_rate_in_rubles('test_currency', test_currency)
        self.assertIsNone(currency)

    def test_get_end_sum(self):
        true_result = '297.64'
        current_result = server.get_end_sum('12.34', '24.12')
        self.assertEqual(true_result, current_result)

    def test_get_rate_in_rubles(self):
        true_result = '74,1503'
        current_result = server.get_rate_in_rubles('USD', test_currency)
        self.assertEqual(true_result, current_result)

    def test_load_rate(self):
        url = server.CURRENT_URL
        webFile = request.urlopen(url)
        data = webFile.read()
        FileName = server.create_file_name(url)
        with open(FileName, "wb") as localFile:
            localFile.write(data)
        webFile.close()
        doc = minidom.parse(FileName)
        true_currency = doc.getElementsByTagName("Valute")
        current_currency = server.load_rate(url)
        total_true, total_current = 0, 0
        for rate in true_currency:
            total_true += Decimal(rate.getElementsByTagName("Value")[0].firstChild.nodeValue.replace(',', '.'))
        for rate in current_currency:
            total_current += Decimal(rate.getElementsByTagName("Value")[0].firstChild.nodeValue.replace(',', '.'))
        self.assertEqual(total_current, total_true)

    def test_server(self):
        test_server = HTTPServer(('', 8000), server.Server)
        server_thread = threading.Thread(target=test_server.serve_forever)
        server_thread.start()
        time.sleep(1)
        status_code = requests.post("http://localhost:8000?begin_currency=USD&end_currency=RUB&sum=100.15/").status_code
        self.assertEqual(status_code, 200)


if __name__ == '__main__':
    unittest.main()