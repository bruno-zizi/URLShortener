import logging
from typing import Annotated
from urllib.parse import urlparse

import typer

from urlshortener.algorithms.factory import ShorteningAlgorithmFactory
from urlshortener.repository.mongo_repository import MongoURLRepository
from urlshortener.settings import ShortenerSettings
from urlshortener.url_shortener import URLShortener


def _validate_options(url_to_minify: str, url_to_expand: str):
    if not url_to_minify and not url_to_expand:
        raise typer.BadParameter("Please specify either --minify or --expand option")

    url_to_minify_parsed = urlparse(url_to_minify)
    if url_to_minify and (
        not url_to_minify_parsed.scheme or not url_to_minify_parsed.netloc
    ):
        raise typer.BadParameter(f"'{url_to_minify}' is not a valid URL")

    url_to_expand_parsed = urlparse(url_to_expand)
    if url_to_expand and (
        not url_to_expand_parsed.scheme or not url_to_expand_parsed.netloc
    ):
        raise typer.BadParameter(f"'{url_to_expand}' is not a valid URL")


def main(
    url_to_minify: Annotated[
        str,
        typer.Option("--minify", "-m", help="URL to shorten"),
    ] = None,
    url_to_expand: Annotated[
        str, typer.Option("--expand", "-e", help="URL to expand")
    ] = None,
    verbose_flag: Annotated[
        bool, typer.Option("-v", "--verbose", help="Print debugging information")
    ] = False,
):
    if verbose_flag:
        logging.basicConfig(level=logging.DEBUG)

    settings = ShortenerSettings()

    _validate_options(url_to_minify, url_to_expand)

    with MongoURLRepository(settings=settings) as repository:
        shortener = URLShortener(
            repository=repository, fixed_domain=settings.fixed_domain
        )
        algorithm = ShorteningAlgorithmFactory().get(
            algorithm_type=settings.shortening_algorithm
        )

        if url_to_minify:
            short_url = shortener.minify(url=url_to_minify, algorithm=algorithm)
            typer.echo(f"{url_to_minify} -> {short_url}")

        if url_to_expand:
            original_url = shortener.expand(short_url=url_to_expand, algorithm=algorithm)
            typer.echo(f"{url_to_expand} -> {original_url}")


def run():
    typer.run(main)


if __name__ == "__main__":
    run()
