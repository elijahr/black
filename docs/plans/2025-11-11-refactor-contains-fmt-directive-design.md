# Refactoring Design: \_contains_fmt_directive Function

## Executive Summary

**Current State:** The `_contains_fmt_directive` function (lines 708-824 in
`src/black/comments.py`) is 117 lines long with significant complexity and redundancy.

**Proposed State:** Refactor into a main orchestrator function (~25 lines) with 4-5
focused helper functions, reducing total line count to ~85-95 lines while improving
readability, testability, and maintainability.

**Expected Benefits:**

- 22-32 line reduction (19-27% decrease)
- Improved code clarity and separation of concerns
- Better testability with isolated helper functions
- Reduced cognitive complexity
- Easier maintenance and future enhancements

---

## Current Function Analysis

### Overview

The `_contains_fmt_directive` function checks if a comment line contains Black
formatting directives (e.g., `# fmt: off`, `# fmt: on`, `# fmt: skip`,
`# yapf: disable/enable`).

**Location:** `src/black/comments.py`, lines 708-824 **Length:** 117 lines (including
docstring) **Cyclomatic Complexity:** High (multiple nested conditionals, early returns,
and branching logic)

### Current Structure

```
_contains_fmt_directive (117 lines)
├── Docstring (18 lines)
├── Exact match check (2 lines)
├── Commented-out directive detection (4 lines)
├── Comment prefix extraction (9 lines)
├── Secondary commented-out check (4 lines)
├── Content whitespace normalization (2 lines)
├── Directive prefix matching (19 lines)
├── Multi-comment pattern handling with '#' (28 lines)
└── Semicolon-separated pattern handling (5 lines)
```

### Key Responsibilities

The function handles 7 distinct concerns:

1. **Exact Directive Matching** (lines 726-728)
   - Quick check if input exactly matches a known directive

2. **Commented-Out Detection via Hash Counting** (lines 730-735)
   - Detects patterns like `## fmt: off` by counting consecutive `#` at start

3. **Comment Prefix Extraction** (lines 737-746)
   - Strips the leading `# ` or `#` to get comment content
   - Handles both standard (`# `) and compact (`#`) formats

4. **Secondary Commented-Out Detection** (lines 748-752)
   - Catches patterns like `# # fmt: off` after initial prefix removal

5. **Directive Start Matching** (lines 757-778)
   - Checks if directive text appears at the start of content
   - Validates what comes after the directive (nothing, whitespace, or trailing comment)

6. **Multi-Comment Pattern Handling** (lines 789-815)
   - Handles patterns like `# pylint # fmt:skip`
   - Distinguishes between valid multi-directives and prose
   - Implements heuristics (word count, empty parts)

7. **Semicolon-Separated Lists** (lines 817-824)
   - Handles patterns like `# pylint; fmt: skip; noqa: E501`

### Identified Issues

#### 1. Redundant Commented-Out Checks

- **Line 732-735:** Hash counting check
- **Line 750-752:** Post-strip hash check
- **Line 793-795:** Empty first part check in multi-comment handling
- **Problem:** Three separate mechanisms checking for the same pattern

#### 2. Complex Multi-Comment Logic

- **Lines 789-815:** 27 lines handling `#`-separated patterns
- Contains multiple nested conditionals
- Mixes pattern detection with prose heuristics
- Difficult to test individual branches

#### 3. Duplicated Directive Matching

- **Lines 758-778:** Start-of-content matching with prefix extraction
- **Lines 804-815:** Reconstructed directive matching in multi-comment
- Similar logic implemented twice with slight variations

#### 4. Unclear Separation of Concerns

- Prose detection heuristic (line 799-801) embedded in multi-comment logic
- Trailing comment validation (lines 766-775) mixed with directive matching
- Makes it difficult to understand and modify individual behaviors

#### 5. Limited Testability

- Large monolithic function makes it hard to test edge cases
- Helper logic cannot be tested in isolation
- Difficult to add new directive patterns or matching rules

