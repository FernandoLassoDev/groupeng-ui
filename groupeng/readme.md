GroupEng
========

GroupEng is an open source (AGPLv3) program that makes it easy for
instructors to assign students to groups for projects or groupwork, even
with large classes.

GroupEng was written specifically to help instructors follow education
research guidelines for improving student, and especially minority,
performance in group project based classwork. It allows instructors to
think at an abstract level about what properties they want student
groups to have; GroupEng handles the details of optimizing the groups to
meet those criteria.

GroupEng operates on class data from an excel spreadsheet (exported to a
.csv text file) and forms groups of students based on grouping rules
supplied by the instructor. These rules are defined using four grouping
operators:

-   **Distribute**: Spread students with some attribute (major, a needed
    skill) across all groups so that each group has about the same
    number of them
-   **Aggregate**: Group students with some attribute (project choice,
    section number) together in the same groups
-   **Cluster**: Ensure that students with some attribute (women,
    minorities) are not isolated in a group (there will be at least 2 of
    them in a group)
-   **Balance**: Ensure equal strength of groups based on some numeric
    score (GPA, pretest).

You specify class data, desired group size, and an ordered list of
grouping rules (earlier rules are given higher priority) in a simple
text file, and GroupEng does the rest, outputting a grouping of the
students, as well as statistics of how well it was able to meet your
rules. GroupEng has a random element, so different runs with the same
rules will generate different groups.

Download
--------

[GroupEng v1.1.1](https://groupeng.org/files/groupeng_1.1.1.zip)

GroupEng requires only [Python](http://www.python.org/). If you are
using a Mac, you already have python, but if it fails try
[this](http://python.org/ftp/python/2.7.2/python-2.7.2-macosx10.6.dmg)
version.

-   Download and install python if necessary (you probably want
    [this](http://www.python.org/ftp/python/2.7.2/python-2.7.2.msi)
    version), then download and unpack the GroupEng archive.
-   Write a group description file telling GroupEng how to make groups
    for your class, see the sample files in the archive for examples.
-   Run GroupEng either by double-clicking the GroupEng.py file in the
    archive and selecting your input file in the file chooser that
    appears, or at a command line specifying the location of your input
    file as an argument

We also have much more detailed
[instructions](https://groupeng.org/files/GroupEng_Instructions.pdf) if
you want them.

GroupEng is still fairly experimental software. I hope it is useful to
you, but it is still a little rough around the edges. Feel free to
[contact me](mailto:tom@dimiduk.net) if you have any problems using
GroupEng

Documentation and Publications
------------------------------

Kathryn's
[talk](https://groupeng.org/files/ASSE_Lawrence_GroupEng_Workshop.pdf)
on GroupEng at the ASEE Lawrence Section in March 2012.

We presented GroupEng at the 2011 WEPAN conference in Seattle.

We gave a [talk](https://groupeng.org/files/GroupEng_Talk_WEPAN.pdf) and
wrote a [paper](https://groupeng.org/files/GroupEng_Paper_WEPAN.pdf) on
GroupEng.

These two documents give a good introduction and overview of GroupEng
and how you should think about using it. We have simplified the input
files since those documents were written, so follow the example that
comes with the program instead of the directions in the paper.
