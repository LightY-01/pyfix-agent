from patched_script2 import capitalize_all_words

assert capitalize_all_words(["hello", "world"]) == ["Hello", "World"]
assert capitalize_all_words([]) == []
assert capitalize_all_words(["python"]) == ["Python"]
