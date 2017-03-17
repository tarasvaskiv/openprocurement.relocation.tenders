from setuptools import setup, find_packages

version = '1.0'

requires = [
    'couchdb',
    'setuptools',
    'openprocurement.api',
    'openprocurement.relocation.core'
]

test_requires = requires + [
    'webtest',
    'python-coveralls',
    'openprocurement.tender.openua',
    'openprocurement.tender.openuadefense',
    'openprocurement.tender.openeu',
    'openprocurement.tender.limited',
]
docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'openprocurement.relocation.core.plugins': [
        'relocation.tenders = openprocurement.relocation.tenders.includeme:main'
    ]
}

setup(name='openprocurement.relocation.tenders',
      version=version,
      description="",
      long_description=open("README.md").read(),
      classifiers=[
        "Framework :: Pylons",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
        ],
      keywords="web services",
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',

      url='https://github.com/openprocurement/openprocurement.relocation.contracts',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.relocation'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      entry_points=entry_points,
      )
