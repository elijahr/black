# Test commented-out fmt directives that should NOT be treated as formatting directives
# These are regression tests for issue #4841

# Issue #4841: Commented-out fmt directives in a list
[
    (1, 2),
    # # fmt: off
    # (3,
    #    4),
    # # fmt: on
    (5, 6),
]


# Double hash at start (commented-out directive)
def double_hash():
    ## fmt: off
    x = 1 + 2
    ## fmt: on
    y = 3


# Comment about fmt directives (contains directive text but is commentary)
def commentary_about_fmt():
    # This is a comment explaining # fmt: off usage
    x = 1
    # Remember to use # fmt: on after # fmt: off
    y = 2


# Multiple hashes
def multiple_hashes():
    ### fmt: off
    a = 1
    #### fmt: on
    b = 2


# Directive in middle of comment
def directive_in_middle():
    # Some text then # fmt: off in middle
    x = 1
    # More text # fmt: on and more
    y = 2


# fmt: off
#nospace
# twospaces
   #threespaces
# fmt: on


# Mix of real and commented directives in same function
def mixed_directives():
    # This should be formatted normally
    x = 1

    # # fmt: off - just a comment, not a directive
    y = 2

    # fmt: off
    # This should NOT be formatted
    z     =     3
    # fmt: on

    # Back to normal formatting
    w = 4


# Nested in different contexts
class MyClass:
    # # fmt: off
    x = 1
    # # fmt: on
    y = 2


# In list comprehension context
result = [
    x
    for x in range(10)
    # # fmt: off
    # if x % 2 == 0
    # # fmt: on
]

# In dictionary
config = {
    "key": "value",
    # # fmt: off
    # "other": "value",
    # # fmt: on
}


# Edge case: directive-like text in string (should be formatted normally)
def strings_with_directive_text():
    comment = "# fmt: off"
    x = 1  # This comment has # fmt: off in it


# Edge case: commented code block with directives
# # def old_function():
# #     # fmt: off
# #     x  =  1
# #     # fmt: on
# #     return x


# Multiple commented directives in sequence
def multiple_commented():
    # # fmt: off
    # # fmt: on
    # # fmt: off
    x = 1


# Whitespace variations in commented directives
def whitespace_variations():
    ##fmt: off
    x = 1
    ## fmt:off
    y = 2
    ##  fmt: off
    z = 3


# Ensure actual directives preserve comment formatting (PR #4811)
def actual_directives_preserve_comments():
    # fmt: off
            #should not be formatted
    # fmt: on
    # fmt: off

        #should not be formatted

    # fmt: on
    pass


# File-level commented directives
# # fmt: off
x = 1
y = 2
# # fmt: on
z = 3


# Issue #4841: fmt: off with trailing comment causes infinite indentation
# This is a KNOWN BUG - currently fails with infinite indentation
if False:
    # fmt: off # some other comment
    pass


# output


# Test commented-out fmt directives that should NOT be treated as formatting directives
# These are regression tests for issue #4841

# Issue #4841: Commented-out fmt directives in a list
[
    (1, 2),
    # # fmt: off
    # (3,
    #    4),
    # # fmt: on
    (5, 6),
]


# Double hash at start (commented-out directive)
def double_hash():
    ## fmt: off
    x = 1 + 2
    ## fmt: on
    y = 3


# Comment about fmt directives (contains directive text but is commentary)
def commentary_about_fmt():
    # This is a comment explaining # fmt: off usage
    x = 1
    # Remember to use # fmt: on after # fmt: off
    y = 2


# Multiple hashes
def multiple_hashes():
    ### fmt: off
    a = 1
    #### fmt: on
    b = 2


# Directive in middle of comment
def directive_in_middle():
    # Some text then # fmt: off in middle
    x = 1
    # More text # fmt: on and more
    y = 2


# fmt: off
#nospace
# twospaces
   #threespaces
# fmt: on


# Mix of real and commented directives in same function
def mixed_directives():
    # This should be formatted normally
    x = 1

    # # fmt: off - just a comment, not a directive
    y = 2

    # fmt: off
    # This should NOT be formatted
    z     =     3
    # fmt: on

    # Back to normal formatting
    w = 4


# Nested in different contexts
class MyClass:
    # # fmt: off
    x = 1
    # # fmt: on
    y = 2


# In list comprehension context
result = [
    x
    for x in range(10)
    # # fmt: off
    # if x % 2 == 0
    # # fmt: on
]

# In dictionary
config = {
    "key": "value",
    # # fmt: off
    # "other": "value",
    # # fmt: on
}


# Edge case: directive-like text in string (should be formatted normally)
def strings_with_directive_text():
    comment = "# fmt: off"
    x = 1  # This comment has # fmt: off in it


# Edge case: commented code block with directives
# # def old_function():
# #     # fmt: off
# #     x  =  1
# #     # fmt: on
# #     return x


# Multiple commented directives in sequence
def multiple_commented():
    # # fmt: off
    # # fmt: on
    # # fmt: off
    x = 1


# Whitespace variations in commented directives
def whitespace_variations():
    ##fmt: off
    x = 1
    ## fmt:off
    y = 2
    ##  fmt: off
    z = 3


# Ensure actual directives preserve comment formatting (PR #4811)
def actual_directives_preserve_comments():
    # fmt: off
            #should not be formatted
    # fmt: on
    # fmt: off

        #should not be formatted

    # fmt: on
    pass


# File-level commented directives
# # fmt: off
x = 1
y = 2
# # fmt: on
z = 3


# Issue #4841: fmt: off with trailing comment causes infinite indentation
# This is a KNOWN BUG - currently fails with infinite indentation
if False:
    # fmt: off # some other comment
    pass
