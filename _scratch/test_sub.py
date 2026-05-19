import re

# Simulate _flatten_for_frontmatter output: literal backslash + 'n'
flattened = "first" + chr(92) + "n" + "second"
print("flattened repr:", repr(flattened))
# Should be: 'first\\nsecond' i.e. backslash + 'n' between

r = re.sub(r"^foo:.*$", f"foo: {flattened}", "foo: bar", flags=re.M)
print("result repr:", repr(r))

# In the resulting string, is there a newline?
print("has newline:", chr(10) in r)
