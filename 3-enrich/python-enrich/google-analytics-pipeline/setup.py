import setuptools

REQUIRED_PACKAGES = [
    "bunch==1.0.1",
    "cerberus==1.2",
    "ua-parser==0.8.0",
    "user-agents==1.1.0",
    "referer_parser==0.4.1",
]

PACKAGE_NAME = 'google_analytics_pipeline'
PACKAGE_VERSION = '1.0.0'

setuptools.setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description='Google Analytics real-time pipeline',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
    package_data={
        PACKAGE_NAME: [],
    },
)
