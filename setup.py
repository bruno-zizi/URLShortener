from setuptools import setup

setup(
    name="urlshortener",
    version="1.0.0",
    description="Url shortener tool",
    author="Bruno Zizi",
    author_email="bruno.zizi@email.com",
    packages=["urlshortener", "urlshortener.algorithms", "urlshortener.repository"],
    python_requires=">=3.10.1,<3.12",
    install_requires=[
        "pymongo == 4.6.1",
        "pytest == 8.0.0",
        "black == 24.1.1",
        "typer == 0.9.0",
        "pydantic-settings == 2.1.0",
        "setuptools == 69.0.3",
        "freezegun==1.4.0",
    ],
    entry_points={"console_scripts": ["urlshortener = urlshortener.cli:run"]},
)