---

## Proposed Refactoring Design

### Architecture Overview

Transform the monolithic function into a composable system with clear separation of
concerns:

```
_contains_fmt_directive (main orchestrator, ~25 lines)
├── _is_commented_out_directive (helper, ~12 lines)
├── _extract_comment_content (helper, ~10 lines)
├── _matches_directive_at_start (helper, ~15 lines)
├── _extract_multi_comment_parts (helper, ~18 lines)
└── _is_valid_multi_comment_pattern (helper, ~12 lines)
```

**Total Estimated Lines:** ~92 lines (including docstrings) **Reduction:** ~25 lines
(21% decrease)

### Proposed Helper Functions

#### 1. `_is_commented_out_directive`

**Purpose:** Single source of truth for detecting commented-out directives **Estimated
Lines:** ~12 (with docstring)

**Responsibilities:**

- Check for consecutive `#` at start (`## fmt: off`)
- Check for `# #` patterns after whitespace (`# # fmt: off`)
- Consolidates all three current checks into one function

**Signature:**

```python
def _is_commented_out_directive(comment_line: str) -> bool:
    """
    Check if a comment line is a commented-out directive.

    Returns True for patterns like:
    - "## fmt: off" (consecutive hashes)
    - "# # fmt: off" (hash after space)
    - "### fmt: off" (multiple consecutive hashes)
    """
```

**Implementation Strategy:**

- Count consecutive `#` at start (if > 1, return True)
- Strip first `#` and leading whitespace, check if next char is `#`
- Early returns for efficiency

**Benefits:**

- Eliminates three redundant checks
- Single testable unit for commented-out detection
- Easy to add new commented-out patterns in future

---

#### 2. `_extract_comment_content`

**Purpose:** Normalize comment input and extract clean content **Estimated Lines:** ~10
(with docstring)

**Responsibilities:**

- Strip leading `# ` or `#` prefix
- Normalize whitespace
- Return None if not a valid comment format

**Signature:**

```python
def _extract_comment_content(comment_line: str) -> str | None:
    """
    Extract the content portion of a comment line.

    Handles:
    - "# fmt: off" -> "fmt: off"
    - "#fmt:off" -> "fmt:off"
    - "   # fmt: off" -> "fmt: off"
    - "not a comment" -> None
    """
```

**Implementation Strategy:**

- Handle both `# ` and `#` prefixes
- Strip and normalize whitespace
- Return None for invalid input

**Benefits:**

- Centralizes prefix handling logic
- Removes duplication between main function and multi-comment handling
- Easier to add support for new comment formats

---

#### 3. `_matches_directive_at_start`

**Purpose:** Check if a directive appears at the start of comment content **Estimated
Lines:** ~15 (with docstring)

**Responsibilities:**

- Check if directive text starts the content
- Validate what follows (nothing, whitespace, or `#` for trailing comment)
- Handle directive prefix variations

**Signature:**

```python
def _matches_directive_at_start(
    content: str,
    directive: str
) -> bool:
    """
    Check if a directive appears at the start of comment content.

    Valid patterns:
    - "fmt: off" (exact match)
    - "fmt: off " (trailing whitespace)
    - "fmt: off # comment" (trailing comment)

    Invalid patterns:
    - "fmt: off directive" (followed by word characters)
    - "some text fmt: off" (not at start)
    """
```

**Implementation Strategy:**

- Extract directive text (remove comment prefix if present)
- Check if content starts with directive text
- Validate what comes after the directive

**Benefits:**

- Removes duplication with multi-comment reconstruction logic
- Single place to define "valid directive" rules
- Easy to modify trailing comment rules

---

#### 4. `_extract_multi_comment_parts`

**Purpose:** Parse multi-comment patterns into individual parts **Estimated Lines:** ~18
(with docstring)

**Responsibilities:**

- Split on `#` separators
- Split on `;` separators
- Return normalized comment parts
- Filter out empty/invalid parts

