from setuptools import setup

setup(
    name='comodiac',
    version='0.1',
    py_modules=['bb'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        bb=bb:cli
    ''',
)