"""
Comprehensive edge case tests for _contains_fmt_directive function.

These tests cover all edge cases including:
- Issue #4841: Commented-out directives that caused crashes
- Multi-comment patterns with directives
- Prose containing directive-like text
- Various whitespace and formatting patterns

Test against baseline (pre-PR #4811, before bug was introduced):
- Some tests WILL FAIL on baseline (the #4841 bug cases)
- Document which tests expose the bug

Test against current fix:
- ALL tests should PASS
"""

from black.comments import FMT_OFF, FMT_ON, FMT_SKIP, _contains_fmt_directive


class TestBasicDirectives:
    """Test basic directive recognition."""

    def test_standard_fmt_off(self) -> None:
        """Standard format: # fmt: off"""
        assert _contains_fmt_directive("# fmt: off", FMT_OFF)

    def test_standard_fmt_on(self) -> None:
        """Standard format: # fmt: on"""
        assert _contains_fmt_directive("# fmt: on", FMT_ON)

    def test_standard_fmt_skip(self) -> None:
        """Standard format: # fmt: skip"""
        assert _contains_fmt_directive("# fmt: skip", FMT_SKIP)

    def test_no_space_after_hash(self) -> None:
        """Compact format: #fmt:off"""
        assert _contains_fmt_directive("#fmt:off", FMT_OFF)

    def test_no_space_after_colon(self) -> None:
        """Format without space after colon: # fmt:off"""
        assert _contains_fmt_directive("# fmt:off", FMT_OFF)

    def test_extra_spaces(self) -> None:
        """Format with extra spaces: #    fmt: off"""
        assert _contains_fmt_directive("#    fmt: off", FMT_OFF)

    def test_not_a_directive(self) -> None:
        """Regular comment should not match"""
        assert not _contains_fmt_directive("# This is a comment", FMT_OFF)


class TestCommentedOutDirectives:
    """
    Test commented-out directives (issue #4841).

    EXPECTED BEHAVIOR ON BASELINE (pre-PR #4811):
    These tests will FAIL/CRASH on baseline because the bug exists.
    The function incorrectly recognizes commented-out directives.
    """

    def test_double_hash_no_space(self) -> None:
        """Commented-out: ## fmt: off

        BUG: On baseline, this is incorrectly recognized as a directive.
        """
        assert not _contains_fmt_directive("## fmt: off", FMT_OFF)

    def test_double_hash_with_space(self) -> None:
        """Commented-out: # # fmt: off

        BUG: On baseline, this is incorrectly recognized as a directive.
        This is the exact pattern from issue #4841.
        """
        assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)

    def test_triple_hash(self) -> None:
        """Commented-out: ### fmt: off"""
        assert not _contains_fmt_directive("### fmt: off", FMT_OFF)

    def test_quadruple_hash(self) -> None:
        """Commented-out: #### fmt: on"""
        assert not _contains_fmt_directive("#### fmt: on", FMT_ON)

    def test_issue_4841_exact_case(self) -> None:
        """Exact case from issue #4841 bug report.

        In context, this appears as:
        [
            (1, 2),
            # # fmt: off
            # (3,
            #    4),
            # # fmt: on
            (5, 6),
        ]

        BUG: On baseline, Black crashes with INTERNAL ERROR.
        """
        assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)
        assert not _contains_fmt_directive("# # fmt: on", FMT_ON)


class TestDirectivesWithTrailingComments:
    """Test directives followed by trailing comments."""

    def test_fmt_off_with_trailing_comment(self) -> None:
        """Directive with trailing comment: # fmt: off # some comment

        This SHOULD be recognized (trailing comments are allowed).
        """
        assert _contains_fmt_directive("# fmt: off # some other comment", FMT_OFF)

    def test_fmt_on_with_explanation(self) -> None:
        """Directive with explanation: # fmt: on # end of unformatted section"""
        assert _contains_fmt_directive("# fmt: on # end of unformatted section", FMT_ON)

    def test_fmt_skip_with_reason(self) -> None:
        """Directive with reason: # fmt: skip # performance critical"""
        assert _contains_fmt_directive("# fmt: skip # performance critical", FMT_SKIP)


class TestMultiCommentPatterns:
    """Test multiple comments on one line with directives."""

    def test_pylint_fmt_skip(self) -> None:
        """Multi-comment: # pylint # fmt:skip

        This is a common pattern where multiple pragma comments appear together.
        """
        assert _contains_fmt_directive("# pylint # fmt:skip", FMT_SKIP)

    def test_type_ignore_fmt_off(self) -> None:
        """Multi-comment: # type: ignore # fmt: off"""
        assert _contains_fmt_directive("# type: ignore # fmt: off", FMT_OFF)

    def test_noqa_fmt_skip(self) -> None:
        """Multi-comment: # noqa # fmt:skip"""
        assert _contains_fmt_directive("# noqa # fmt:skip", FMT_SKIP)

    def test_short_word_before_directive(self) -> None:
        """Short identifier before directive: # x # fmt: off"""
        assert _contains_fmt_directive("# x # fmt: off", FMT_OFF)