**Signature:**

```python
def _extract_multi_comment_parts(content: str) -> list[str]:
    """
    Extract individual comment parts from multi-comment patterns.

    Handles:
    - "# pylint # fmt:skip" -> ["pylint", "fmt:skip"]
    - "# pylint; fmt: skip" -> ["pylint", "fmt: skip"]
    - "# # fmt: off" -> [] (empty first part indicates commented-out)
    """
```

**Implementation Strategy:**

- Try `#` split first, then `;` split
- Normalize each part (strip whitespace)
- Filter out empty parts in specific contexts
- Return list of clean comment parts

**Benefits:**

- Separates parsing logic from validation logic
- Easier to support new multi-comment separators
- Testable in isolation

---

#### 5. `_is_valid_multi_comment_pattern`

**Purpose:** Validate if multi-comment pattern is legitimate **Estimated Lines:** ~12
(with docstring)

**Responsibilities:**

- Check if first part indicates prose vs. directive
- Apply word count heuristics
- Detect commented-out patterns in multi-comment context

**Signature:**

```python
def _is_valid_multi_comment_pattern(parts: list[str]) -> bool:
    """
    Check if a multi-comment pattern is valid (not prose).

    Invalid patterns:
    - First part is empty (indicates "# # ..." commented-out)
    - First part has >2 words (indicates prose like "Remember to use")

    Valid patterns:
    - Short first part (1-2 words like "pylint", "type: ignore")
    - Single word identifiers
    """
```

**Implementation Strategy:**

- Check for empty first part
- Count words in first part
- Apply heuristics to distinguish directives from prose

**Benefits:**

- Isolates prose detection heuristics
- Easy to tune heuristics based on real-world feedback
- Testable with various prose examples

---

### Refactored Main Function Structure

```python
def _contains_fmt_directive(
    comment_line: str, directives: set[str] = FMT_OFF | FMT_ON | FMT_SKIP
) -> bool:
    """
    Checks if the given comment contains format directives, alone or paired with
    other comments.

    [Keep existing docstring examples]
    """
    # Quick check: exact match
    if comment_line in directives:
        return True

    # Check for commented-out directive patterns
    if _is_commented_out_directive(comment_line):
        return False

    # Extract clean comment content
    content = _extract_comment_content(comment_line)
    if content is None:
        return False

    # Check if directive appears at start of content
    for directive in directives:
        if _matches_directive_at_start(content, directive):
            return True

    # Check multi-comment patterns (# and ; separators)
    parts = _extract_multi_comment_parts(content)
    if not parts or not _is_valid_multi_comment_pattern(parts):
        return False

    # Check each part for exact directive matches
    for part in parts[1:]:  # Skip first part (already checked above)
        reconstructed = _COMMENT_PREFIX + part
        if reconstructed in directives:
            return True
        # Also check without space for compact formats
        reconstructed_compact = "#" + part
        if reconstructed_compact in directives:
            return True

    return False
```

**Estimated Lines:** ~25-30 (with docstring)

---

## Expected Improvements

### Quantitative Metrics

| Metric                  | Current | Proposed | Improvement             |
| ----------------------- | ------- | -------- | ----------------------- |
| Total Lines             | 117     | ~92      | -25 lines (-21%)        |
| Lines in Main Function  | 117     | ~28      | -89 lines (-76%)        |
| Cyclomatic Complexity   | ~15     | ~5       | -10 (-67%)              |
| Number of Functions     | 1       | 6        | +5 (better modularity)  |
| Testable Units          | 1       | 6        | +5 (better testability) |
| Maximum Function Length | 117     | ~18      | -99 lines (-85%)        |

### Qualitative Improvements

#### 1. Readability

- **Before:** Must read 117 lines to understand logic flow
- **After:** Main function provides high-level algorithm, helpers provide details
- **Benefit:** New contributors can understand the system faster

#### 2. Testability

