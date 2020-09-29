#!/usr/bin/env python3

from providers.aws import AwsProvider


if __name__ == '__main__':
    AwsProvider().loop()
