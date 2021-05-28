#!/usr/bin/env python3
import click
import logging

from importlib import import_module


@click.command()
@click.option(
    "--provider", required=True, help="Provider module name, may only be one."
)
@click.option(
    "--applications", required=True, help="Application module names, comma seperated."
)
@click.option("--debug", is_flag=True)
def main(provider, applications, debug):
    logging.basicConfig(
        format="%(asctime)s %(levelname)s:%(message)s",
        level=logging.DEBUG if debug else logging.INFO,
    )
    logging.info("Listening for events...")

    Provider = getattr(
        import_module("joule.providers.{}".format(provider)),
        "{}Provider".format(provider.capitalize()),
    )

    logging.debug("Starting with provider {}".format(Provider))

    Applications = []

    for application in applications.split(","):
        Application = getattr(
            import_module("joule.applications.{}".format(application)),
            "{}Application".format(application.capitalize()),
        )
        Applications.append(Application())
        logging.debug("Starting with application {}".format(Application))

    Provider(*Applications).loop()


if __name__ == "__main__":
    main()
