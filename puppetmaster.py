#!/usr/bin/env python3
import logging
from providers.aws import AwsProvider


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    logging.info('Listening for events...')
    AwsProvider().loop()
