
import re

class Settings():
    def __init__(self,
                 member_iteration_filter_pattern = '^_',
                 convert_underscores_to_hypens = False,
                 convert_camel_case_to_hypens = False,
                 dump_method_name_in_node_classes: str = None,
                ):
        self.member_iteration_filter_pattern = re.compile(member_iteration_filter_pattern)
        self.convert_underscores_to_hypens = convert_underscores_to_hypens
        self.convert_camel_case_to_hypens = convert_camel_case_to_hypens
        self.dump_method_name_in_node_classes = dump_method_name_in_node_classes
