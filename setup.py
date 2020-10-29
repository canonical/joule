from setuptools import setup


setup(
    name="autoscale",
    version="0.1.0",
    url="https://github.com/joedborg/microk8s-autoscale",
    license="Apache License 2.0",
    author="Joe Borg",
    author_email="joseph.borg@canonical.com",
    description="Drive applications inside auto scale groups",
    packages=[
        "autoscale",
        "autoscale.applications",
        "autoscale.events",
        "autoscale.providers",
    ],
    install_requires=["boto3", "ec2-metadata"],
    entry_points={
        "console_scripts": [
            "autoscale=autoscale.daemon:main",
        ],
    },
)
