import datetime
import json
from decimal import Decimal, ROUND_DOWN
from http.server import HTTPServer, BaseHTTPRequestHandler
from sys import argv
from urllib import request
from xml.dom import minidom


CURRENT_URL = 'http://www.cbr.ru/scripts/XML_daily.asp'


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_POST(self):
        try:
            begin_currency, end_currency, begin_sum = path_to_param(self.path)
            self._set_headers()
            rate = get_rate_in_rubles(begin_currency)
            self.wfile.write(json.dumps({
                'begin_currency': begin_currency,
                'end_currency': end_currency,
                'begin_sum': begin_sum,
                'end_sum': get_end_sum(begin_sum, rate)
            }).encode('utf-8'))
            with open('logs.txt', 'a') as file:
                file.write(
                    f'{datetime.datetime.now()}:   '
                    f'begin_currency: {begin_currency}, '
                    f'end_currency: {end_currency},'
                    f'begin_sum: {begin_sum},'
                    f'end_sum: {get_end_sum(begin_sum, rate)}\n'
                )
        except:
            self.send_response(400)
            self.end_headers()


def path_to_param(path):
    def partition(param1, param2, param3):
        return param1.partition('=')[2], param2.partition('=')[2], param3.partition('=')[2]

    path = path.split("&")
    p1, p2, p3 = path[0], path[1], path[2]
    if 'begin_currency' in p1:
        if 'end_currency' in p2:
            return partition(p1, p2, p3)
        else:
            return partition(p1, p3, p2)
    elif 'end_currency' in p1:
        if 'begin_currency' in p2:
            return partition(p2, p1, p3)
        else:
            return partition(p3, p1, p2)
    else:
        if 'begin_currency' in p2:
            return partition(p2, p3, p1)
        else:
            return partition(p3, p2, p1)


def get_end_sum(begin_sum, rate):
    return str(
        Decimal(Decimal(begin_sum.replace(',', '.')) * Decimal(rate.replace(',', '.'))).quantize(
            Decimal('.01'), rounding=ROUND_DOWN
        )
    )


def create_file_name(url):
    UrlSplit = url.split("/")[-1]
    ExtSplit = UrlSplit.split(".")[1]
    return UrlSplit.replace(ExtSplit, "xml")


def load_rate(url=CURRENT_URL):
    webFile = request.urlopen(url)
    data = webFile.read()
    FileName = create_file_name(url)
    with open(FileName, "wb") as localFile:
        localFile.write(data)
    webFile.close()
    doc = minidom.parse(FileName)
    currency = doc.getElementsByTagName("Valute")
    return currency


def get_rate_in_rubles(buy_currency, currency=load_rate()):
    for rate in currency:
        if rate.getElementsByTagName("CharCode")[0].firstChild.nodeValue == buy_currency:
            return rate.getElementsByTagName("Value")[0].firstChild.nodeValue
    return None


def run(port=8000):
    httpd = HTTPServer(('', port), Server)
    print(f'server is up on port: {port}')
    httpd.serve_forever()


if __name__ == "__main__":
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