- **Before:** One large integration test per behavior
- **After:** Each helper can be unit tested independently
- **Benefit:** Better test coverage, faster test execution, clearer test failures

#### 3. Maintainability

- **Before:** Changes require understanding entire 117-line function
- **After:** Changes are often isolated to a single helper function
- **Benefit:** Reduced risk of regression, easier code review

#### 4. Extensibility

- **Before:** Adding new directive patterns requires modifying complex logic
- **After:** Clear extension points (e.g., new separator in
  `_extract_multi_comment_parts`)
- **Benefit:** Easier to add features like new comment formats

#### 5. Debugging

- **Before:** Stack traces show one large function
- **After:** Stack traces show which helper failed
- **Benefit:** Faster root cause identification

---

## Testing Strategy

### Unit Tests for Helper Functions

#### 1. `_is_commented_out_directive`

**Test Cases:**

- Consecutive hashes: `## fmt: off`, `### fmt: on`
- Space-separated: `# # fmt: off`, `# ## fmt: skip`
- Valid single hash: `# fmt: off` (should return False)
- Edge cases: `#`, `##`, `# `, empty string

**Expected Test Count:** ~8 tests

---

#### 2. `_extract_comment_content`

**Test Cases:**

- Standard format: `# fmt: off` → `"fmt: off"`
- Compact format: `#fmt:off` → `"fmt:off"`
- Extra spaces: `#    fmt: off` → `"fmt: off"`
- No hash: `fmt: off` → `None`
- Leading whitespace: `   # fmt: off` → `"fmt: off"`
- Edge cases: `#`, empty string

**Expected Test Count:** ~8 tests

---

#### 3. `_matches_directive_at_start`

**Test Cases:**

- Exact match: `"fmt: off"` matches `"# fmt: off"`
- Trailing whitespace: `"fmt: off "` matches
- Trailing comment: `"fmt: off # comment"` matches
- Word after: `"fmt: off directive"` doesn't match
- Not at start: `"some fmt: off"` doesn't match
- Compact directive: `"fmt:off"` matches `"#fmt:off"`

**Expected Test Count:** ~10 tests

---

#### 4. `_extract_multi_comment_parts`

**Test Cases:**

- Hash separator: `"pylint # fmt:skip"` → `["pylint", "fmt:skip"]`
- Semicolon separator: `"pylint; fmt: skip"` → `["pylint", "fmt: skip"]`
- Empty first part: `"# fmt: off"` → `[]` (or appropriate handling)
- Multiple parts: `"a # b # c"` → `["a", "b", "c"]`
- Single part: `"fmt: off"` → `["fmt: off"]`

**Expected Test Count:** ~8 tests

---

#### 5. `_is_valid_multi_comment_pattern`

**Test Cases:**

- Valid short: `["pylint", "fmt:skip"]` → True
- Valid two words: `["type: ignore", "fmt: off"]` → True
- Invalid prose: `["Remember to use", "fmt: off"]` → False
- Invalid empty: `["", "fmt: off"]` → False
- Single part: `["fmt: off"]` → True

**Expected Test Count:** ~8 tests

---

### Integration Tests

#### Existing Test Suites

- **`tests/test_contains_fmt_directive_edge_cases.py`**: 291 lines, comprehensive edge
  cases
  - All existing tests must pass after refactoring
  - No behavioral changes expected

- **`tests/test_comments.py`**: 46 lines, basic functionality tests
  - All existing tests must pass
  - Tests actual directive recognition in various formats

#### New Integration Tests

- Add tests that verify helpers work correctly together
- Test complex real-world patterns from actual codebases
- Performance tests for regex-heavy operations

**Expected Test Count:** ~5 additional integration tests

---

### Test Execution Plan

1. **Before Refactoring:**
   - Run all existing tests, document baseline:
     `pytest tests/test_contains_fmt_directive_edge_cases.py tests/test_comments.py -v`
   - Ensure 100% pass rate

2. **During Refactoring:**
   - Create helper functions one at a time
   - Write unit tests for each helper before integrating
   - Run integration tests after each helper addition

