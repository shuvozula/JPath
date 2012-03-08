#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# python-jpath: Simple JSON parser using X-path like strings.

# Copyright (c) 2012, Spondon Saha

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the author nor the names of its contributors may
#       be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__author__ = 'spondonsaha@gmail.com (Spondon Saha)'

import io
import json


class Error(Exception):
    """Base Exception class."""
    pass


def open(file_path=None, file_obj=None):
    """Opens a file-like object and reads its contents into a json object.
    
    Arguments:
        file_path: Path to the json file
    
    Raises:
        IOError: thrown if invalid file-path is given
        ValueError: thrown if error is encountered when loading json-data
    
    Returns:
        A JPath object.
    """
    # Perform validations
    if not file_path and not file_obj:
        raise ValueError('Nothing to open: No file-path, no file-object!')
    if file_obj and not isinstance(file_obj, file):
        raise IOError('Invalid file-like-object!\n%s' % file_obj.__class__)
    # open the file if not file-like-object provided
    if not file_obj:
        file_obj = io.open(file_path, 'rb')
    # read in all the contents into memory
    # TODO: need to optimize this
    json_string = file_obj.read()
    # return the JPath object created from the file-like-object provided
    return JPath(json_string)


def read(json_string=None):
    """Takes the provided JSON string and returns a JPath object.

    Expects a json string, either from a .read() operation or an arbitrary
    string containing json data. This string is then passed onto Jpath
    constructor to return an object of JPath.

    Arguments:
        json_string: An arbitrary json string.

    Raises:
        ValueError: Iff the provided json_string is None.

    Returns:
        A JPath object.
    """
    if not json_string:
        raise ValueError('No json string provided!')
    else:
        return JPath(json_string)


class JPath(object):
    """The JPath class for parsing JSON data."""

    def __init__(self, json_string=None):
        """JPath Constructor."""
        if not json_string:
            raise ValueError('No Json string provided! Use open() or read().')
        else:
            self.json_data = self._load_json(json_string)

    def __str__(self):
        """Pretty print json string."""
        return json.dumps(self.json_data, sort_keys=True, indent=4)

    def _load_json(self, json_string=None):
        """Creates a json object made out of the provided json string.

        Arguments:
            json_string: string containing json data.

        Raises:
            ValueError: Iff json_string is set to None.

        Returns:
            A json object.
        """
        if not json_string:
            raise ValueError('No json string provided!')
        return json.loads(json_string)

    def _get_element(self, json_data, path=None, tokens=None):
        """Much like XPath, but for Json.
        
        It parses the path-string and recursively dives into the JSON data tree
        to fetch the requested element. A sample path could be a->b->c, which
        returns the element list/dict c, which is a child of b, which is a child
        of a.
        
        Arguments:
          json_data: A simplejson object.
          path: a string that looks like XPath.
          tokens: usually a list of dict-names from the migration-settings file.
        
        Returns:
          A value or a dict based on the requested path-string
        
        Raises:
          Error: in case no path-string is provided.
        """
        if not tokens:
            if not path:
                raise Error('No path string received: %s' % path)
            else:
                path = path.strip('/')
                tokens = path.split('/')
        if len(tokens) > 1:
            pop_token = tokens.pop(0)  # dequeue the first element, LIFO
            new_json_data = json_data[pop_token]
            return self._get_element(json_data=new_json_data, tokens=tokens)
        else:
            return json_data[tokens[0]]

    def get(self, json_path):
        """Gets migration configurations from settings file.
        
        Arguments:
          json_path: path to the json configuration file.
        
        Raises:
          Error: if no data was pre-loaded into self.json_data. Also raised when
          the provided path does not return a value from the settings file.
        
        Returns:
          the setting value requested by the provided json-path.
        """
        req_setting = None
        if not self.json_data:
            raise Error('JSON data did not load successfully.')
        try:
            return self._get_element(json_data=self.json_data, path=json_path)
        except Exception or StandardError, ex:
            raise Error('Wrong JPath provided or data is invalid!\n%s' % ex)
