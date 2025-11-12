"""Tests for comment handling functions."""

from black.comments import FMT_OFF, FMT_ON, FMT_SKIP, _contains_fmt_directive


def test_contains_fmt_directive_ignores_commented_out_directives():
    """Test that commented-out fmt directives are not recognized.

    This is a regression test for issue #4841 where Black incorrectly
    treated commented-out directives like "## fmt: off" as active directives.
    """
    # Basic directives - these SHOULD be recognized
    assert _contains_fmt_directive("# fmt: off", FMT_OFF)
    assert _contains_fmt_directive("#fmt:off", FMT_OFF)
    assert _contains_fmt_directive("# fmt: on", FMT_ON)
    assert _contains_fmt_directive("#    fmt: off", FMT_OFF)

    # Commented-out directives - these should NOT be recognized
    # Multiple consecutive # at the start
    assert not _contains_fmt_directive("## fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("### fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("##fmt:off", FMT_OFF)

    # Space after first # followed by another #
    assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("# ## fmt: off", FMT_OFF)

    # Multi-comment patterns - these SHOULD be recognized
    # Common pattern: pragma comment followed by fmt directive
    assert _contains_fmt_directive("# pylint # fmt:skip", FMT_SKIP)
    assert _contains_fmt_directive("# pylint # fmt: skip", FMT_SKIP)
    assert _contains_fmt_directive("# some # fmt: off", FMT_OFF)

    # Directive at the start followed by other comments
    assert _contains_fmt_directive("# fmt: off # some other comment", FMT_OFF)
    assert _contains_fmt_directive("# fmt: skip # noqa: E501 # pylint", FMT_SKIP)

    # Semicolon-separated comments (established convention)
    assert _contains_fmt_directive("# pylint; fmt: skip; noqa: E501", FMT_SKIP)

    # Prose containing directive-like text - should NOT be recognized
    # The directive appears in the middle of a sentence (multiple words before it)
    assert not _contains_fmt_directive("# Remember to use # fmt: on after # fmt: off")
    assert not _contains_fmt_directive("# This is about fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("# Some text then # fmt: off in middle", FMT_OFF)
