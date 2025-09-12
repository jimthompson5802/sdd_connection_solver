#!/bin/bash

# Script to fix Session model validation issues in test files

# Create the 16-word list for 0 solved groups (16 - 0*4 = 16)
SIXTEEN_WORDS='["apple", "banana", "cherry", "date", "elephant", "fox", "grape", "hat", "ice", "juice", "kite", "lemon", "mouse", "nest", "orange", "pen"]'

# Create 12-word list for 1 solved group (16 - 1*4 = 12)
TWELVE_WORDS='["apple", "banana", "cherry", "date", "elephant", "fox", "grape", "hat", "ice", "juice", "kite", "lemon"]'

# Create 8-word list for 2 solved groups (16 - 2*4 = 8)
EIGHT_WORDS='["apple", "banana", "cherry", "date", "elephant", "fox", "grape", "hat"]'

# Create 4-word list for 3 solved groups (16 - 3*4 = 4)
FOUR_WORDS='["apple", "banana", "cherry", "date"]'

echo "Fixing Session model validation issues..."

# Fix llm_model to llm_model_config in all test files
find tests -name "*.py" -exec sed -i '' 's/llm_model="/llm_model_config="/g' {} \;

echo "Fixed llm_model field names"

# Note: remaining_words length fixes need to be done manually based on context
# since we need to know how many solved_groups_count each test expects

echo "Session model field names fixed. Need to manually adjust remaining_words counts."
