#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""App com modo debug para ver erros"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from src.main import create_app

if __name__ == '__main__':
    app = create_app('development')
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )
