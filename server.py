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
            path = self.path.split("&")
            begin_currency, end_currency, begin_sum = path[0].partition('=')[2], path[1].partition('=')[2], \
                                                      path[2].partition('=')[2]
            self._set_headers()
            rate = get_rate_in_rubles(begin_currency)
            self.wfile.write(json.dumps({
                'begin_currency': begin_currency,
                'end_currency': end_currency,
                'begin_sum': begin_sum,
                'end_sum': get_end_sum(begin_sum, rate)
            }).encode('utf-8'))
        except:
            self.send_response(400)
            self.end_headers()


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
    print(f'Сервер поднят на порту: {port}')
    httpd.serve_forever()


if __name__ == "__main__":
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
