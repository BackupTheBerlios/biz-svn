
=======================
Biz Templating Overview
=======================

:version: 0.1
:date: 2006-05-22
:author: Yuce Tekol <yucetekol AT yahoo DOT com>

Introduction
------------

Biz includes a simple templating system for developers and users not wishing to depend on an external templating framework (e.g., Cheetah).

Syntax
------

(Note: I am borrowing some Cheetah terminology here.)

Biz templating system offers two basic tools for the template writer, *placeholders* and *directives*.


Placeholders
............

Placeholders are filled with corresponding values in the namespace, they are denoted by ``$placeholder`` or ``${placeholder}``, placeholder should be a legal Python identifier. Consider the following template::

  <a href="$link.target">$link.name</a>

``$link.target`` and ``$link.name`` are placeholders. Assuming ``link.target`` evaluates to ``http://biz.berlios.de`` and ``link.name`` evaluates to ``Biz Homepage``, rendering the template produces the output below::
  
  <a href="http://biz.berlios.de">Biz Homepage</a>

You can use ``${placeholder}`` notation to tell the placeholder unambiguosly::

  Biz ${what}page


Directives
..........

Directives are being used to inject some logic into the template. They occupy strictly one line; no other template element can coexist with a directive on the same line. There are three types of directives: headers, chains and one-liners.

A *header* directive marks the beginning of a block. The block is made of one or more lines of source which are processed to create output. Header directive starts with ``{%``, ...::

  <table>
  {% for link in links
	<tr>
	  <td><a href="$link.target">$link.name</a></td>
	  <td>$link.description</td>
	</tr>
  %}

Chain directives maybe used to create linked blocks, such as ``if..elif..else``::

  {% if grade > 80
	A
  %} elif grade > 60 %{
	B
  %} else %{
	C
  %}

