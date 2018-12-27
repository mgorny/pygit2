# -*- coding: UTF-8 -*-
#
# Copyright 2010-2017 The pygit2 contributors
#
# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2,
# as published by the Free Software Foundation.
#
# In addition to the permissions in the GNU General Public License,
# the authors give you unlimited permission to link the compiled
# version of this file into combinations with other programs,
# and to distribute those combinations without any restriction
# coming from the use of this file.  (The General Public License
# restrictions do apply in other respects; for example, they cover
# modification of the file, and distribution when not linked into
# a combined executable.)
#
# This file is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING.  If not, write to
# the Free Software Foundation, 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301, USA.

"""Tests for Object objects."""

from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from pygit2 import GIT_OBJ_TREE, GIT_OBJ_TAG, Tree, Tag
from . import utils


BLOB_SHA = 'a520c24d85fbfc815d385957eed41406ca5a860b'
BLOB_CONTENT = """hello world
hola mundo
bonjour le monde
""".encode()
BLOB_NEW_CONTENT = b'foo bar\n'
BLOB_FILE_CONTENT = b'bye world\n'

class ObjectTest(utils.RepoTestCase):

    def test_equality(self):
        # get a commit object twice and see if it equals itself
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit_a = self.repo[commit_id]
        commit_b = self.repo[commit_id]

        assert commit_a is not commit_b
        assert commit_a == commit_b
        assert not(commit_a != commit_b)

    def test_hashing(self):
        # get a commit object twice and compare hashes
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit_a = self.repo[commit_id]
        commit_b = self.repo[commit_id]

        assert hash(commit_a)

        assert commit_a is not commit_b
        assert commit_a == commit_b
        # if the commits are equal then their hash *must* be equal
        # but different objects can have the same commit
        assert hash(commit_a) == hash(commit_b)

        # sanity check that python container types work as expected
        s = set()
        s.add(commit_a)
        s.add(commit_b)
        assert len(s) == 1
        assert commit_a in s
        assert commit_b in s

        d = {}
        d[commit_a] = True
        assert commit_b in d
        assert d[commit_b]

        l = [commit_a]
        assert commit_b in l

    def test_peel_commit(self):
        # start by looking up the commit
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]
        # and peel to the tree
        tree = commit.peel(GIT_OBJ_TREE)

        assert type(tree) == Tree
        assert str(tree.id) == 'fd937514cb799514d4b81bb24c5fcfeb6472b245'

    def test_peel_commit_type(self):
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]
        tree = commit.peel(Tree)

        assert type(tree) == Tree
        assert str(tree.id) == 'fd937514cb799514d4b81bb24c5fcfeb6472b245'


    def test_invalid(self):
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]

        with pytest.raises(ValueError): commit.peel(GIT_OBJ_TAG)

    def test_invalid_type(self):
        commit_id = self.repo.lookup_reference('refs/heads/master').target
        commit = self.repo[commit_id]

        with pytest.raises(ValueError): commit.peel(Tag)

    def test_short_id(self):
        seen = dict() # from short_id to full hex id
        def test_obj(obj, msg):
            short_id = obj.short_id
            msg = msg+" short_id="+short_id
            already = seen.get(short_id)
            if already:
                assert already == obj.id.hex
            else:
                seen[short_id] = obj.id.hex
                lookup = self.repo[short_id]
                assert obj.id == lookup.id
        for commit in self.repo.walk(self.repo.head.target):
            test_obj(commit, "commit#"+commit.id.hex)
            tree = commit.tree
            test_obj(tree, "tree#"+tree.id.hex)
            for entry in tree:
                test_obj(self.repo[entry.hex], "entry="+entry.name+"#"+entry.hex)
