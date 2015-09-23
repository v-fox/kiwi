# NAME

kiwi - Building Operating System Images

# SYNOPSIS

__kiwi__ system prepare --description=*directory* --root=*directory*

    [--type=*buildtype*]
    [--allow-existing-root]
    [--set-repo=*source,type,alias*]
    [--ass-repo=*source,type,alias*]

# DESCRIPTION

## __prepare__

Prepare and install a new system for chroot access

# OPTIONS

## __--description=directory__

The description must be a directory containing a kiwi XML description and optional metadata files

## __--root=directory__

The path to the new root directory of the system

## __--type=buildtype__

Set the build type. If not set the default XML specified build type will be used

## __--allow-existing-root__

Allow to use an existing root directory. Use with caution this could cause an inconsistent root tree if the existing contents does not fit to the additional installation

## __--set-repo=source,type,alias__

Overwrite the repo source for the first XML repository with the
given repo source, type and alias.

## __--add-repo=source,type,alias__

Add a new repository with specified source, type and alias

# REPOSITORIES

Available repo types are:

1. yast2
2. rpm-md
3. rpm-dir

