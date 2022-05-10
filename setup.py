from setuptools import find_packages, setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

# Get admin.
admin = {}
with open("hvec_tide/admin.py") as fp:
    exec(fp.read(), admin)

setup(
    name = 'hvec_tide',
    version = admin['__version__'],
    author = admin['__author__'],
    author_email = admin['__author_email__'],
    description = 'Python package with convenience tools for utide',
    long_description=long_description,
    url='https://github.com/hvec-lab',
    project_urls={
        'Source': 'https://github.com/hvec-lab/hvec_tide'
#        'Documentation': 'http://pastas.readthedocs.io/en/latest/',
#        'Tracker': 'https://github.com/pastas/pastas/issues',
#        'Help': 'https://github.com/pastas/pastas/discussions'
    },
    license = 'MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10'
        'Topic :: Scientific/Engineering'
    ],
    platforms='Windows',
    install_requires=['numpy>=1.17',
                      'pandas>=1.1',
                      'scipy>=1.3',
                      'utide',
                      'tqdm',
                      'datetime'],
    packages=find_packages(exclude=['development', '__pycache__']),
)