import os

import click
import logger_provider
import uvicorn
from core.config import config


@click.command()
@click.option(
    "--env",
    type=click.Choice(["local", "dev", "prod"], case_sensitive=False),
    default="local",
)
@click.option(
    "--debug",
    type=click.BOOL,
    is_flag=True,
    default=False,
)
def main(env: str, debug: bool):
    """Main function, start coding here"""
    logger_provider.set_logger_level(env)

    log = logger_provider.get_logger(__name__)
    log.debug("This is a Debug log")
    log.info("This is a information log")
    log.error("This is a Error log")
    log.critical("This is a Critical log")

    uvicorn.run(
        app="app.server:app",
        host=config.APP_HOST,
        port=config.APP_PORT,
        reload=True if config.ENV != "production" else False,
        workers=1,
    )


if __name__ == "__main__":
    main()
