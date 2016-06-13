from setuptools import setup

setup(
    name='lektor-gae',
    description='Publishes your Lektor site to Google App Engine.',
    version='0.1',
    author=u'Kirk Meyer',
    author_email='kirk.meyer@alpaxo.com',
    license='MIT',
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
)
