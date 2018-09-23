import sys

collect_ignore = ["setup.py"]

if sys.version_info < (3, 6):
    collect_ignore.append("test/test_tree/test_var_annotations.py")
