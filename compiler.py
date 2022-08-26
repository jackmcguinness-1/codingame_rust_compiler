from typing import List
from xml.etree.ElementInclude import include

class FileReadData:
    dependencies_to_ignore: List[str]
    root_src_path: str
    src_file_name: str
    
    def __init__(self, dependencies_to_ignore, root_src_path, src_file_name):
        self.dependencies_to_ignore = dependencies_to_ignore
        self.root_src_path = root_src_path
        self.src_file_name = src_file_name
        
class FileParsedData:
    dependencies_included: List[str]
    file_lines: List[str]
    
    def __init__(self, dependencies_included: List[str], file_lines: List[str]):
        self.dependencies_included = dependencies_included
        self.file_lines = file_lines

def build_file_with_dependencies(file_data: FileReadData) -> FileParsedData:
    root_src_path = file_data.root_src_path
    dependencies_to_ignore = file_data.dependencies_to_ignore
    src_file_name = file_data.src_file_name
    
    main_source_file = open(root_src_path + src_file_name, "r")
    main_source_lines = main_source_file.readlines()

    contains_mod_decl = lambda s: "mod" in s
    lines_declaring_modules = list(filter(contains_mod_decl, main_source_lines))

    parse_mod_name = lambda s: s.split(" ")[-1].replace(";","").replace("\n","")
    mod_names = list(map(parse_mod_name, lines_declaring_modules))

    construct_mod_path = lambda mod_name: root_src_path + mod_name + ".rs"
    include_dependency = lambda mod_name: not mod_name in dependencies_to_ignore
    dependencies_to_include = filter(include_dependency, mod_names)
    mod_source_file_names = list(map(construct_mod_path, dependencies_to_include))

    contains_use_decl = lambda s: "use crate" in s
    should_remove_line = lambda s: not contains_mod_decl(s) and not contains_use_decl(s)

    output_file_lines = list(filter(should_remove_line, main_source_lines))

    for mod_file_name in mod_names:
        mod_file_data = FileReadData(dependencies_to_ignore, root_src_path, mod_file_name + ".rs")
        mod_src_parsed = build_file_with_dependencies(mod_file_data)
        for dep in mod_src_parsed.dependencies_included:
            dependencies_to_ignore.append(dep)
        for line in mod_src_parsed.file_lines:
            output_file_lines.append(line)
            
    file_parsed_data = FileParsedData(dependencies_to_include, output_file_lines)

    return file_parsed_data



def main():
    dependencies_to_ignore = []
    
    main_file_data = FileReadData([], "./challenge/src/", "main.rs")
    
    parsed_file_data = build_file_with_dependencies(main_file_data)
    
    target_path = "./compiled_test/src/main.rs"
    output_file = open(target_path, "w")

    append_newline = lambda s: s+"\n"
    #output_file_lines = list(map(append_newline, output_file_lines))

    output_file.writelines(parsed_file_data.file_lines)

if __name__ == "__main__":
    main()