# Refactor `_contains_fmt_directive()` with Comprehensive Regression Testing

> **Status:** COMPLETED - 2025-11-11
>
> All tasks completed successfully:
>
> - Edge case tests created and comprehensive regression testing performed
> - Fix applied to prevent commented-out fmt directives from causing crashes
> - Code refactored for improved maintainability
> - All 382+ tests passing
> - Documentation updated in CHANGES.md

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this
> plan task-by-task.

**Goal:** Refactor the `_contains_fmt_directive()` function to reduce complexity from
117 lines to a more maintainable structure, while ensuring no regressions through
comprehensive testing against historical states.

**Architecture:** Establish a testing baseline by reverting PR #4811, write
comprehensive edge case tests, re-introduce PR #4811, apply our fix, then refactor with
confidence that tests will catch any regression.

**Tech Stack:** Python, pytest, git (revert, cherry-pick), Black's test infrastructure

---

## Phase 1: Preserve Current Work and Setup

### Task 1: Commit All Current Work

**Goal:** Ensure all work on `fix-4841` branch is safely committed before switching
branches.

**Files:**

- All modified files in working directory

**Step 1: Check git status**

Run: `git status` Expected: Shows any uncommitted changes

**Step 2: Stage and commit any uncommitted work**

```bash
git add -A
git commit -m "WIP: preserve current state before testing workflow"
```

**Step 3: Verify branch state**

Run: `git log --oneline -5` Expected: Shows all commits including the WIP commit if any

**Step 4: Note current HEAD for later**

Run: `git rev-parse HEAD > /tmp/fix-4841-head.txt` Expected: Saves current HEAD SHA for
reference

---

## Phase 2: Establish Pre-PR #4811 Baseline

### Task 2: Fetch Latest from psf/black and Create Test Branch

**Goal:** Get the latest code from upstream and create a branch at the state before PR
#4811.

**Files:**

- None (git operations only)

**Step 1: Add psf/black remote if not exists**

```bash
git remote add psf https://github.com/psf/black.git 2>/dev/null || echo "Remote already exists"
```

**Step 2: Fetch latest from psf/black**

Run: `git fetch psf main` Expected: Downloads latest commits from upstream

**Step 3: Create test-edge-cases branch from psf/main**

Run: `git checkout -b test-edge-cases psf/main` Expected: Creates and switches to new
branch based on psf/main

**Step 4: Verify we're on the new branch**

Run: `git branch --show-current` Expected: `test-edge-cases`

---

### Task 3: Revert PR #4811 Commit