3. **After Refactoring:**
   - Run full test suite: `pytest tests/`
   - Run Black on Black codebase: `black src/ tests/ --check`
   - Run Black on test data: `black tests/data/cases/fmtonoff*.py --check`
   - Performance comparison (if needed)

---

## Implementation Plan

### Phase 1: Preparation (No Code Changes)

**Duration:** 30 minutes

1. Run full test suite, document baseline results
2. Create feature branch: `git checkout -b refactor/contains-fmt-directive`
3. Document current function behavior with specific examples
4. Identify all call sites of `_contains_fmt_directive`

**Deliverable:** This design document, baseline test results

---

### Phase 2: Extract Helper Functions (Incremental)

**Duration:** 2-3 hours

#### Step 1: Extract `_is_commented_out_directive`

1. Write unit tests (TDD approach)
2. Implement helper function
3. Replace inline checks in main function
4. Run integration tests
5. Commit: "refactor: extract \_is_commented_out_directive helper"

#### Step 2: Extract `_extract_comment_content`

1. Write unit tests
2. Implement helper function
3. Replace inline logic in main function
4. Run integration tests
5. Commit: "refactor: extract \_extract_comment_content helper"

#### Step 3: Extract `_matches_directive_at_start`

1. Write unit tests
2. Implement helper function
3. Replace directive matching logic in main function
4. Run integration tests
5. Commit: "refactor: extract \_matches_directive_at_start helper"

#### Step 4: Extract `_extract_multi_comment_parts`

1. Write unit tests
2. Implement helper function
3. Replace multi-comment parsing in main function
4. Run integration tests
5. Commit: "refactor: extract \_extract_multi_comment_parts helper"

#### Step 5: Extract `_is_valid_multi_comment_pattern`

1. Write unit tests
2. Implement helper function
3. Replace prose detection heuristics in main function
4. Run integration tests
5. Commit: "refactor: extract \_is_valid_multi_comment_pattern helper"

**Deliverable:** 5 helper functions with unit tests, all integration tests passing

---

### Phase 3: Optimize Main Function

**Duration:** 1 hour

1. Simplify main function flow using helpers
2. Remove redundant logic now handled by helpers
3. Add inline comments explaining high-level algorithm
4. Run full test suite
5. Commit: "refactor: simplify \_contains_fmt_directive main function"

**Deliverable:** Cleaned up main function (~25 lines)

---

### Phase 4: Validation

**Duration:** 1 hour

1. Run full Black test suite: `pytest tests/ -v`
2. Run Black on Black: `black src/ tests/ --check`
3. Run Black on all test data: `black tests/data/ --check`
4. Compare performance (if needed): time before/after on large files
5. Code review (self or peer)
6. Update CHANGES.md if needed (for internal refactoring note)

**Deliverable:** Confidence that refactoring is safe and complete

---

### Phase 5: Documentation and Cleanup

**Duration:** 30 minutes

1. Update function docstrings
2. Add module-level comments explaining helper architecture
3. Update any developer documentation
4. Final commit: "docs: update comments for refactored \_contains_fmt_directive"
5. Create pull request (if applicable)

**Deliverable:** Complete, documented, tested refactoring

---

## Risk Assessment

### Low Risk Areas

- **Helper function extraction:** Each helper has clear inputs/outputs
- **Unit test creation:** Well-defined test cases from existing edge case tests
- **Documentation:** No user-facing changes

### Medium Risk Areas

- **Multi-comment pattern logic:** Complex parsing, easy to introduce bugs
  - **Mitigation:** Extract incrementally, run tests after each step

- **Trailing comment validation:** Subtle logic around what's valid after directive
  - **Mitigation:** Comprehensive unit tests for `_matches_directive_at_start`

### High Risk Areas

- **Prose detection heuristics:** Word count rules might not cover all cases
  - **Mitigation:** Keep existing heuristics unchanged, add tests documenting edge cases
  - **Fallback:** If issues arise, revert to more conservative detection

