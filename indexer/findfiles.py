# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Jordi Mas i Hernandez <jmas@softcatala.org>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

import fnmatch
import os
from pathlib import Path


class FindFiles:
    """
    Utility class that provides functionality for finding files, directories or
    both with a given pattern.
    """

    @staticmethod
    def find_recursive(directory: str, pattern: str) -> list[str]:
        """
        Recursively find files matching a pattern inside a directory tree.

        Args:
            directory (str): The root directory from which the recursive search
                begins.
            pattern (str): Unix shell-style wildcard pattern to match file names.

        Returns:
            list[str]: A sorted list of unique file paths that match the pattern.
        """
        filelist_set = set()
        dirs = FindFiles.find_dirs(directory, "*")
        for _dir in dirs:
            files = FindFiles.find(_dir, pattern)
            for f in files:
                filelist_set.add(f)

        filelist = list(filelist_set)
        filelist.sort()
        return filelist

    @staticmethod
    def find_dirs(directory: str, pattern: str) -> list[str]:
        """
        Find directories matching a pattern inside a directory tree.

        Args:
            directory (str): The root directory where the search starts.
            pattern (str): Unix shell-style wildcard pattern to match directory names.

        Returns:
            list[str]: A sorted list of directory paths that match the pattern.
        """
        dirlist = []

        for root, dirs, _ in os.walk(directory):
            for basename in dirs:
                if fnmatch.fnmatch(basename, pattern):
                    filename = Path(root) / basename
                    dirlist.append(str(filename))

        dirlist.sort()
        return dirlist

    @staticmethod
    def find(directory: str, pattern: str) -> list[str]:
        """
        Find files matching a pattern inside a directory tree.

        Args:
            directory (str): The root directory where the file search starts.
            pattern (str): Unix shell-style wildcard pattern to match file names.

        Returns:
            list[str]: A sorted list of file paths that match the pattern.
        """
        filelist = []

        for root, _, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = Path(root) / basename
                    filelist.append(str(filename))

        filelist.sort()
        return filelist
