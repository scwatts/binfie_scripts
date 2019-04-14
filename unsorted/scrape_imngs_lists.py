#!/usr/bin/env python3
'''This script was used to scrape the IMNGS database early 2018. Couple of useful things:
    * HTTP session - login and token management
    * simple example of logging
    * getpass - securely prompt password at command line
    * get and process JSON responses from API
'''
import argparse
import concurrent.futures
import getpass
import json
import logging
import pathlib
import sys


import requests


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True, type=str,
            help='Username')
    parser.add_argument('--threads', required=False, default=4, type=int,
            help='Threads to use')

    return parser.parse_args()


def main():
    # Get command line arguments and create session
    args = get_arguments()
    initalising_logging()
    session = login(args.username, getpass.getpass())

    # Get data
    page_count = get_page_count(session)
    logging.debug('got %s pages', page_count)
    task_args = ((session, n) for n in range(1, page_count+1))
    task_func = download_page
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        results = [r for r in executor.map(lambda x: task_func(*x), task_args)]


def initalising_logging():
    log_format = logging.Formatter(fmt='%(asctime)s %(module)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    log_streamhandler = logging.StreamHandler()
    log_streamhandler.setFormatter(log_format)
    logger = logging.getLogger()
    logger.addHandler(log_streamhandler)
    logger.setLevel(logging.DEBUG)


def login(username, password):
    logging.debug('creating session')
    logging.debug('requesting imngs.org')
    # Create session and get CSRF token
    session = requests.Session()
    try:
        r = session.get('https://www.imngs.org/')
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    # Login
    logging.debug('logging in')
    data = {'csrfmiddlewaretoken': session.cookies['csrftoken'],
            'username': username,
            'password': password}
    try:
        r = session.post('https://www.imngs.org/users/login/', data=data)
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    # This is required for list paging requests. idk lol
    logging.debug('requesting lists page')
    try:
        r = session.get('https://www.imngs.org/16S_rRNA/search/')
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    return session


def get_page_count(session):
    try:
        r = get_page(session, '1')
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
    return int(json.loads(r.text)['paging_params']['num_pages'])


def download_page(session, page_number):
    logging.debug('requestin paging %s' % page_number)
    output_fp = pathlib.Path('page_%s.json' % page_number)
    try:
        r = get_page(session, page_number)
        r.raise_for_status()
    except requests.exceptions.HTTPError as error:
        logging.error('Got %s for %s', error, page_number)
    logging.debug('got %s got page %s', r, page_number)
    logging.debug('writing page %s', page_number)
    with output_fp.open('w') as fh:
        fh.write(r.text)


def get_page(session, page_number):
    data = {'page': page_number}
    session.headers.update({'X-CSRFToken': session.cookies['csrftoken']})
    return session.post('https://www.imngs.org/16S_rRNA/paging/', data=data)


if __name__ == '__main__':
    main()
