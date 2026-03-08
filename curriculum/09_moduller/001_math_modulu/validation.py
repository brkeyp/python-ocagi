# -*- coding: utf-8 -*-
def validate(scope, output):
    has_module = 'math' in scope or 'pi' in scope
    has_output = '3.14' in output
    return has_module and has_output