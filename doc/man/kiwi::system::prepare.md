# NAME

kiwi - Building Operating System Images

# SYNOPSIS

__kiwi__ system prepare --description=*directory* --root=*directory*

    [--type=*buildtype*]
    [--allow-existing-root]
    [--set-repo=*source*]
    [--set-repotype=*type*]
    [--set-repoalias=*alias*]

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

## __--set-repo=source__

Overwrite the repo source for the first XML repository

## __--set-repotype=type__

Overwrite the repo type for the first XML repository. Available types are

1. yast2
2. rpm-md
3. rpm-dir

## __--set-repoalias=alias__

Overwrite the repo alias for the first XML repository
