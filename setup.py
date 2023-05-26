import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='arulespy',
    author='Michael Hahsler',
    author_email='mhahsler@lyle.smu.edu',
    description='Python interface to the R package arules',
    keywords='association rules, frequent itemsets',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/mhahsler/arulespy',
    project_urls={
        'Documentation': 'https://github.com/mhahsler/arulespy',
        'Bug Reports':
        'https://github.com/mhahsler/arulespy/issues',
        'Source Code': 'https://github.com/mhahsler/arulespy',
        # 'Funding': '',
        # 'Say Thanks!': '',
    },
    package_dir={'': 'src'},
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        # see https://pypi.org/classifiers/

        'Development Status :: 4 - Beta',

        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',

        'Programming Language :: Python :: 3',
        'Programming Language :: R',
        'Programming Language :: C++',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Operating System :: OS Independent',

        'Topic :: Scientific/Engineering :: Information Analysis'
    ],
    python_requires='>=3.8',
    install_requires=['pandas',
                      'numpy',
                      'scipy',
                      'rpy2'                   
                      ],
    # install_requires=['Pillow'],
    extras_require={
        'dev': ['check-manifest'],
        # 'test': ['coverage'],
    },
    # entry_points={
    #     'console_scripts': [  # This can provide executable scripts
    #         'run=arules:main',
    # You can execute `run` in bash to run `main()` in src/arules/__init__.py
    #     ],
    # },
)

