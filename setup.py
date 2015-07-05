from setuptools import setup


version = '0.1'

setup(
    name='swift_persistent_identifier',
    version='0.1',
    description='implements a paste filter to get, add and respond a pid for a'
                'incoming digital object',
    long_description='''
         This provides a python middleware distributed via egg which can be
         added to the OpenStack Swift pipeline to add (Epic) PID support for
         incoming objects
      ''',
    classifiers=[
        'Programming Language :: Python'
        ],
    keywords='',
    author='BeneDicere',
    author_email='b.von.st.vieth@fz-juelich.de',
    include_package_data=True,
    packages=['swift_persistent_identifier'],
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    entry_points={
        'paste.filter_factory': ['persistent_identifier_middleware = '
                                 'swift_persistent_identifier.'
                                 'persistent_identifier_middleware:'
                                 'filter_factory'],
    }
)
