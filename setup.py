from setuptools import setup

setup(
    name='lektor-gae',
    description='Publishes your Lektor site to Google App Engine.',
    url='https://github.com/isotherm/lektor-gae/',
    version='0.1',
    author=u'Kirk Meyer',
    author_email='kirk.meyer@alpaxo.com',
    license='MIT',
    platforms='any',
    py_modules=['lektor_gae'],
    entry_points={
        'lektor.plugins': [
            'gae = lektor_gae:GaePlugin',
        ]
    },
    install_requires=[
        'Lektor',
        'PyYAML',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
