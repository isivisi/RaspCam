from setuptools import setup

setup(
    name='camera',
    description='',
    author='John Iannandrea',
    author_email='jiannandrea@gmail.com',
    url='http://github.com/isivisi/camera',
    install_requires=[
        'picamera',
        'tornado'
    ],
    include_package_data=True,
    version='0.1.4',
    packages=['raspcam'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'pycam = pycam:main'
        ]
    }
)