- **Commented-out detection:** Must catch all patterns to avoid #4841 regression
  - **Mitigation:** Existing comprehensive test suite in
    `test_contains_fmt_directive_edge_cases.py`
  - **Verification:** All 291 lines of edge case tests must pass

---

## Success Criteria

### Functional Requirements

- [ ] All existing tests pass (no behavioral changes)
- [ ] All edge cases from `test_contains_fmt_directive_edge_cases.py` still work
- [ ] Issue #4841 patterns still correctly identified as commented-out
- [ ] PR #4811 functionality (comment-only fmt blocks) still works

### Code Quality Requirements

- [ ] Main function reduced to ≤30 lines (from 117)
- [ ] No function exceeds 20 lines (excluding docstrings)
- [ ] All helpers have comprehensive unit tests (≥80% coverage)
- [ ] Docstrings updated and accurate

### Performance Requirements

- [ ] No measurable performance regression (±5% acceptable)
- [ ] Memory usage unchanged

### Documentation Requirements

- [ ] All helper functions have clear docstrings with examples
- [ ] Design decisions documented in code comments
- [ ] This design document updated with actual implementation results

---

## Future Enhancements

After this refactoring, the following enhancements become easier:

1. **Support for Custom Directives**
   - Add user-configurable directive patterns
   - Easy to extend `_matches_directive_at_start` with regex support

2. **Better Error Messages**
   - When a directive is malformed, helpers can return specific error info
   - Users could get hints like "Did you mean `# fmt: off` instead of `## fmt: off`?"

3. **Performance Optimization**
   - Cache directive matching results (helpers are pure functions)
   - Add fast-path for common patterns

4. **Enhanced Prose Detection**
   - Machine learning or NLP to detect prose vs. directives
   - Language-aware word counting

5. **Directive Context Awareness**
   - Check if directive appears in appropriate context (e.g., `skip` only on compound
     statements)
   - Already available via call site, but helpers make it easier to add validation

---

## Appendix A: Current Function Metrics

### Line-by-Line Breakdown

```
708-710: Function signature (3 lines)
711-725: Docstring (15 lines)
726-728: Exact match check (3 lines)
730-735: Commented-out check #1 - hash counting (6 lines)
737-746: Comment prefix extraction (10 lines)
748-752: Commented-out check #2 - post-strip (5 lines)
754-755: Content normalization (2 lines)
757-778: Directive start matching (22 lines)
780-815: Multi-comment pattern handling (36 lines)
817-824: Semicolon-separated handling (8 lines)
---
Total: 117 lines
```

### Complexity Metrics

- **Cyclomatic Complexity:** 15 (very high - threshold is 10)
- **Nesting Depth:** 4 levels (high)
- **Number of Branches:** 12+ (if/elif/else)
- **Number of Early Returns:** 4

### Dependencies

- **Constants Used:** `FMT_OFF`, `FMT_ON`, `FMT_SKIP`, `_COMMENT_PREFIX`,
  `_COMMENT_LIST_SEPARATOR`
- **Called From:**
  - Line 208: `is_fmt_off = _contains_fmt_directive(comment.value, FMT_OFF)`
  - Line 209: `is_fmt_skip = _contains_fmt_directive(comment.value, FMT_SKIP)`
  - Line 445: `if _contains_fmt_directive(comment.value, FMT_SKIP):`
- **Total Call Sites:** 3 in comments.py

---

## Appendix B: Test Coverage

### Current Test Files

#### 1. `tests/test_contains_fmt_directive_edge_cases.py` (291 lines)

**Classes and Methods:**

- `TestBasicDirectives` (7 tests)
- `TestCommentedOutDirectives` (6 tests) - Issue #4841 focus
- `TestDirectivesWithTrailingComments` (3 tests)
- `TestMultiCommentPatterns` (4 tests)
- `TestProseContainingDirectives` (5 tests)
- `TestSemicolonSeparatedComments` (2 tests)
- `TestWhitespaceVariations` (3 tests)
- `TestEdgeCases` (8 tests)
- `TestYapfCompatibility` (2 tests) - Note: Uses undefined FMT_YAPF
- `TestRegressionFromIssue4841` (3 tests)

