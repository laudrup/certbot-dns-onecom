from setuptools import setup
from setuptools import find_packages


version = '0.1.1'

install_requires = [
    'acme>=0.21.1',
    'certbot>=0.21.1',
    'dns-lexicon>=2.1.22',
    'setuptools',
    'zope.interface',
    'beautifulsoup4',
]

setup(
    name='certbot-dns-onecom',
    version=version,
    description="One.com DNS Authenticator plugin for Certbot",
    url='https://github.com/laudrup/certbot-dns-onecom',
    author="Kasper Laudrup",
    author_email="laudrup@stacktrace.dk",
    license='Apache License 2.0',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],

    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    extras_require={},
    entry_points={
        'certbot.plugins': [
            'dns-onecom = certbot_dns_onecom.dns_onecom:Authenticator',
        ],
    },
)
