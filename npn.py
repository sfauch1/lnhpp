import urllib.request
import time
import datetime
import json
import csv
import yaml
from pathlib import Path
import MySQLdb

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
        csv_file = write_to_csv(data, arg)
    # write_to_db('npn_fr_2019-02-10 08:37:34.csv')


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

        csvwriter.writerow([npn])

    csv_data.close()
    return csv_file


def write_to_db(csv_file):
    connection = MySQLdb.connect(host=config['mysql']['host'], user=config['mysql']['user'],
                                 passwd=config['mysql']['password'], db=config['mysql']['db'])

    cursor = connection.cursor()

    query = """LOAD DATA LOCAL INFILE '""" + Path(config['files']['output_directory']).joinpath(csv_file).as_posix() + """'
    INTO TABLE product_license
    CHARACTER SET 'latin1'
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES
    (
        licence_date
    )"""

    cursor.execute(query)
    connection.commit()


if __name__ == '__main__':
    main()
