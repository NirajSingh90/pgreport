Introduction
============

Pgreport takes the default postgresql.conf , configurations 
of hardware it's being deployed on and generates a report file [PDF] consisting of recommendations. 

Installation/Usage
==================

Source installation
-------------------

Its a python script.There is no need to build/compile pgreport.
Extracting the zip to a convenient location.
Note that you will need postgresql-server installation on system.


Using pgreport
============

pgreport works by taking an existing postgresql.conf file as an input,
and based on system hardware configurations it will output a new pdf file.

Usage::

  python pgreport [$PGDATA/postgresql.conf]
  
  for ex:
  python pgreport /etc/postgresql/9.1/main/postgresql.conf
  
  Output:
  [The execution of the program will take some time]
  The output i.e; Report.pdf will be saved in the same directory of your program.

Todo
====

testing
work on additional parameters

Bugs
====

Program is under testing phase.If you find any bugs please mail the below concerned person.

Contact
=======

 * Initial commits are done in the git repostiory at
   http://git.postgresql.org/git/pgreport.git and
   http://github.com/Rushikesh005/pgreport

If you have any hints, changes or improvements, please contact:

 * Rushikesh Patil rushikesh.patil003@gmail.com
 * Prashant Pandey prashantpandeyfun10@gmail.com
