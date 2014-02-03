# coding: utf8
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

import pytest

from scorify import scoresheet
from scorify import directives


@pytest.fixture
def good_sample_csv():
    import StringIO
    import csv
    return csv.reader(StringIO.StringIO("""
    layout,header
    layout,skip
    layout,data

    exclude,ppt,0000
    exclude,ppt,9999

    transform,normal,map(1:5,1:5)
    transform,reverse,map(1:5,5:1)

    score,happy1,happy,normal
    score,sad1,sad,reverse
    score,happy2,happy,reverse
    score,sad2,sad,normal

    measure,mean_happy,mean(happy)
    measure,mean_sad,mean(sad)
    """))


def test_successful_read(good_sample_csv):
    reader = scoresheet.Reader(good_sample_csv)
    ss = reader.read_into_scoresheet()
    assert type(ss) == scoresheet.Scoresheet

def test_layout_section():
    skip = directives.Layout('skip')
    header = directives.Layout('header')
    data = directives.Layout('data')

    ls = scoresheet.LayoutSection([header,data])
    assert ls.is_valid()

    ls = scoresheet.LayoutSection([header,skip,data])
    assert ls.is_valid()

    ls = scoresheet.LayoutSection([header,header,data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header,data,data])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([header,data,skip])
    assert not ls.is_valid()

    ls = scoresheet.LayoutSection([data,header])
    assert not ls.is_valid()
