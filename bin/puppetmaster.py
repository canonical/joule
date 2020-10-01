#!/usr/bin/env python3
import logging
from providers.aws import AwsProvider


def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    logging.info('Listening for events...')
    AwsProvider().loop()


if __name__ == '__main__':
    main()