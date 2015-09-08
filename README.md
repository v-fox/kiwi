KIWI
====

horizon - development branch

An investment to to implement a new kiwi version based on python
Make it more flexible, 100% test covered, eliminate unused code
paths, based on one language, make it easier for people to
contribute

Introduction
------------

The openSUSE KIWI Image System provides an operating
system image solution for Linux supported hardware platforms as
well as for virtualization systems like Xen, VMware, etc. The KIWI
architecture was designed as a two level system. The first stage,
based on a valid software package source, creates a so called 
unpacked image according to the provided image description.
The second stage creates from a required unpacked image an
operating system image. The result of the second stage is called
a packed image or short an image.
