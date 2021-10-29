import argparse
import glob
import json
import os
import shutil
from urllib.parse import urlencode

import requests_cache

# Setup cached request session
if not os.path.exists('request_cache.sqlite'):
    requests_cache.install_cache('request_cache')
session = requests_cache.CachedSession('request_cache')

base_url = "https://web.duelistsunite.org/omega-api-decks/%s?%s"


def convert_deck(list: str, to: str = None, identifier: str = None, writedata: bool = False):
    """Convert a given deck list to a given format.

    Args:
        list (dict | str): Deck list in any of the following formats:
            ydk: YDK format as path to ydk file
            ydke: YDKE format string
            omega: Omega code
            names: List of card names
            json: JSON object
        to (str): Format to convert to
        identifier (str): Hint to format to convert from
        writedata (bool): When used as a module, write data to files instead of returning data
    """
    if '.ydk' in list:
        f = open(list, 'r')
        list = f.read()
        f.close()
    elif '.json' in list:
        f = open(list, 'r')
        list = json.load(f)
        f.close()

    querydict = {'list': list}

    if to:
        querydict['to'] = to

    if identifier:
        querydict['identifier'] = identifier

    string = urlencode(querydict)
    url = base_url % ('convert', string)
    response = session.get(url)

    if not response.ok:
        print(f"ERROR {response.status_code}: {url}")
        return None

    responsedata: dict = response.json()
    deckdata: dict = responsedata['data']['formats']
    
    if not writedata:
        if 'json' in deckdata:
            deckdata['json'] = json.loads(deckdata['json'])
        return deckdata

    if to == 'ydk' or not to:
        ydkdata = deckdata['ydk']
        with open('output/output.ydk', 'w') as f:
            f.write(ydkdata)
        print("YDK: Written to output.ydk\n")

    if to == 'names' or not to:
        decklist = deckdata['names']
        with open('output/output.txt', 'w') as f:
            f.write(decklist)
        print("Names: Written to output.txt\n")

    if to == 'json' or not to:
        jsondata = json.loads(deckdata['json'])
        with open('output/output.json', 'w') as f:
            json.dump(jsondata, f, indent=4)
        print("JSON: Written to output.json\n")

    if to == 'ydke' or not to:
        print(f"YDKE: {deckdata['ydke']}\n")

    if to == 'omega' or not to:
        print(f"Omega code: {deckdata['omega']}\n")


def imageify_deck(list: str):
    """Generates image from deck

    Args:
        list (dict | str): Deck list in any of the following formats:
            ydk: YDK format as path to ydk file
            ydke: YDKE format string
            omega: Omega code
            names: List of card names
            json: JSON object
    """
    querydict = {'list': list}
    string = urlencode(querydict)
    url = base_url % ('imageify', string)
    response = session.get(url, stream=True)

    if not response.ok:
        print(f"ERROR {response.status_code}: {url}")
        return None

    with open('output/output.png', 'wb') as f:
        shutil.copyfileobj(response.raw, f)
    print("PNG: Written to output.png\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--list", help="deck list in formats [YDKE, YDK, JSON, omega code, names]", required=True)
    parser.add_argument("-t", "--to", help="format to convert to")
    parser.add_argument("-i", "--identifier", help="input identifier")
    parser.add_argument("-m", "--imageify",
                        action='store_true', help="generate image from deck")
    parser.add_argument("-c", "--clean", action='store_true',
                        help="clean directory")
    args = parser.parse_args()

    if not os.path.exists('output'):
        os.makedirs('output')

    if not args.list:
        parser.print_help()
        exit()

    if args.clean:
        for filetype in ["output/*.txt", "output/*.json", "output/*.ydk", "output/*.png"]:
            for file in glob.glob(filetype):
                os.remove(file)
        os.removedirs('output')
    elif args.imageify:
        imageify_deck(args.list)
    else:
        convert_deck(args.list, args.to, args.identifier, writedata=True)
