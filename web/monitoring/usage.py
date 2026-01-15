#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright (c) 2017 Jordi Mas i Hernandez <jmas@softcatala.org>
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

import datetime
import logging
from pathlib import Path
from shutil import copyfile


class Usage:
    """
    This class keeps a log of the usage of a service:
        - For usage write a line on the file with the date
        - At the number of days specified cleans old entries
    """

    FILE = "/srv/stats/usage.txt"
    DAYS_TO_KEEP = 7
    rotate = True

    def _set_filename(self, filename: str) -> None:
        self.FILE = filename

    def _get_time_now(self) -> datetime.datetime:
        return datetime.datetime.now()

    def get_date_from_line(self, line: str) -> str:
        """
        Gets the date from a given line by splitting it by "\t" and accessing it.

        Args:
            line (str): The line to get the date from.

        Returns:
            str: The date in string format.
        """
        return line.split("\t", 1)[0]

    def log(self, endpoint, time_used) -> None:  # noqa: ANN001, D102
        try:
            with Path(self.FILE).open("a+") as file_out:
                current_time = self._get_time_now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                file_out.write(
                    "{0}\t{1}\t{2}\n".format(current_time, endpoint, time_used)
                )

            first_line = self._read_first_line()
            if first_line is None:
                raise ValueError("self._read_first_line() returned None")
            if self.rotate and self._is_old_line(first_line):
                self._rotate_file()
        except Exception as exception:
            logging.error("log. Error:" + str(exception))
            pass

    def _get_line_components(self, line: str) -> tuple[str, str, str]:
        components = line.strip().split("\t")
        return components[0], components[1], components[2]

    def _init_stats_dict(self, dictionary: dict) -> dict:
        dictionary["calls"] = 0
        dictionary["time_used"] = 0
        return dictionary

    def get_stats(self, date_requested: datetime.datetime) -> dict:
        """
        Gets a dictionary of statistics about the usage of the application for a
        requested date.

        Args:
            date_requested (datetime.datetime): The date from which to get stats.

        Returns:
            dict: A dictionary containing multiple statistics of usage.
        """
        results = {}
        try:
            with Path(self.FILE).open("r") as file_in:
                for line in file_in:
                    date_component, endpoint, time_component = (
                        self._get_line_components(line)
                    )

                    if endpoint in results:
                        stats = results[endpoint]
                    else:
                        stats = {}
                        results[endpoint] = self._init_stats_dict(stats)

                    datetime_no_newline = date_component
                    line_datetime = datetime.datetime.strptime(
                        datetime_no_newline, "%Y-%m-%d %H:%M:%S"
                    )
                    if line_datetime.date() == date_requested.date():
                        stats["calls"] = stats["calls"] + 1
                        stats["time_used"] = stats["time_used"] + float(
                            time_component
                        )

            for endpoint in results:
                result = results[endpoint]
                calls = result["calls"]
                result["time_used"] = (
                    result["time_used"] / calls if calls else 0
                )

        except Exception as exception:
            logging.error("get_stats. Error:" + str(exception))
            pass

        return results

    def _read_first_line(self) -> str | None:
        try:
            with Path(self.FILE).open("r") as f:
                first = f.readline()
                return first
        except IOError:
            return None

    def _is_old_line(self, line: str) -> bool:
        if line is None:
            return False

        line = self.get_date_from_line(line)
        line_datetime = datetime.datetime.strptime(line, "%Y-%m-%d %H:%M:%S")
        return line_datetime < self._get_time_now() - datetime.timedelta(
            days=self.DAYS_TO_KEEP
        )

    def _rotate_file(self) -> None:
        TEMP = "usage.bak"
        directory = Path(self.FILE).resolve().parent
        temp_file = directory / TEMP

        copyfile(self.FILE, temp_file)

        with (
            Path(temp_file).open("r") as temp,
            Path(self.FILE).open("w") as new,
        ):
            for line in temp:
                if self._is_old_line(line) is False:
                    new.write(line)