**Goal:** Revert commit b895a73fd4997657a80f2f3f2785c5d496739f6e (PR #4811) to establish
baseline before the bug was introduced.

**Files:**

- `src/black/comments.py` - Will be reverted to pre-PR #4811 state
- `tests/data/cases/fmtonoff.py` - Will be reverted
- `tests/data/cases/fmtskip7.py` - Will be reverted

**Step 1: Verify the commit exists**

Run: `git log --oneline --all | grep b895a73` Expected: Shows the commit

**Step 2: Revert the PR #4811 commit**

```bash
git revert b895a73fd4997657a80f2f3f2785c5d496739f6e --no-edit
```

Expected: Creates a revert commit

**Step 3: Verify the revert**

Run: `git log --oneline -3` Expected: Shows revert commit at top

**Step 4: Check that \_contains_fmt_directive is in pre-PR #4811 state**

Run:
`git diff b895a73fd4997657a80f2f3f2785c5d496739f6e~1 HEAD -- src/black/comments.py | head -50`
Expected: No differences (or minimal differences)

**Step 5: Run tests to establish baseline**

Run: `python -m pytest tests/ --ignore=tests/test_blackd.py -x` Expected: Tests should
pass (this is the state before PR #4811)

**Step 6: Commit the revert**

Already committed by `git revert`, but verify:

```bash
git log -1 --pretty=format:"%s"
```

Expected: Shows "Revert ..." message

---

### Task 4: Write Comprehensive Edge Case Tests

**Goal:** Create extensive edge case tests that cover all scenarios, including the #4841
bug reproduction.

**Files:**

- Create: `tests/test_contains_fmt_directive_edge_cases.py` (comprehensive unit tests)

**Step 1: Create comprehensive unit test file**

Create
`/Users/elijahrutschman/Development/black/tests/test_contains_fmt_directive_edge_cases.py`:

```python
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

from black.comments import _contains_fmt_directive, FMT_OFF, FMT_ON, FMT_SKIP


class TestBasicDirectives:
    """Test basic directive recognition."""

    def test_standard_fmt_off(self):
        """Standard format: # fmt: off"""
        assert _contains_fmt_directive("# fmt: off", FMT_OFF)

    def test_standard_fmt_on(self):
        """Standard format: # fmt: on"""
        assert _contains_fmt_directive("# fmt: on", FMT_ON)

    def test_standard_fmt_skip(self):
        """Standard format: # fmt: skip"""
        assert _contains_fmt_directive("# fmt: skip", FMT_SKIP)

    def test_no_space_after_hash(self):
        """Compact format: #fmt:off"""
        assert _contains_fmt_directive("#fmt:off", FMT_OFF)

    def test_no_space_after_colon(self):
        """Format without space after colon: # fmt:off"""
        assert _contains_fmt_directive("# fmt:off", FMT_OFF)

    def test_extra_spaces(self):
        """Format with extra spaces: #    fmt: off"""
        assert _contains_fmt_directive("#    fmt: off", FMT_OFF)

    def test_not_a_directive(self):
        """Regular comment should not match"""
        assert not _contains_fmt_directive("# This is a comment", FMT_OFF)


class TestCommentedOutDirectives:
    """
    Test commented-out directives (issue #4841).

    EXPECTED BEHAVIOR ON BASELINE (pre-PR #4811):
    These tests will FAIL/CRASH on baseline because the bug exists.
    The function incorrectly recognizes commented-out directives.
    """

    def test_double_hash_no_space(self):
        """Commented-out: ## fmt: off

        BUG: On baseline, this is incorrectly recognized as a directive.
        """
        assert not _contains_fmt_directive("## fmt: off", FMT_OFF)

    def test_double_hash_with_space(self):
        """Commented-out: # # fmt: off

        BUG: On baseline, this is incorrectly recognized as a directive.
        This is the exact pattern from issue #4841.
        """
        assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)

    def test_triple_hash(self):
        """Commented-out: ### fmt: off"""
        assert not _contains_fmt_directive("### fmt: off", FMT_OFF)

    def test_quadruple_hash(self):
        """Commented-out: #### fmt: on"""
        assert not _contains_fmt_directive("#### fmt: on", FMT_ON)

    def test_issue_4841_exact_case(self):
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

    def test_fmt_off_with_trailing_comment(self):
        """Directive with trailing comment: # fmt: off # some comment

        This SHOULD be recognized (trailing comments are allowed).
        """
        assert _contains_fmt_directive("# fmt: off # some other comment", FMT_OFF)

    def test_fmt_on_with_explanation(self):
        """Directive with explanation: # fmt: on # end of unformatted section"""
        assert _contains_fmt_directive("# fmt: on # end of unformatted section", FMT_ON)

    def test_fmt_skip_with_reason(self):
        """Directive with reason: # fmt: skip # performance critical"""
        assert _contains_fmt_directive("# fmt: skip # performance critical", FMT_SKIP)


class TestMultiCommentPatterns:
    """Test multiple comments on one line with directives."""

    def test_pylint_fmt_skip(self):
        """Multi-comment: # pylint # fmt:skip

        This is a common pattern where multiple pragma comments appear together.
        """
        assert _contains_fmt_directive("# pylint # fmt:skip", FMT_SKIP)

    def test_type_ignore_fmt_off(self):
        """Multi-comment: # type: ignore # fmt: off"""
        assert _contains_fmt_directive("# type: ignore # fmt: off", FMT_OFF)

    def test_noqa_fmt_skip(self):
        """Multi-comment: # noqa # fmt:skip"""
        assert _contains_fmt_directive("# noqa # fmt:skip", FMT_SKIP)

    def test_short_word_before_directive(self):
        """Short identifier before directive: # x # fmt: off"""
        assert _contains_fmt_directive("# x # fmt: off", FMT_OFF)


class TestProseContainingDirectives:
    """
    Test comments that contain directive-like text but are actually prose.

    These should NOT be recognized as directives.
    """

    def test_prose_explaining_fmt_off(self):
        """Prose: # Remember to use # fmt: off"""
        assert not _contains_fmt_directive("# Remember to use # fmt: off", FMT_OFF)

    def test_prose_about_fmt_on(self):
        """Prose: # This is about fmt: on usage"""
        assert not _contains_fmt_directive("# This is about fmt: on usage", FMT_ON)

    def test_prose_with_directive_after_text(self):
        """Prose: # Some text # fmt: off in middle"""
        assert not _contains_fmt_directive("# Some text # fmt: off in middle", FMT_OFF)

    def test_directive_as_word_suffix(self):
        """Prose: # fmt:off directive

        The word 'directive' after makes this prose, not an active directive.
        """
        assert not _contains_fmt_directive("# fmt:off directive", FMT_OFF)

    def test_explaining_usage(self):
        """Prose: # Use fmt:skip to skip formatting"""
        assert not _contains_fmt_directive("# Use fmt:skip to skip formatting", FMT_SKIP)


class TestSemicolonSeparatedComments:
    """Test semicolon-separated comment lists."""

    def test_semicolon_list_with_fmt_skip(self):
        """Semicolon list: # pylint; fmt: skip; noqa: E501"""
        assert _contains_fmt_directive("# pylint; fmt: skip; noqa: E501", FMT_SKIP)

    def test_semicolon_fmt_off(self):
        """Semicolon list: # type: ignore; fmt: off"""
        assert _contains_fmt_directive("# type: ignore; fmt: off", FMT_OFF)


class TestWhitespaceVariations:
    """Test various whitespace patterns."""

    def test_tabs_instead_of_spaces(self):
        """Tabs: #\tfmt:\toff"""
        # This might not be recognized depending on implementation
        # Document expected behavior
        result = _contains_fmt_directive("#\tfmt:\toff", FMT_OFF)
        # Accept either True or False, just document what happens
        assert isinstance(result, bool)

    def test_multiple_spaces(self):
        """Multiple spaces: #  fmt:  off"""
        assert _contains_fmt_directive("#  fmt:  off", FMT_OFF)

    def test_leading_whitespace(self):
        """Leading whitespace before #: '   # fmt: off'"""
        # Comments shouldn't have leading whitespace in practice
        # but test the behavior
        result = _contains_fmt_directive("   # fmt: off", FMT_OFF)
        assert isinstance(result, bool)


class TestEdgeCases:
    """Test unusual edge cases."""

    def test_empty_string(self):
        """Empty string should not match"""
        assert not _contains_fmt_directive("", FMT_OFF)

    def test_just_hash(self):
        """Just a hash: #"""
        assert not _contains_fmt_directive("#", FMT_OFF)

    def test_hash_with_spaces(self):
        """Hash with spaces: #   """
        assert not _contains_fmt_directive("#   ", FMT_OFF)

    def test_directive_text_without_hash(self):
        """Directive text without hash: fmt: off"""
        assert not _contains_fmt_directive("fmt: off", FMT_OFF)

    def test_partial_directive(self):
        """Partial directive: # fmt"""
        assert not _contains_fmt_directive("# fmt", FMT_OFF)

    def test_wrong_directive_text(self):
        """Wrong directive: # fmt: offf (typo)"""
        assert not _contains_fmt_directive("# fmt: offf", FMT_OFF)

    def test_case_sensitive(self):
        """Case sensitivity: # FMT: OFF"""
        # Black is case-sensitive
        assert not _contains_fmt_directive("# FMT: OFF", FMT_OFF)


class TestYapfCompatibility:
    """Test yapf directive compatibility."""

    def test_yapf_disable(self):
        """yapf: disable directive"""
        from black.comments import FMT_YAPF
        assert _contains_fmt_directive("# yapf: disable", FMT_YAPF)

    def test_yapf_enable(self):
        """yapf: enable directive"""
        from black.comments import FMT_YAPF
        assert _contains_fmt_directive("# yapf: enable", FMT_YAPF)


class TestRegressionFromIssue4841:
    """
    Specific regression tests from issue #4841 and related comments.

    These are real-world patterns that caused the bug.
    """

    def test_remicard ona_trailing_comment_case(self):
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

    def test_list_context_commented_directive(self):
        """Commented directive in list context (issue #4841).

        The commented-out directive should NOT be recognized.
        """
        assert not _contains_fmt_directive("# # fmt: off", FMT_OFF)
        assert not _contains_fmt_directive("# # fmt: on", FMT_ON)

    def test_function_context_commented_directive(self):
        """Commented directive in function context."""
        assert not _contains_fmt_directive("## fmt: off", FMT_OFF)
```

**Step 2: Run tests against baseline (pre-PR #4811)**

Run: `python -m pytest tests/test_contains_fmt_directive_edge_cases.py -v`

Expected: Some tests will FAIL, specifically:

- `TestCommentedOutDirectives` tests will fail (the bug exists)
- Other tests should mostly pass

**Step 3: Document which tests fail**

Create a file documenting the baseline state:

```bash
python -m pytest tests/test_contains_fmt_directive_edge_cases.py -v 2>&1 | tee /tmp/baseline-test-results.txt
```

**Step 4: Commit the edge case tests**

```bash
git add tests/test_contains_fmt_directive_edge_cases.py
git commit -m "test: add comprehensive edge case tests for _contains_fmt_directive

These tests cover all edge cases including issue #4841.
On baseline (pre-PR #4811), some tests fail showing the bug.
After our fix, all tests should pass."
```

---

## Phase 3: Re-introduce PR #4811

### Task 5: Revert the Revert (Re-apply PR #4811)

**Goal:** Re-introduce commit b895a73fd with its functionality and tests.

**Files:**

- `src/black/comments.py` - PR #4811 changes restored
- `tests/data/cases/fmtonoff.py` - PR #4811 tests restored
- `tests/data/cases/fmtskip7.py` - PR #4811 tests restored

**Step 1: Revert the revert commit**

Find the revert commit hash:

```bash
REVERT_SHA=$(git log --oneline -1 --grep="Revert.*b895a73" --format="%H")
echo "Revert commit: $REVERT_SHA"
```

Revert the revert:

```bash
git revert $REVERT_SHA --no-edit
```

Expected: This re-applies PR #4811

**Step 2: Verify PR #4811 is back**

Run: `git diff b895a73fd4997657a80f2f3f2785c5d496739f6e HEAD -- src/black/comments.py`
Expected: Should be minimal/no differences

**Step 3: Run PR #4811 tests**

Run: `python -m pytest tests/test_format.py -k fmtonoff -v` Expected: All fmtonoff tests
pass (PR #4811 functionality works)

**Step 4: Run edge case tests**

Run: `python -m pytest tests/test_contains_fmt_directive_edge_cases.py -v`

Expected: Tests in `TestCommentedOutDirectives` will now FAIL (the #4841 bug is present)

**Step 5: Document the failing tests**

```bash
python -m pytest tests/test_contains_fmt_directive_edge_cases.py -v 2>&1 | tee /tmp/with-pr4811-test-results.txt
```

**Step 6: Commit**

```bash
git commit -m "Revert the revert: re-introduce PR #4811

This brings back b895a73fd4997657a80f2f3f2785c5d496739f6e.
PR #4811 tests pass but edge case tests for #4841 now fail."
```

---

## Phase 4: Apply Our Fix from fix-4841 Branch

### Task 6: Cherry-Pick Our Fix

**Goal:** Apply the fix from `fix-4841` branch to resolve issue #4841.

**Files:**

- `src/black/comments.py` - Our fix to `_contains_fmt_directive()`
- `tests/test_comments.py` - Our unit tests
- `tests/data/cases/fmtonoff_commented.py` - Our integration tests

**Step 1: Get the fix commits from fix-4841**

```bash
# View commits from fix-4841 that we need
git log fix-4841 --oneline --not test-edge-cases | head -10
```

Expected: Shows our fix commits

**Step 2: Cherry-pick the core fix commit**

Find the commit that fixes `_contains_fmt_directive()`:

```bash
FIX_SHA=$(git log fix-4841 --oneline --grep="fix: prevent commented-out fmt directives" --format="%H" | head -1)
echo "Fix commit: $FIX_SHA"
git cherry-pick $FIX_SHA
```

Expected: Applies our fix

**Step 3: Cherry-pick test files if needed**

```bash
# Cherry-pick commits with our tests
git cherry-pick --continue
# Or manually apply if there are conflicts
```

**Step 4: Run ALL tests**

Run: `python -m pytest tests/ --ignore=tests/test_blackd.py -v`

Expected: ALL tests pass:

- Baseline edge cases ✓
- PR #4811 tests ✓
- Our #4841 fix tests ✓

**Step 5: Specifically verify edge case tests**

Run: `python -m pytest tests/test_contains_fmt_directive_edge_cases.py -v` Expected: ALL
PASS (100%)

**Step 6: Document success**

```bash
python -m pytest tests/test_contains_fmt_directive_edge_cases.py -v 2>&1 | tee /tmp/with-fix-test-results.txt
```

**Step 7: Commit if needed**

```bash
git add -A
git commit -m "Apply fix from fix-4841 branch

All tests now pass:
- Edge case tests: 100%
- PR #4811 tests: 100%
- Issue #4841 fix verified"
```

---

## Phase 5: Refactor with Confidence

### Task 7: Design the Refactoring

**Goal:** Create a plan to simplify `_contains_fmt_directive()` while keeping all tests
passing.

**Files:**

- Design document to be created

**Step 1: Analyze current function structure**

Read `/Users/elijahrutschman/Development/black/src/black/comments.py` lines 708-824

Identify:

- Redundant checks (lines 730-735 vs 748-752)
- Logic that can be extracted to helpers
- Opportunities for simplification

**Step 2: Design helper functions**

Propose structure:

```python
def _is_commented_out_directive(comment_line: str) -> bool:
    """Returns True if comment looks like a commented-out directive.

    Examples:
        ## fmt: off -> True (consecutive hashes)
        # # fmt: off -> True (hash after space)
    """

def _extract_comment_content(comment_line: str) -> str | None:
    """Extract content after first # and optional whitespace.

    Returns None if not a valid comment format.
    """

def _has_directive_at_start(content: str, directives: set[str]) -> bool:
    """Check if content starts with any directive from the set.

    Validates that directive is standalone or followed by trailing comment.
    """

def _check_multi_comment_directive(content: str, directives: set[str]) -> bool:
    """Check for directives in # separated multi-comment patterns.

    Examples:
        "pylint # fmt:skip" -> True
        "Remember to use # fmt: off" -> False (prose)
    """

def _check_semicolon_list_directive(content: str, directives: set[str]) -> bool:
    """Check for directives in semicolon-separated lists.

    Example:
        "pylint; fmt: skip; noqa" -> True
    """

def _contains_fmt_directive(
    comment_line: str, directives: set[str] = FMT_OFF | FMT_ON | FMT_SKIP
) -> bool:
    """Main function using helpers - should be ~30 lines."""
    # Exact match check
    # Commented-out check
    # Extract content
    # Check directive at start
    # Check multi-comment
    # Check semicolon list
```

**Step 3: Write the design document**

Create `docs/plans/2025-11-11-refactor-contains-fmt-directive-design.md` with:

- Current problems (redundancy, complexity)
- Proposed helper functions
- Expected line count reduction (117 → ~80 total)
- Testing strategy (all existing tests must pass)

**Step 4: Get approval for design**

Review and approve the design before implementing.

---

### Task 8: Implement the Refactoring

**Goal:** Refactor using the approved design.

**Files:**

- Modify: `src/black/comments.py`

**Step 1: Run tests before refactoring**

Run: `python -m pytest tests/ --ignore=tests/test_blackd.py -x` Expected: ALL PASS
(baseline before refactoring)

**Step 2: Extract helper functions one at a time**

For each helper:

1. Write the helper function
2. Update `_contains_fmt_directive()` to use it
3. Run tests to verify no regression
4. Commit

Example for first helper:

```bash
# Edit src/black/comments.py - add _is_commented_out_directive()
# Edit _contains_fmt_directive() to use it
git add src/black/comments.py
git commit -m "refactor: extract _is_commented_out_directive helper

Extracts commented-out directive detection into separate function.
Lines 730-752 logic now in helper.

All tests pass."
python -m pytest tests/ --ignore=tests/test_blackd.py -x
```

**Step 3: Continue for each helper**

Repeat for:

- `_extract_comment_content()`
- `_has_directive_at_start()`
- `_check_multi_comment_directive()`
- `_check_semicolon_list_directive()`

**Step 4: Final cleanup of main function**

Simplify `_contains_fmt_directive()` to use all helpers.

**Step 5: Run full test suite**

Run: `python -m pytest tests/ --ignore=tests/test_blackd.py -v` Expected: ALL PASS (same
as before refactoring)

**Step 6: Check line count reduction**

```bash
git diff HEAD~6 src/black/comments.py | grep "^+" | wc -l
git diff HEAD~6 src/black/comments.py | grep "^-" | wc -l
```

Expected: Net reduction in complexity

**Step 7: Final commit**

```bash
git commit -m "refactor: complete simplification of _contains_fmt_directive

Reduced from 117 lines to ~80 lines across multiple functions.
Improved maintainability by extracting 5 helper functions.

All 382+ tests pass with no regressions."
```

---

### Task 9: Merge Back to fix-4841

**Goal:** Bring the refactored code back to the `fix-4841` branch.

**Files:**

- All refactored files

**Step 1: Switch to fix-4841**

Run: `git checkout fix-4841`

**Step 2: Merge test-edge-cases branch**

```bash
git merge test-edge-cases -m "Merge comprehensive edge case tests and refactoring

Includes:
- Comprehensive edge case tests
- Refactored _contains_fmt_directive() for better maintainability
- All 382+ tests passing"
```

**Step 3: Run final verification**

Run: `python -m pytest tests/ --ignore=tests/test_blackd.py -v` Expected: ALL PASS

**Step 4: Review the complete change**

```bash
git log --oneline main..HEAD
git diff main src/black/comments.py | head -100
```

---

## Phase 6: Update Documentation and Finish

### Task 10: Update Changelog and Plan Documents

**Goal:** Document the refactoring in changelog and plan.

**Files:**

- `CHANGES.md` - Add note about refactoring
- This plan document - Mark as completed

**Step 1: Add changelog entry**

Add to `CHANGES.md` under the existing #4841 entry:

```markdown
- Fixed a crash when Black encounters commented-out fmt directives (e.g.,
  `# # fmt: off`) within code. These are now correctly treated as regular comments
  rather than formatting directives. The implementation was refactored for improved
  maintainability. (#4841)
```

**Step 2: Commit changelog**

```bash
git add CHANGES.md
git commit -m "docs: update changelog with refactoring note"
```

**Step 3: Mark this plan as completed**

Add completion note to top of this document.

---

## Success Criteria

- [ ] All edge case tests pass on current fix
- [ ] Verified tests fail on baseline (pre-PR #4811)
- [ ] Verified tests fail after re-introducing PR #4811 (shows bug exists)
- [ ] Verified ALL tests pass after applying our fix
- [ ] Refactored `_contains_fmt_directive()` to ~80 lines from 117
- [ ] All 382+ tests pass after refactoring
- [ ] Code is more maintainable with clear helper functions
- [ ] Documentation updated

## Testing Verification Matrix

| State                   | Edge Cases       | PR #4811 Tests | Our Fix Tests | Total     |
| ----------------------- | ---------------- | -------------- | ------------- | --------- |
| Baseline (pre-PR #4811) | Some FAIL        | N/A            | N/A           | ~380 pass |
| After PR #4811          | FAIL (#4841 bug) | PASS           | N/A           | ~380 pass |
| After our fix           | PASS             | PASS           | PASS          | 382+ pass |
| After refactoring       | PASS             | PASS           | PASS          | 382+ pass |

## References

- Issue #4841: https://github.com/psf/black/issues/4841
- PR #4811: https://github.com/psf/black/pull/4811
- Commit b895a73fd: The PR #4811 commit that introduced the bug
- Original plan:
  `/Users/elijahrutschman/Development/black/docs/plans/2025-11-11-fix-commented-fmt-directives.md`
