#!/usr/bin/env python3
import click
import logging

from importlib import import_module


@click.command()
@click.option("--application", required=True, help="Application module name")
@click.option("--provider", required=True, help="Provider module name")
@click.option("--debug", is_flag=True)
def main(application, provider, debug):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )
    logging.info("Listening for events...")

    Provider = getattr(
        import_module("joule.providers.{}".format(provider)),
        "{}Provider".format(provider.capitalize()),
    )

    Application = getattr(
        import_module("joule.applications.{}".format(application)),
        "{}Application".format(application.capitalize()),
    )

    logging.debug("Starting with provider {}".format(Provider))
    logging.debug("Starting with application {}".format(Application))

    Provider().loop(Application())


if __name__ == "__main__":
    main()