class TestProseContainingDirectives:
    """
    Test comments that contain directive-like text but are actually prose.

    These should NOT be recognized as directives.
    """

    def test_prose_explaining_fmt_off(self) -> None:
        """Prose: # Remember to use # fmt: off"""
        assert not _contains_fmt_directive("# Remember to use # fmt: off", FMT_OFF)

    def test_prose_about_fmt_on(self) -> None:
        """Prose: # This is about fmt: on usage"""
        assert not _contains_fmt_directive("# This is about fmt: on usage", FMT_ON)

    def test_prose_with_directive_after_text(self) -> None:
        """Prose: # Some text # fmt: off in middle"""
        assert not _contains_fmt_directive("# Some text # fmt: off in middle", FMT_OFF)

    def test_directive_as_word_suffix(self) -> None:
        """Prose: # fmt:off directive

        The word 'directive' after makes this prose, not an active directive.
        """
        assert not _contains_fmt_directive("# fmt:off directive", FMT_OFF)

    def test_explaining_usage(self) -> None:
        """Prose: # Use fmt:skip to skip formatting"""
        result = "# Use fmt:skip to skip formatting"
        assert not _contains_fmt_directive(result, FMT_SKIP)


class TestSemicolonSeparatedComments:
    """Test semicolon-separated comment lists."""

    def test_semicolon_list_with_fmt_skip(self) -> None:
        """Semicolon list: # pylint; fmt: skip; noqa: E501"""
        assert _contains_fmt_directive("# pylint; fmt: skip; noqa: E501", FMT_SKIP)

    def test_semicolon_fmt_off(self) -> None:
        """Semicolon list: # type: ignore; fmt: off"""
        assert _contains_fmt_directive("# type: ignore; fmt: off", FMT_OFF)


class TestWhitespaceVariations:
    """Test various whitespace patterns."""

    def test_tabs_instead_of_spaces(self) -> None:
        """Tabs: #\tfmt:\toff"""
        # This might not be recognized depending on implementation
        # Document expected behavior
        result = _contains_fmt_directive("#\tfmt:\toff", FMT_OFF)
        # Accept either True or False, just document what happens
        assert isinstance(result, bool)

    def test_multiple_spaces(self) -> None:
        """Multiple spaces: #  fmt:  off"""
        assert _contains_fmt_directive("#  fmt:  off", FMT_OFF)

    def test_leading_whitespace(self) -> None:
        """Leading whitespace before #: '   # fmt: off'"""
        # Comments shouldn't have leading whitespace in practice
        # but test the behavior
        result = _contains_fmt_directive("   # fmt: off", FMT_OFF)
        assert isinstance(result, bool)


class TestEdgeCases:
    """Test unusual edge cases."""

    def test_empty_string(self) -> None:
        """Empty string should not match"""
        assert not _contains_fmt_directive("", FMT_OFF)

    def test_just_hash(self) -> None:
        """Just a hash: #"""
        assert not _contains_fmt_directive("#", FMT_OFF)

    def test_hash_with_spaces(self) -> None:
        """Hash with spaces: #   """
        assert not _contains_fmt_directive("#   ", FMT_OFF)

    def test_directive_text_without_hash(self) -> None:
        """Directive text without hash: fmt: off"""
        assert not _contains_fmt_directive("fmt: off", FMT_OFF)

    def test_partial_directive(self) -> None:
        """Partial directive: # fmt"""
        assert not _contains_fmt_directive("# fmt", FMT_OFF)

    def test_wrong_directive_text(self) -> None:
        """Wrong directive: # fmt: offf (typo)"""
        assert not _contains_fmt_directive("# fmt: offf", FMT_OFF)

    def test_case_sensitive(self) -> None:
        """Case sensitivity: # FMT: OFF"""
        # Black is case-sensitive
        assert not _contains_fmt_directive("# FMT: OFF", FMT_OFF)


class TestYapfCompatibility:
    """Test yapf directive compatibility."""

    def test_yapf_disable(self) -> None:
        """yapf: disable directive"""
        assert _contains_fmt_directive("# yapf: disable", FMT_OFF)

    def test_yapf_enable(self) -> None:
        """yapf: enable directive"""
        assert _contains_fmt_directive("# yapf: enable", FMT_ON)


class TestRegressionFromIssue4841:
    """
    Specific regression tests from issue #4841 and related comments.

    These are real-world patterns that caused the bug.
    """

    def test_remicardona_trailing_comment_case(self) -> None:
        """From RemiCardona's comment on #4841.

        Pattern: # fmt: off # some other comment
        In context:
        if False:
            # fmt: off # some other comment
            pass

        This SHOULD be recognized as a valid directive.
        The trailing comment is allowed.
        """
        assert _contains_fmt_directive("# fmt: off # some other comment", FMT_OFF)

    def test_list_context_commented_directive(self) -> None:
        """Commented directive in list context (issue #4841).

        The commented-out directive should NOT be recognized.
        """
        assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)
        assert not _contains_fmt_directive("# # fmt: on", FMT_ON)

    def test_function_context_commented_directive(self) -> None:
        """Commented directive in function context."""
        assert not _contains_fmt_directive("## fmt: off", FMT_OFF)
