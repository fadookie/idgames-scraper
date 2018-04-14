#!/usr/bin/env python
import json
import urllib
# import time
import re
import os
import logging
from contextlib import contextmanager

# Set this to your nearest FTP mirror:
ftp_server = 'http://ftp.mancubus.net/pub/idgames/'
# ftp_server = 'http://ftp.mancubus.net/pub/idgames/historic/doom0_2.zip'

# ID to start downloading from
start_id = 9

# ID to stop downloading at
end_id = 40

# Directories in /idgames to ignore - these are intepreted as regex
dir_blacklist_src = [
    'deathmatch/.*',
    'docs/.*',
    'graphics/.*',
    'historic/.*',
    'idstuff/.*',
    'music/.*',
    'prefabs/.*',
    'roguestuff/.*',
    'skins/.*',
    'sounds/.*',
    'source/.*',
    'themes/.*',
    'utils/.*',
]
dir_blacklist = []

for x in dir_blacklist_src:
    dir_blacklist.append(re.compile(x))


def is_dir_blacklisted(dir):
    for matcher in dir_blacklist:
        if matcher.match(dir) is not None:
            return True
    return False


def get_api_request(query):
    api_server = 'https://legacy.doomworld.com/idgames/api/api.php?'
    query['out'] = 'json'
    query_string = urllib.urlencode(query)
    request_url = api_server + query_string
    return request_url


# def get_file_page(start_id):
#     return get_api_request({
#         'action': 'latestfiles',
#         'limit': 100,
#         'startid': start_id,
#     })


def get_file(file_id):
    return get_api_request({
        'action': 'get',
        'id': file_id,
    })


@contextmanager
def working_directory(path):
    current_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(current_dir)

downloads_folder = 'scraper_downloads'
try:
    os.mkdir(downloads_folder)
except Exception:
    pass
os.chdir(downloads_folder)

for entry_id in range(start_id, end_id):
    request_url = get_file(entry_id)
    # print('Sending request to "{}"'.format(request_url))
    response = urllib.urlopen(request_url)
    data = json.load(response)
    entry = data['content']

    if is_dir_blacklisted(entry['dir']):
        print('skipping entry id {} ({}) in blacklisted dir "{}"'
              .format(entry_id, entry['filename'], entry['dir']))
        continue

    download_url = ftp_server + entry['dir'] + entry['filename']
    # print('got download_url:{} for file:\n{}'.format(download_url, entry))

    try:
        os.makedirs(str(entry_id))
    except Exception as e:
        logging.error(e)

    with working_directory(str(entry_id)):
        if os.path.isfile(entry['filename']):
            print 'file "{}" already downloaded, skipping.'.format(
                entry['filename'])
            continue
        print('downloading {}...'.format(download_url))
        urllib.urlretrieve(download_url, entry['filename'])

    # time.sleep(1)  # Wait for a second to be nice to their API server
