#! /usr/bin/python3.9

import logging
import sys

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/username/ExampleFlask/')

from Planning import app as application

application.secret_key = 'anything you wish'