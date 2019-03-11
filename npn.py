import urllib.request
import time
import datetime
import json
import csv
import yaml
from os import remove
from pathlib import Path

config = None


def main():
    get_config()
    print('Start : %(timestamp)s\n' % {'timestamp' : get_timestamp()})
    execute('en', 'fr')
    print('Finish : %(timestamp)s' % {'timestamp' : get_timestamp()})


def get_config():
    """Read configuration from YAML file"""

    global config
    config = yaml.safe_load(open('config.yml'))


def execute(*args):
    """Iterate over each categories and execute functions for specified language"""

    i = 0
    while i < len(config['categories']):
        category = config['categories'][i]
        for arg in args:
            filename = download_file(arg, category)
            data = parse_json_file(filename)
            write_to_csv(data, arg, category)
        i += 1


def download_file(language, category):
    """Download JSON file for specified language and category"""

    json_file = Path(config['files']['output_directory']).joinpath(
        '%(category)s_%(language)s_%(timestamp)s.%(file_extension)s' % {'category': category,
                                                                        'language': language,
                                                                        'timestamp': get_timestamp(),
                                                                        'file_extension': 'json'})
    print('Downloading %(category)s (%(language)s) data to %(output)s' % {'category': category,
                                                                          'language': language,
                                                                          'output': json_file})

    urllib.request.urlretrieve(config['files'][category]['url'] % {'language': language}, json_file.as_posix())

    return json_file


def parse_json_file(filename):
    """Parse JSON file and return data to caller"""

    print('Parsing JSON file :  %(file)s' % {'file': filename})

    with Path.open(filename) as json_data:
        data = json.load(json_data)
        delete_file(Path(filename).as_posix())
        return data


def get_timestamp():
    """Get current time as string"""

    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

    return st


def write_to_csv(data, language, category):
    """Write parsed data from JSON file to CSV for specified language"""

    csv_file = Path(config['files']['output_directory']).joinpath(
        '%(category)s_%(language)s_%(timestamp)s.%(file_extension)s' % {'category': category,
                                                                        'language': language,
                                                                        'timestamp': get_timestamp(),
                                                                        'file_extension': 'csv'})

    print(
        'Writing JSON data for %(category)s (%(language)s) to : %(file)s' % {'category': category,
                                                                             'language': language,
                                                                             'file': csv_file})

    csv_data = Path.open(csv_file, 'w')

    csvwriter = csv.writer(csv_data, delimiter='\t')

    count = 0

    for npn in data:

        if count == 0:

            header = npn.keys()

            csvwriter.writerow(header)

            count += 1

        csvwriter.writerow(npn.values())

    csv_data.close()


def delete_file(filename):
    """Delete file from disk"""

    print('Deleting file :  %(file)s' % {'file': filename})
    remove(filename)


if __name__ == '__main__':
    main()
