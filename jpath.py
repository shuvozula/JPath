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

"""General parser module that contains various parsers.

Currently, only houses the JPath parser class.
"""

import json
import re


class Error(Exception):
  """Base Exception class."""


class JPathError(Error):
  """Base error class for JPath related errors."""


class QueryError(JPathError):
  """Raised whenever a query related exception occurs."""


class JPath(object):
  """JPath parser class to manage JSON data.

  This parser can be used to manage JSON data, by performing get, set operations
  on it using JPath queries. These Jpath queries look very similar to Xpath
  queries and carries over many of the similar syntactic goodies, such as
  defining predicates to fetch nodes with a certain value: [1] or [2] to fetch
  the first or second element respectively, or [@foo=bar] which fetches a node
  whose attribute called "foo" has the value "bar". To iterate over large data
  sets and perform get or set operations over each iter-element, IterItems()
  can be used, with the only constraint that the provided Jpath query has
  an iterable token "[*]", otherwise a QueryError is raised. Other syntactic
  goodies will be added as this library matures.

  Attributes:
    _delimiter: str, Forward-slash delimiter for jpath queries.
    _attribute_sniffer_regex: re, Regex to extract the index or key-attribute
        from jpath queries.
  """

  _delimiter = '/'
  _attribute_sniffer_regex = re.compile(r"""
      ^                          # start of string
      (                          # -- start of group --
        \[                       # start of index classifier
          (?P<index>             # -- start of group --
            \d+                  # index number
          )                      # -- end of group --
        \]                       # end of index classifier
      )                          # -- end of group --
      |                          # ---~~~ OR ~~~----
      (                          # -- start of group --
        \[@                      # start of instrospect token classifier
          (?P<key_attribute>     # -- start of key-attribute --
            \w+                  # alphanumeric key attribute
          )                      # -- end of key-attribute --
          =
          (?P<key_value>         # -- start of key-value --
            .+                   # Any string of any length
          )                      # -- end of key-value --
        \]                       # end of instrospect token classifier
      )                          # -- end of group --
      $                          # end of string
      """, re.VERBOSE | re.IGNORECASE)

  def __init__(self, json_data):
    """Constructor for JPath.

    Takes the JSON data structure as a string or a dict or a list. If the data
    is provided as stringified JSON, then its fed to json.loads to return
    the corresponding dictionary/list.

    Arguments:
      json_data: str|dict|list, JSON data stucture to be manipulated.

    Raises:
      ValueError: If the provided json_data is either None or an empty string.
    """
    if not json_data:
      raise ValueError(('Expecting stringified JSON data, dict or a list, '
                        'got: type=%r "%r"') % (type(json_data), json_data))
    self.json_data = json_data
    if isinstance(json_data, basestring):
      self.json_data = json.loads(json_data)

  def __str__(self):
    """Pretty print json string."""
    return json.dumps(self.json_data, sort_keys=True, indent=4)

  def _GrabDataByToken(self, json_data, token):
    """Helper method to extract data by type of token: index or key-attribute.

    Arguments:
      json_data: dict, JSON data to use with the token.
      token: str, token string to use to query the json_data dictionary.

    Returns:
      The fetched json data using the token.
    """
    new_json_data = None
    m = self._attribute_sniffer_regex.search(token)
    if m:
      findings = m.groupdict()
      if findings['index']:
        token = int(findings['index'])
        new_json_data = json_data[token]
      elif findings['key_attribute'] and findings['key_value']:
        for data_elem in json_data:
          if data_elem[findings['key_attribute']] == findings['key_value']:
            new_json_data = data_elem
            break
    else:
      new_json_data = json_data[token]
    return new_json_data

  def Get(self, jpath_query, json_data=None, tokens=None):
    """Gets the requested JSON subtree or value based on provided jpath-query.

    It parses the path-string and recursively dives into the JSON data tree
    to fetch the requested element. A sample path could be a/b/c, which
    returns the element keyed by c, which is a child of b, which is a child
    of a. The path could also have key attributes, such as a/[@attr=b]/c, which
    basically returns value keyed by c from a dictionary which has a key
    attribute by the name 'attr' with value 'b'  and is one of the children or
    only child of a.

    Arguments:
      jpath_query: str, Jpath query string.
      json_data: dict, Optional JSON data to be introspected for fetching
          sub-tree.
      tokens: list, Result of splitting the path by the provided delimiter.

    Returns:
      A str, int, dict or list based on the requested path-string.

    Raises:
      JPathError: in case no path-string is provided.
    """
    if not json_data:
      json_data = self.json_data
    if not tokens:
      if not jpath_query:
        raise JPathError('No Jpath string provided: %r' % jpath_query)
      else:
        jpath_query = jpath_query.strip(self._delimiter)
        tokens = jpath_query.split(self._delimiter)
    # dequeue the first element, LIFO
    token = tokens.pop(0)
    # check if its an index number or key attribute and fetch the json-data
    new_json_data = self._GrabDataByToken(json_data, token)
    if tokens:
      # make recurive call to traverse to nested data
      return self.Get(jpath_query=jpath_query,
                      json_data=new_json_data,
                      tokens=tokens)
    else:
      return new_json_data

  def Set(self, jpath_query, set_value, json_data=None, tokens=None):
    """Sets the value of the JSON data-set based on provided jpath-query.

    Arguments:
      jpath_query: str, JPath query string.
      set_value: *, Value to be added to data end-point specified by
          jpath-query. Value could be any one of dict, list, str, int or float.
      json_data: dict, JSON data to be introspected for setting set_value.
      tokens: list, List of tokens acquired by splitting the path by '/'.

    Returns:
      True on success or False on failure.

    Raises:
      JPathError: If no jpath query is provided.
      QueryError: If the provided query is speculative and not absolute.
    """
    if not json_data:
      json_data = self.json_data
    if not tokens:
      if not jpath_query:
        raise JPathError('No Jpath string provided: %r' % jpath_query)
      else:
        jpath_query = jpath_query.strip(self._delimiter)
        tokens = jpath_query.split(self._delimiter)
    # dequeue the first element, LIFO
    token = tokens.pop(0)
    # only absolute tokens acceptable
    if token.startswith('[@'):
      raise QueryError(
          ('Only absolute queries acceptable, such as /path/to/1/data. No '
           'speculative queries, such as /[@attr=abc]/ allowed.\n'
           'Got: %r') % token)
    m = re.match(r'(\[(?P<index>\d+)\])|(?P<key>[a-zA-Z0-9]+)', token)
    if m:
      results = m.groupdict()
      key = int(results['index']) if results['index'] else results['key']
    else:
      raise QueryError(
          ('Provided corrupt jpath: %s. Failed at token: %s') % (jpath_query,
                                                                 token))
    if tokens:
      new_json_data = json_data[key]
      # make recurive call to traverse to nested data
      return self.Set(jpath_query=jpath_query,
                      set_value=set_value,
                      json_data=new_json_data,
                      tokens=tokens)
    else:
      json_data[key] = set_value

  def IterItems(self, jpath_query):
    """Iterates over JSON data based on provided json-path.

    This function allows you to iterate over the provided JSON data. The jpath
    query needs to have an iterator token [*], otherwise a JPathError will be
    raised.

    A typical jpath query could look like: /path/to/data_list/[*]/nested_data/

    Where, /path/to/data_list/ is the jpath to where the iterable data-set is
    located and and the /nested_data/ is an optional path that fetches the
    nested-data within each iter-element.

    Arguments:
      jpath_query: str, JPath query string.

    Yields:
      Data fetched from the provided jpath_query.

    Raises:
      JPathError: if the provided jpath-query does not have an iterator token.
    """
    if '[*]' not in jpath_query:
      raise JPathError('Expecting iterator token [*].')
    base_path, trailing_path = jpath_query.split('[*]')
    base_data = self.Get(jpath_query=base_path)
    for data_elem in base_data:
      trailing_data = self.Get(jpath_query=trailing_path, json_data=data_elem)
      yield trailing_data
