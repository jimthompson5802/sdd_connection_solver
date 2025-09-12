#!/usr/bin/env python3

import re

# Read the file
with open("tests/unit/test_context_service.py", "r") as f:
    content = f.read()

# Patterns to fix: Sessions with 4 words and solved_groups=[] should have solved_groups_count=3
# Sessions with 8 words and solved_groups=[] should have solved_groups_count=2

# Fix 4-word sessions with solved_groups=[]
pattern_4_words = re.compile(
    r'remaining_words=\["apple", "banana", "cherry", "date"\],\s*solved_groups=\[\],', re.MULTILINE
)
content = pattern_4_words.sub(
    'remaining_words=["apple", "banana", "cherry", "date"],\n'
    "            solved_groups_count=3,  # 16 - 3*4 = 4 remaining words",
    content,
)

# Fix 8-word sessions with solved_groups=[]
pattern_8_words = re.compile(
    r'remaining_words=\["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"\],\s*solved_groups=\[\],',
    re.MULTILINE,
)
content = pattern_8_words.sub(
    'remaining_words=["apple", "banana", "cherry", "date", "cat", "dog", "bird", "fish"],\n'
    "            solved_groups_count=2,  # 16 - 2*4 = 8 remaining words",
    content,
)

# Fix sessions with empty remaining_words
content = re.sub(
    r"remaining_words=\[\],\s*solved_groups=\[\],",
    "remaining_words=[],\n" "            solved_groups_count=4,  # 16 - 4*4 = 0 remaining words",
    content,
)

# Write back
with open("tests/unit/test_context_service.py", "w") as f:
    f.write(content)

print("Fixed Session model instances in test_context_service.py")