**Total:** 43 test methods

#### 2. `tests/test_comments.py` (46 lines)

**Functions:**

- `test_contains_fmt_directive_ignores_commented_out_directives` (1 comprehensive test)

**Coverage:** Basic functionality + issue #4841 regression

### Proposed Additional Tests

After refactoring, add unit tests for each helper:

- `test_is_commented_out_directive` (~8 tests)
- `test_extract_comment_content` (~8 tests)
- `test_matches_directive_at_start` (~10 tests)
- `test_extract_multi_comment_parts` (~8 tests)
- `test_is_valid_multi_comment_pattern` (~8 tests)

**Total New Tests:** ~42 unit tests **Total Test Coverage:** 85+ tests for directive
recognition

---

## Appendix C: Performance Considerations

### Current Performance Profile

- **String Operations:** Heavy use of `split()`, `strip()`, `startswith()`
- **Iteration:** Loops over directive sets (max 3 items), split parts (typically 1-3)
- **Regex:** None currently (all string methods)
- **Expected Bottleneck:** Multi-file processing, but per-call time is negligible

### Refactoring Impact

- **Helper Function Call Overhead:** Minimal (Python function calls are fast)
- **Early Returns:** Preserved in refactored version, maintains fast-path
- **Memory:** No additional allocations (same intermediate strings)

### Optimization Opportunities (Future)

1. **Memoization:** `@lru_cache` on pure helpers like `_extract_comment_content`
2. **Compiled Regex:** For directive matching (if beneficial)
3. **Fast Path:** Common cases like `# fmt: off` could be hardcoded

**Recommendation:** Measure before optimizing; current performance likely sufficient

---

## Appendix D: Alternative Designs Considered

### Alternative 1: Regex-Based Approach

**Description:** Use a single comprehensive regex to match all valid directive patterns

**Pros:**

- Single regex could be more performant
- Declarative pattern matching
- Easier to visualize all valid patterns

**Cons:**

- Regex complexity would be very high (hard to read/maintain)
- Error messages and debugging harder
- Prose detection heuristics don't fit regex model
- Black generally avoids complex regex

**Decision:** Rejected - doesn't align with Black's code style, reduces readability

---

### Alternative 2: State Machine

**Description:** Parse comment character-by-character with state transitions

**Pros:**

- Clear state transitions
- Single pass through string
- Easy to extend with new states

**Cons:**

- Overkill for current complexity
- More code than current approach
- Harder to understand for contributors
- Not a common pattern in Black codebase

**Decision:** Rejected - too complex for the problem space

---

### Alternative 3: Visitor Pattern

**Description:** Parse comment into AST-like structure, visit nodes to detect directives

**Pros:**

- Very extensible
- Clean separation of parsing and validation
- Could support nested comments in future

**Cons:**

- Massive overkill for flat comment strings
- Would increase line count, not decrease
- Adds unnecessary abstraction

**Decision:** Rejected - over-engineering

---

### Alternative 4: Keep Monolithic, Just Refactor Internal Logic

**Description:** Improve current function without extracting helpers

**Pros:**

- Minimal risk (no API changes)
- Faster to implement
- No additional function call overhead

**Cons:**

- Doesn't improve testability
- Still hard to understand and maintain
- Doesn't reduce complexity metrics
- Limited future extensibility

**Decision:** Rejected - doesn't achieve goals of improving maintainability and
testability

---

### Chosen Approach: Helper Function Extraction

**Rationale:**

- Balances readability, testability, and maintainability
- Aligns with Black's existing code style
- Incremental implementation reduces risk
- Clear extension points for future features
- Achieves significant line count reduction
- Improves complexity metrics
