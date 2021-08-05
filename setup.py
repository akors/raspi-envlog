#!/usr/bin/env python

import os
from distutils.core import setup

setup(name='raspi-envlog',
      version='1.1',
      description='Raspberry Pi environment logger',
      author='Alexander Korsunsky',
      author_email='a.korsunsky@gmail.com',
      url='https://github.com/akors/raspi-envlog',
      packages=['raspi_envlog'],
      package_dir={'': 'py'},
      scripts=[os.path.join('py/envlog-monitor')],
      install_requires=[
        'influxdb',
        'sdnotify',
        'vcgencmd @ https://github.com/nicmcd/vcgencmd/tarball/master',
        'Adafruit_DHT',
        'icmplib']
     )
