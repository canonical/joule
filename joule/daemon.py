#!/usr/bin/env python3
import logging
from autoscale.applications.microk8s import MicroK8sApplication
from autoscale.providers.aws import AwsProvider


def main():
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO
    )
    logging.info("Listening for events...")
    AwsProvider().loop(MicroK8sApplication())


if __name__ == "__main__":
    main()
