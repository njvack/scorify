# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

from collections import namedtuple

import directives

class Scoresheet(object):
    def __init__(self):
        self.errors = []
        self.layout_section = LayoutSection()
        self.exclude_section = ExcludeSection
        self.transform_section = None
        self.score_section = None
        self.measure_section = None

    def add_error(self, line_number, message):
        self.errors.append(ScoresheetMessage(line_number, message))


ScoresheetMessage = namedtuple('ScoresheetMessage', ['line', 'message'])


class Reader(object):
    def __init__(self, data=None):
        """
        data should be a csv.Reader-like object. Notably, it should be interable,
        return a list per iteration, and support line_number.
        """
        self.data = data

    def read_into_scoresheet(self, sheet=None):
        if sheet == None:
            sheet = Scoresheet()
        section_map = {
            'layout': sheet.layout_section,
            'exclude' : sheet.exclude_section
        }
        layout_lines = []
        exclusion_lines = []

        for line in self.data:
            ignore_line = (len(line) < 2) or (line[0] == "#")
            if ignore_line:
                continue
            stripped_parts = [str(p).strip() for p in line]
            line_type = stripped_parts[0]
            line_params = stripped_parts[1:]
            try:
                sect = section_map[line_type]
            except KeyError:
                sheet.add_error(
                    self.data.line_num,
                    "I don't understand {0}".format(line_type))
        return sheet

class Section(object):
    def __init__(self, directives=[]):
        super(Section, self).__init__()
        self.directives = directives
        self.errors = []

    def append_from_strings(self, string_list):
        raise NotImplementedError()


class LayoutSection(Section):
    def __init__(self, directives=[]):
        super(LayoutSection, self).__init__(directives)

    def is_valid(self):
        self.errors = []
        headers = [d for d in self.directives if d.info == 'header']
        if len(headers) > 1:
            self.errors.append('you can only have one header in your layout')
        if len(headers) < 1:
            self.errors.append('you must have one header in your layout')

        datas = [d for d in self.directives if d.info == 'data']
        if len(datas) > 1:
            self.errors.append('you can only have one data in your layout')
        if len(datas) < 1:
            self.errors.append('you must have one data in your layout')

        last_entry = self.directives[-1]
        if not last_entry.info == 'data':
            self.errors.append("data needs to come last in your layout")

        return len(self.errors) == 0

    def append_from_strings(self, string_list):
        """
        string_list will have the "layout" stripped off already; it should
        be one of ["header", "data", "skip"] but we'll let directives.Layout
        figure that out.
        """
        if len(string_list) < 1:
            raise directives.DirectiveError("layout must be 'header', 'data', or 'skip'")
        self.directives.append(directives.Layout(string_list[0]))


class ExcludeSection(Section):
    def __init__(self, directives):
        super(ExcludeSection, self).__init__(directives)

    def append_from_strings(self, string_list):
        if len(string_list) < 1:
            raise directives.DirectiveError(
                "exclude must specify a column name")
        exclude_col = string_list[0]
        exclude_val = ''
        if len(string_list) > 1:
            exclude_val = string_list[1]
        self.directives.append(directives.Exclude(exclude_col, exclude_val))

