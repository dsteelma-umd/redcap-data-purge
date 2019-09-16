from setuptools import setup

setup(
    name = 'RedcapDataPurge',
    version = '0.1.0',
    packages = ['redcapdatapurge'],
    entry_points = {
        'console_scripts': [
            'redcapdatapurge = redcapdatapurge.__main__:main'
        ]
    },
    install_requires=[
        'dataset',
        'mysqlclient'
    ]
)
