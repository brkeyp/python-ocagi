# -*- coding: utf-8 -*-
def validate(scope, output):
    import os
    return os.path.exists('test.txt')