import os

import click
import logger_provider


@click.command()
@click.option(
    "--env",
    type=click.Choice(["dev", "prd"], case_sensitive=False),
    default="dev",
)
def main(env: str):
    """Main function, start coding here"""
    logger_provider.set_logger_level(env)

    log = logger_provider.get_logger(__name__)
    log.debug("This is a Debug log")
    log.info("This is a information log")
    log.error("This is a Error log")
    log.critical("This is a Critical log")


if __name__ == "__main__":
    main()
