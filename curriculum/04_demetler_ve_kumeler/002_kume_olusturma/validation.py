# -*- coding: utf-8 -*-
def validate(scope, output):
    return isinstance(scope.get('my_set'), set)