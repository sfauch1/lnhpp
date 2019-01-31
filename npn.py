import urllib.request
import time
import datetime
import json
import csv
import os

url = 'https://health-products.canada.ca/api/natural-licences/productlicence/?lang=%(language)s&type=json'
json_file = os.path.join('files', 'npn_%(language)s_%(timestamp)s.json')
csv_file = os.path.join('files', 'npn_%(language)s_%(timestamp)s.csv')
ts = time.time()
st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')


def main():
    print('Starting process...')
    execute('fr', 'en')


def execute(*args):
    for arg in args:
        filename = download_file(arg)
        data = parse_json_file(filename)
        write_to_csv(data, arg)


def download_file(language):
    print('Downloading %(language)s file' % {'language': language})
    filename = json_file % {'language': language, 'timestamp': st}
    urllib.request.urlretrieve(url % {'language': language}, filename)
    return filename


def parse_json_file(filename):
    print('Parsing JSON file -> %(file)s' % {'file': filename})
    with open(filename) as json_data:
        data = json.load(json_data)
        return data


def write_to_csv(data, language):
    filename = csv_file % {'language': language, 'timestamp': st}
    print('Writing JSON data to -> %(file)s' % {'file': filename})
    csv_data = open(filename, 'w')

    csvwriter = csv.writer(csv_data)

    count = 0

    for npn in data:

        if count == 0:
            header = npn.keys()

            csvwriter.writerow(header)

            count += 1

        csvwriter.writerow(npn.values())

    csv_data.close()
    

if __name__ == '__main__':
    main()
