import setuptools

with open('readme.md') as fh:
    long_description = fh.read()

setuptools.setup(
    name='md.persistence',
    version='0.1.0',
    description='Set of persistence contracts & implementation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='License :: OSI Approved :: MIT License',
    package_dir={'': 'lib'},
    packages=['md.persistence'],
    install_requires=['md.python.dict==0.*'],
    dependency_links=[
        'https://source.md.land/python/md-python-dict/'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
