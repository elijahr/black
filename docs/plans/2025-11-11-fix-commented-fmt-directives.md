# Fix Commented fmt:off/on Directives (Issue #4841) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix Black crash when processing commented-out fmt directives (e.g., `# # fmt: off`) while preserving the fix from PR #4811 that handles actual fmt directives in comment-only blocks.

**Architecture:** The bug is in `_contains_fmt_directive()` function in `src/black/comments.py` which incorrectly identifies commented-out fmt directives as valid directives. The function splits comment strings and finds directive patterns as substrings, causing commented-out directives like `# # fmt: off` to be treated as valid. The fix ensures directives are only recognized when they appear at the start of the comment content, not nested within it.

**Tech Stack:** Python, pytest, Black's AST processing and comment handling system

---

## Task 1: Add Failing Test for Commented-Out Directives

**Files:**
- Create: `tests/data/cases/fmtonoff_commented.py` (new test case file)

**Step 1: Write the failing test case**

Create a new test file with code that triggers the bug (from issue #4841):

```python
# Test case 1: The original bug report - commented-out fmt directives in a list
[
    (1, 2),
    # # fmt: off
    # (3,
    #    4),
    # # fmt: on
    (5, 6),
]

# Test case 2: From RemiCardona's comment - commented-out directive in an if block
if False:
    # fmt: off # some other comment
    pass

# Test case 3: Ensure actual fmt directives still work (from PR #4811)
# fmt: off
#nospace
# twospaces
# fmt: on

# Test case 4: Mix of commented and uncommented directives
def example():
    # This should be formatted normally
    x = 1

    # # fmt: off - this is just a comment about fmt, not a directive
    y = 2

    # fmt: off
    # This should NOT be formatted
    z     =     3
    # fmt: on

    # Back to normal formatting
    w = 4
```

**Step 2: Run Black on the test file to verify it fails**

Run: `python -m black tests/data/cases/fmtonoff_commented.py --check`

Expected: INTERNAL ERROR about producing different code on second pass

**Step 3: Commit the failing test**

```bash
git add tests/data/cases/fmtonoff_commented.py
git commit -m "test: add failing test for commented-out fmt directives

Reproduces issue #4841 where commented-out fmt directives like
'# # fmt: off' cause Black to crash with an internal error."
```

---

## Task 2: Fix `_contains_fmt_directive()` Function

**Files:**
- Modify: `src/black/comments.py:708-738` (the `_contains_fmt_directive` function)

**Step 1: Understand the current implementation**

Read the current `_contains_fmt_directive` function to understand how it works:

```python
def _contains_fmt_directive(
    comment_line: str, directives: set[str] = FMT_OFF | FMT_ON | FMT_SKIP
) -> bool:
    """Check if a comment line contains a fmt directive."""
    semantic_comment_blocks = [
        comment_line,
        *[
            _COMMENT_PREFIX + comment.strip()
            for comment in comment_line.split(_COMMENT_PREFIX)[1:]
        ],
        *[
            _COMMENT_PREFIX + comment.strip()
            for comment in comment_line.strip(_COMMENT_PREFIX).split(
                _COMMENT_LIST_SEPARATOR
            )
        ],
    ]
    return any(comment in directives for comment in semantic_comment_blocks)
```

The problem: When processing `# # fmt: off`, the second list comprehension splits by `_COMMENT_PREFIX` and creates `['', 'fmt: off']`, which becomes `['# ', '# fmt: off']` after prefixing. This incorrectly matches the directive.

**Step 2: Write unit test for the fix**

Add a test function in `tests/test_comments.py` (or create it if it doesn't exist) to test `_contains_fmt_directive` directly:

```python
def test_contains_fmt_directive_ignores_commented_out_directives():
    """Test that commented-out fmt directives are not recognized."""
    from black.comments import _contains_fmt_directive, FMT_OFF, FMT_ON

    # These should be recognized as directives
    assert _contains_fmt_directive("# fmt: off", FMT_OFF)
    assert _contains_fmt_directive("#fmt:off", FMT_OFF)
    assert _contains_fmt_directive("# fmt: on", FMT_ON)
    assert _contains_fmt_directive("#    fmt: off", FMT_OFF)

    # These should NOT be recognized (commented-out directives)
    assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("## fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("# some text # fmt: off", FMT_OFF)
    assert not _contains_fmt_directive("# This is about fmt: off", FMT_OFF)

    # This SHOULD be recognized (trailing comment is OK)
    assert _contains_fmt_directive("# fmt: off # some other comment", FMT_OFF)
```

**Step 3: Run the unit test to verify it fails**

Run: `python -m pytest tests/test_comments.py::test_contains_fmt_directive_ignores_commented_out_directives -v`

Expected: FAIL showing that commented-out directives are incorrectly detected

**Step 4: Implement the fix**

Replace the `_contains_fmt_directive` function in `src/black/comments.py`:

```python
def _contains_fmt_directive(
    comment_line: str, directives: set[str] = FMT_OFF | FMT_ON | FMT_SKIP
) -> bool:
    """Check if a comment line contains a fmt directive.

    Only recognizes directives that appear at the start of the comment content,
    not nested within the comment (e.g., '# # fmt: off' is ignored).
    """
    # Strip leading comment prefix and whitespace to get the comment content
    content = comment_line.lstrip(_COMMENT_PREFIX).lstrip()

    # Check if any directive appears at the start of the content
    for directive in directives:
        directive_text = directive.lstrip(_COMMENT_PREFIX).lstrip()
        if content.startswith(directive_text):
            # Found a directive at the start - could have trailing comment
            return True

    # Also check the original multi-style comment handling, but only for
    # directives that appear as complete semantic blocks (not substrings)
    semantic_comment_blocks = [
        comment_line,
        *[
            _COMMENT_PREFIX + comment.strip()
            for comment in comment_line.strip(_COMMENT_PREFIX).split(
                _COMMENT_LIST_SEPARATOR
            )
        ],
    ]

    # Only match exact directives, not substrings
    return any(comment in directives for comment in semantic_comment_blocks)
```

**Step 5: Run the unit test to verify it passes**

Run: `python -m pytest tests/test_comments.py::test_contains_fmt_directive_ignores_commented_out_directives -v`

Expected: PASS

**Step 6: Run Black on the failing test file to verify the crash is fixed**

Run: `python -m black tests/data/cases/fmtonoff_commented.py --check`

Expected: Success (no internal error)

**Step 7: Commit the fix**

```bash
git add src/black/comments.py tests/test_comments.py
git commit -m "fix: prevent commented-out fmt directives from being recognized

Fixes #4841 where commented-out fmt directives like '# # fmt: off'
were incorrectly recognized as valid directives, causing Black to
crash with an internal error.

The fix modifies _contains_fmt_directive() to only recognize
directives that appear at the start of the comment content, not
nested within it."
```

---

## Task 3: Run Full Test Suite and Verify PR #4811 Still Works

**Files:**
- Verify: `tests/data/cases/fmtonoff.py` (tests from PR #4811)
- Verify: `tests/data/cases/fmtskip7.py` (tests from PR #4811)

**Step 1: Run the full test suite**

Run: `python -m pytest tests/ -v`

Expected: All tests pass, including the original tests from PR #4811

**Step 2: Specifically verify PR #4811 test cases**

Run: `python -m black tests/data/cases/fmtonoff.py --check`

Expected: No changes needed (file is already formatted correctly)

**Step 3: Run Black on fmtskip7.py**

Run: `python -m black tests/data/cases/fmtskip7.py --check`

Expected: No changes needed

**Step 4: Manually verify the key scenarios from PR #4811**

Create a temporary test file with the scenarios from PR #4811:

```python
# /tmp/test_pr_4811.py
def example():
    # fmt: off
    # This comment should not be reformatted
    #nospace
    # twospaces
    # fmt: on
    pass

def another():
    # fmt: off
    # First block
    # fmt: on

    x = 1  # This should be formatted

    # fmt: off
    # Second block
    # fmt: on
```

Run: `python -m black /tmp/test_pr_4811.py`

Expected: No changes to the commented sections within fmt:off/on blocks

**Step 5: Verify the new test file is formatted correctly**

Run: `python -m black tests/data/cases/fmtonoff_commented.py --diff`

Expected: Shows the expected formatting (commented-out directives are treated as regular comments)

---

## Task 4: Add Integration Test to Black's Test Suite

**Files:**
- Modify: `tests/test_black.py` or appropriate test file

**Step 1: Find where fmtonoff tests are run**

Search for how `fmtonoff.py` test cases are executed:

Run: `grep -r "fmtonoff" tests/`

Expected: Find the test that runs the case files

**Step 2: Ensure fmtonoff_commented.py is included**

If case files are auto-discovered, verify that our new test file will be picked up. If they're explicitly listed, add `fmtonoff_commented.py` to the list.

**Step 3: Run the specific test**

Run: `python -m pytest tests/test_black.py -k fmtonoff -v`

Expected: All fmtonoff tests pass, including our new commented directive test

**Step 4: Commit the integration**

```bash
git add tests/test_black.py  # if modified
git commit -m "test: integrate commented fmt directive test into suite"
```

---

## Task 5: Add Changelog Entry

**Files:**
- Modify: `CHANGES.md`

**Step 1: Add entry to CHANGES.md**

Add an entry under the "## Unreleased" section in the "### Stable style" or "### Bug fixes" section:

```markdown
### Bug fixes

- Fixed a crash when Black encounters commented-out fmt directives (e.g., `# # fmt: off`)
  within code. These are now correctly treated as regular comments rather than formatting
  directives. (#4841)
```

**Step 2: Review the change**

Run: `git diff CHANGES.md`

Expected: Shows the added changelog entry

**Step 3: Commit the changelog**

```bash
git add CHANGES.md
git commit -m "docs: add changelog entry for issue #4841 fix"
```

---

## Task 6: Final Verification and Cleanup

**Files:**
- Verify: All modified files

**Step 1: Run the full test suite one final time**

Run: `python -m pytest tests/ -v`

Expected: All tests pass (408+ tests)

**Step 2: Run Black on the entire codebase**

Run: `python -m black src/ tests/ --check`

Expected: No formatting issues

**Step 3: Verify git status is clean**

Run: `git status`

Expected: Clean working directory, all changes committed

**Step 4: Review all commits**

Run: `git log --oneline origin/main..HEAD`

Expected: Shows 4-5 commits with clear messages about the fix

**Step 5: Create a summary of what was fixed**

Document the fix:
- Bug: `_contains_fmt_directive()` incorrectly identified commented-out fmt directives
- Root cause: String splitting created substring matches
- Fix: Only recognize directives at the start of comment content
- Tests: Added comprehensive test cases for commented-out directives
- Verification: All PR #4811 tests still pass

---

## Success Criteria

- [ ] Black no longer crashes on `# # fmt: off` patterns
- [ ] Black no longer crashes on `# fmt: off # trailing comment` patterns
- [ ] All original PR #4811 test cases still pass
- [ ] Comment-only fmt:off/on blocks still work correctly (PR #4811 functionality)
- [ ] All 408+ tests pass
- [ ] Changelog entry added
- [ ] Code is properly committed with clear messages

## References

- Issue #4841: https://github.com/psf/black/issues/4841
- PR #4811: https://github.com/psf/black/pull/4811
- Original issue #1245: https://github.com/psf/black/issues/1245
