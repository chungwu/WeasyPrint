# coding: utf8
"""
    weasyprint.tests.test_text
    --------------------------

    Test the text layout.

    :copyright: Copyright 2011-2012 Simon Sapin and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

import os

import cairo

from ..css import StyleDict
from ..css.properties import INITIAL_VALUES
from ..text import split_first_line
from .test_layout import parse, body_children
from .testing_utils import FONTS, assert_no_logs


FONTS = FONTS.split(', ')


def make_text(text, width=None, **style):
    """Wrapper for split_first_line() creating a StyleDict."""
    style = StyleDict({
        'font_family': ['Nimbus Mono L', 'Liberation Mono', 'FreeMono',
                        'monospace'],
    }, INITIAL_VALUES).updated_copy(style)
    return split_first_line(text, style, hinting=False, max_width=width)


@assert_no_logs
def test_line_content():
    """Test the line break for various fixed-width lines."""
    for width, remaining in [(100, 'text for test'),
                             (45, 'is a text for test')]:
        text = 'This is a text for test'
        _, length, resume_at, _, _, _ = make_text(
            text, width, font_family=FONTS, font_size=19)
        assert text[resume_at:] == remaining
        assert length == resume_at


@assert_no_logs
def test_line_with_any_width():
    """Test the auto-fit width of lines."""
    _, _, _, width_1, _, _ = make_text('some text')
    _, _, _, width_2, _, _ = make_text('some text some text')
    assert width_1 < width_2


@assert_no_logs
def test_line_breaking():
    """Test the line breaking."""
    string = 'This is a text for test'

    # These two tests do not really rely on installed fonts
    _, _, resume_at, _, _, _ = make_text(string, 90, font_size=1)
    assert resume_at is None

    _, _, resume_at, _, _, _ = make_text(string, 90, font_size=100)
    assert string[resume_at:] == 'is a text for test'

    _, _, resume_at, _, _, _ = make_text(string, 100, font_family=FONTS,
                                         font_size=19)
    assert string[resume_at:] == 'text for test'


@assert_no_logs
def test_text_dimension():
    """Test the font size impact on the text dimension."""
    string = 'This is a text for test. This is a test for text.py'
    _, _, _, width_1, height_1, _ = make_text(string, 200, font_size=12)

    _, _, _, width_2, height_2, _ = make_text(string, 200, font_size=20)
    assert width_1 * height_1 < width_2 * height_2


@assert_no_logs
def test_text_font_size_zero():
    """Test a text with a font size set to 0."""
    page, = parse('''
        <style>
            p { font-size: 0; }
        </style>
        <p>test font size zero</p>
    ''')
    paragraph, = body_children(page)
    # zero-sized text boxes are removed
    line, = paragraph.children
    assert not line.children
    assert line.height == 0
    assert paragraph.height == 0
