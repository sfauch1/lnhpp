import urllib.request
import time
import datetime
import json
import csv
import yaml
from pathlib import Path

config = None


def main():
    get_config()
    execute('fr', 'en')


def get_config():
    """Read configuration from YAML file"""

    global config
    config = yaml.safe_load(open('config.yml'))


def execute(*args):
    """Iterate over each languages and execute functions"""

    for arg in args:
        filename = download_file(arg)
        data = parse_json_file(filename)
        write_to_csv(data, arg)


def download_file(language):
    """Download JSON file for specified language"""

    json_file = Path(config['files']['output_directory']).joinpath(
        config['files']['json_file'] % {'language': language, 'timestamp': get_timestamp()})
    print('Downloading %(language)s data to %(output)s' % {'language': language, 'output': json_file})
    urllib.request.urlretrieve(config['url'] % {'language': language}, json_file.as_posix())
    return json_file


def parse_json_file(filename):
    """Parse JSON file and return data to caller"""

    print('Parsing JSON file :  %(file)s' % {'file': filename})
    with Path.open(filename) as json_data:
        data = json.load(json_data)
        return data


def get_timestamp():
    """Get current time as string"""

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st


def write_to_csv(data, language):
    """Write parsed data from JSON file to CSV for specified language"""

    csv_file = Path(config['files']['output_directory']).joinpath(
        config['files']['csv_file'] % {'language': language, 'timestamp': get_timestamp()})
    print('Writing JSON data to : %(file)s' % {'file': csv_file})
    csv_data = Path.open(csv_file, 'w')

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
