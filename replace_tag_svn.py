#!/usr/bin/python
"""Replace @since tag with metadata from svn log command.

It searches Java files in given directory or current directory. For each one it updates @since tag with value taken from first svn commit from svn log command.

Copyright (C) 2008 Kamil Demecki <kodstark@gmail.com>

Licensed under the terms of any of the following licenses at your choice:

- GNU Lesser General Public License Version 2.1 or later (the "LGPL")
  http://www.gnu.org/licenses/lgpl.html

- Mozilla Public License Version 1.1 or later (the "MPL")
  http://www.mozilla.org/MPL/MPL-1.1.html
"""
import os
import re
import sys
import time
import subprocess

re_since = re.compile(r'(.*)@since.*')

def replace_since_tag_from_svn_metadata(directory):
    for file_name in find_java_files(directory):        
        svn_log_data = get_svn_log(file_name)
        create_date = get_create_date_from_svn_log(svn_log_data)
        new_since_tag = get_new_since_tag(create_date)
        file_data = get_file_data(file_name)        
        if exist_since_tag(file_data) and is_not_correct_since_tag(file_data, new_since_tag):
            log_fixing_file(file_name, new_since_tag)
            fixed_file_data = fix_since_tag(file_data, new_since_tag)
            save_file_data(file_name, fixed_file_data)

def find_java_files(directoryName):    
    for curdir, dirs, files in os.walk(directoryName):
        for file_name in files: 
            if file_name.endswith(".java"): yield os.path.join(curdir, file_name)
        if 'CVS' in dirs: dirs.remove('CVS')
        if '.svn' in dirs: dirs.remove('.svn')
        if '.git' in dirs: dirs.remove('.git')

def get_svn_log(file_name):
    svn_log_process = subprocess.Popen(["svn", "-q", "log", file_name], env={'LANG':'C'}, 
                                       stdin=subprocess.PIPE, stdout=subprocess.PIPE).stdout
    result = svn_log_process.read()
    return result

def get_create_date_from_svn_log(svn_log_data):
    first_log = [log for log in svn_log_data.split('\n') if log.startswith('r')][-1]
    create_date_str = ' '.join(first_log.split('|')[-1].strip().split(' ')[:2])
    result = time.strptime(create_date_str, '%Y-%m-%d %H:%M:%S')
    return result

def get_file_data(file_name):
    with open(file_name) as file_handler:
        file_data = file_handler.read()
    return file_data

def exist_since_tag(file_data):
    return file_data.find("@since") != -1

def is_not_correct_since_tag(file_data, new_since_tag):
    return file_data.find(new_since_tag) == -1

def get_new_since_tag(create_date):
    return "@since %s" % time.strftime('%b %d, %Y', create_date)

def save_file_data(file_name, fixed_file_data):
    with open(file_name, 'w') as file_handler:
        file_handler.write(fixed_file_data)

def fix_since_tag(file_data, new_since_tag):
    fixed_file_data = re_since.sub("\\1" + new_since_tag, file_data)
    return fixed_file_data

def log_fixing_file(file_name, new_since_tag):
    print "Add fixed tag '%s' in file %s" % (new_since_tag, file_name)

def get_directory():
    try:
        directory = sys.argv[1]
    except IndexError:
        directory = '.'
    return directory

def main():
    directory = get_directory()
    replace_since_tag_from_svn_metadata(directory)

if __name__ == '__main__':
    main()
