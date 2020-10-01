from setuptools import setup


setup(
    name='microk8s-puppetmaster',
    version='0.1.0',
    url='https://github.com/joedborg/microk8s-puppetmaster',
    license='Apache License 2.0',
    author='Joe Borg',
    author_email='joseph.borg@canonical.com',
    description='Drive MicroK8s inside scale groups',
    packages=[
        'bin',
        'providers'
    ],
    install_requires=[
        'boto3',
        'ec2-metadata'
    ],
    entry_points={
        'console_scripts': [
            'puppetmaster=bin.puppetmaster:main',
        ],
    }
)
