"""
Boris
-------------

A small library for accessing and searching current Barclays Cycle Hire 
availability in London, UK.
"""
from setuptools import setup


setup(
    name='Boris',
    version='0.1',
    url='http://github.com/e-dard/boris',
    license='WTFPL',
    author='Edward Robinson',
    author_email='me@eddrobinson.net',
    description="Easily access and search Barclays bike availability in London, UK.",
    long_description=__doc__,
    py_modules=['boris.py, client.py'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'lxml>=3.0.1', 'Postcodes>=0.1'
    ],
    tests_require=['nose', 'mock'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
