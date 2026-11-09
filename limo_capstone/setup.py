import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'limo_capstone'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'maps'), [f for f in glob('maps/*') if os.path.isfile(f)]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='pcu',
    maintainer_email='user@todo.todo',
    description='LIMO Capstone Project Package',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'stall_detector_node = limo_capstone.stall_detector_node:main',
        ],
    },
)
