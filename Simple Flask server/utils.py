#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utils and decorators"""

import hashlib

# Decorators


def action(route, template, methods=['GET']):
    """Decorator to create an action"""
    def real_decorator(function):
        function.pi_api_action = True
        function.pi_api_route = route
        function.pi_api_template = template
        function.pi_api_methods = methods
        return function
    return real_decorator


def only_logged_user():
    """Decorator to specify the action must only be called by logger users"""
    def real_decorator(function):
        function.pi_api_only_logged_user = True
        return function
    return real_decorator


def only_member_user():
    """Decorator to specify the action must only be called by users members of the project"""
    def real_decorator(function):
        function.pi_api_only_member_user = True
        return function
    return real_decorator


def only_admin_user():
    """Decorator to specify the action must only be called by admin users of the project"""
    def real_decorator(function):
        function.pi_api_only_admin_user = True
        return function
    return real_decorator


def cache(time=0, byUser=None):
    """Decorator to specify the number of seconds the result should be cached, and if cache can be shared between users"""
    def real_decorator(function):
        function.pi_api_cache_time = time
        function.pi_api_cache_by_user = byUser
        return function
    return real_decorator


def user_info(props):
    """Decorator to indiquate a list of properties requested about the current user"""
    def real_decorator(function):
        function.pi_api_user_info = props
        return function
    return real_decorator

#Utils


def md5Checksum(filePath):
    """Compute the md5sum of a file"""
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()
