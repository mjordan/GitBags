#!/usr/bin/env python

"""
Script to demonstrate how to create a GitBag. For more information,see
https://github.com/mjordan/GitBags. This script is in the public domain.

Usage: ./create_gitbag_sample.py [-l|--light] /path/to/directory

-l, --light: Create a light GitBag
/path/to/directory: The path to the directory that you want to create
  the GitBag in.
"""
import os
import sys
import re
import argparse
import bagit
import git

def get_directory_contents(root_dir):
    "Gets a list of files in root_dir"
    file_path_list = []
    for root_dir, sub_folders, files in os.walk(root_dir):
        for file in files:
            path_to_file = os.path.join(root_dir, file)
            # We don't want to include files in the .git directory.
            if not re.search(r"\.git", path_to_file):
                file_path_list.append(path_to_file)

    return file_path_list

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-l", "--light", help="Create a light GitBag",
        action="store_true")
    argparser.add_argument("git_bag_dir", help = "The target directory")
    args = argparser.parse_args()

    if not os.path.exists(args.git_bag_dir):
        sys.exit("Sorry, %s doesn't appear to exist." % args.git_bag_dir)

    # Create the Bag.
    bag = bagit.make_bag(args.git_bag_dir, {'Contact-Name': 'Mark Jordan'})

    # Initialize the Git repo. We do this only after we have created the Bag.
    repo = git.Repo.init(args.git_bag_dir)

    # Get the repo's index so we can add files.
    index = repo.index

    if args.light:
        # Add the files required for a light GitBag.
        index.add(['bag-info.txt', 'bagit.txt', 'manifest-md5.txt', 'tagmanifest-md5.txt'])
    else:
        # Add all the files in the Bag directory to create a full GitBag.
       file_paths = get_directory_contents(args.git_bag_dir)
       index.add(file_paths)

    # Commit the staged changes.
    index.commit("Initial commit.")

