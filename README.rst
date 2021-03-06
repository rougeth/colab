.. -*- coding: utf-8 -*-

.. highlight:: rest

.. _colab_software:

=================================
Colab, a Software for Communities
=================================

.. image:: https://travis-ci.org/colab/colab.svg?branch=master
    :target: https://travis-ci.org/colab/colab

.. image:: https://coveralls.io/repos/colab/colab/badge.png?branch=master
          :target: https://coveralls.io/r/colab/colab?branch=master


What is Colab?
==============

Application that integrates existing systems to represent the contributions of the members through:

* The amendments to the Wiki trac system.

* Changes to the trac system code.

* Discussions at the mailman list.

* And other systems in the community.



Features
========

* Developed by Interlegis Communities http://colab.interlegis.leg.br/

* Written in Python http://python.org/

* Built with Django Web Framework https://www.djangoproject.com/

* Search engine with Solr https://lucene.apache.org/solr/



Installation
============

First install the dependencies and than the project it self:

.. code-block::

  pip install -r requirements.txt
  pip install .



Running Colab
=============

To run Colab with development server you will have to:

1- Create the example configuration file:

.. code-block::

  colab-init-config > /etc/colab/settings.yaml
  
2- Edit the configuration file. Make sure you set everything you need including **database** credentials.
  
3- Run the development server: 

.. code-block::

  colab-admin runserver 0.0.0.0:8000


**NOTE**: In case you want to keep the configuration file else where just set the 
desired location in environment variable **COLAB_SETTINGS**.

About test
==========

How to write a test
--------------------
Inside of each folder on /vagrant/colab/<folder> you can create a folder called
"tests", and inside of it implements the code for test each file. 
 
How to run the tests
--------------------

Follow the steps below:

* Go to vagrant/colab/
* run: ./runtests.sh