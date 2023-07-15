import os
import sys
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to
# the sys.path.
sys.path.append(parent)

import movie_subtitle_finder

file_path = sys.argv[1]
movie_subtitle_finder.process_all_files_in_directory(file_path)
