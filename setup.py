from setuptools import setup, find_packages


if __name__ == "__main__":
    setup(
        name='MyLogParser',
        version='0.1',
        description="Simple log parser app - Python exercise",
        packages=find_packages(),
        install_requires=[
            'file-read-backwards',
            'pytest',
        ],
    )
