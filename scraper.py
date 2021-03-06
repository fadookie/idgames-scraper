#!/usr/bin/env python
import json
import urllib
import re
import os
import time
import logging
import webbrowser
from contextlib import contextmanager

# Set this to your nearest FTP mirror:
ftp_server = 'http://ftp.mancubus.net/pub/idgames/'

# ID to start downloading from
start_id = 9

# ID to stop downloading at
end_id = 25

# Open idgames page for each downloaded file in a browser tab?
open_browser = True

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

    dl_folder_name = '{0:05d}'.format(entry_id)
    try:
        os.makedirs(dl_folder_name)
    except Exception as e:
        logging.error(e)

    with working_directory(dl_folder_name):
        if os.path.isfile(entry['filename']):
            print 'file "{}" already downloaded, skipping.'.format(
                entry['filename'])
            time.sleep(1)  # Wait for a second to be nice to their API server
            continue

        with open("entry.json", "w") as outfile:
            json.dump(data, outfile, indent=4)
            print('dumped entry json to file.')

        if open_browser:
            print('trying to open browser for url:'.format(entry['url']))
            webbrowser.open_new_tab(entry['url'])

        print('downloading {}...'.format(download_url))
        urllib.urlretrieve(download_url, entry['filename'])
