import argparse
import re
import os

obj_src_map = \
    {"tools/objtool/libstring.o": "tools/lib/string.c",
     "tools/objtool/str_error_r.o": "tools/lib/str_error_r.c"}

include_dirs = \
    ["/usr/lib/gcc/x86_64-redhat-linux/4.8.5/include",
                "arch/x86/include",
                "arch/x86/include/generated",
                "include",
                "arch/x86/include/uapi",
                "arch/x86/include/generated/uapi",
                "include/uapi",
                "include/generated/uapi"]

headers = []

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--logfile', required=True, help='log file input', dest='logfile')
    parser.add_argument('-o', '--output', default='filelist.txt', help='file list generated to output', dest='output')
    # parser.add_argument('-p', '--parrent', required=True, help='real parrent dir', dest='parent_dir')
    args = parser.parse_args()
    return (args.logfile, args.output)

def get_normal_src_file(objfile):
    c_file = objfile.replace('.o', '.c')
    asm_file = objfile.replace('.o', '.S')
    if os.path.exists(c_file):
        return c_file
    elif os.path.exists(asm_file):
        return asm_file
    return None

def get_objtool_src_file(objfile):
    src_file = get_normal_src_file(objfile)
    if src_file is None:
        objfile1 = objfile.replace('objtool', 'lib/subcmd')
        src_file =  get_normal_src_file(objfile1)
        if src_file is not None:
            return src_file
        else:
            return obj_src_map[objfile]
    else:
        return src_file

def find_file_from_system_include_dirs(header_file):
    for path in include_dirs:
        h_file = os.path.join(path, header_file)
        if os.path.exists(h_file):
            return h_file
    return None

def find_file_from_source_dir(file_dir, header_file):
    h_file = os.path.join(file_dir, header_file)
    if os.path.exists(h_file):
        return h_file
    return None

def get_header_files(file):
    file_dir_path = os.path.dirname(file)
    f = open(file, mode = "r")
    for line in f.readlines():
        if '#' != line[0]:
            continue
        lines = line.split()
        if len(lines) < 2:
            continue
        if '#include' == lines[0]:
            header_file = lines[1]
        elif 'include' == lines[1]:
            header_file = lines[2]
        else:
            continue
        if '<' == header_file[0]:
            header_file_n = header_file.strip('<>')
            header_file_get = find_file_from_system_include_dirs(header_file_n)
        elif '"' == header_file[0]:
            header_file_n = header_file.strip('"')
            header_file_get = find_file_from_source_dir(file_dir_path, header_file_n)
        else:
            print 'invalid file ' + file + "'s header " + header_file + " start " + lines[0]
            continue
        if header_file_get is None:
            if 'uapi' in file:
                continue
            else:
                print "source file" + file + "'s header " + header_file + " not exists!"
                continue
        if header_file_get not in headers:
            print header_file_get
            headers.append(header_file_get)
            get_header_files(header_file_get)

def get_source_files(log_file, root_dir):
    src_files = []
    for line in log_file.readlines():
        lines = line.split()
        if 'CC' == lines[0]:
            obj_file = lines[len(lines) - 1]
            if '.mod.o' in obj_file:
                continue
            obj_file = obj_file.replace(root_dir + '/', '')
            if obj_file.find('objtool'):
                src_file = get_objtool_src_file(obj_file)
            else:
                src_file = get_normal_src_file(obj_file)
            if src_file is None:
                print obj_file + ' cannot find src file'
                exit(1)
            src_files.append(src_file)
    return src_files

if __name__ == '__main__':
    logfile, output = get_args()
    parent_dir = 'E:\\project\\linux-3.10.0-862.el7.centos.x86_64'
    root_dir = os.getcwd()
    f_log = open(logfile, mode='r')
    f_output = open(output, mode ='w')
    all_headers = []
    src_files = get_source_files(f_log, root_dir)
    for file in src_files:
        get_header_files(file)
    print "headers:"
    for h in headers:
        print h
    for file in src_files:
        path = os.path.join(parent_dir, file)
        path = path.replace('/', '\\')
        f_output.write(path)
        f_output.write('\r\n')
    for h in headers:
        path = os.path.join(parent_dir, h)
        path = path.replace('/', '\\')
        f_output.write(path)
        f_output.write('\r\n')


