
============
Biz Tutorial
============

:version: 0.0.1
:author: Yüce Tekol <http://www.geocities.com/yucetekol>

.. contents::



Installing Biz
--------------


Creating and Running Your First Biz Project
-------------------------------------------

Audience
--------

While we are developing Biz, we always keep three types of users behind our minds:

1) Not programmer users: These users don't know, or don't care about programming, they only want an easily configurable site, which they can add applications which are created by others.

2) Single programmers: 

3) Small development teams: These teams have developers and page designers, and they want the logic separated from the content, and which in turn separated from the presentation.

Biz Applications
----------------

Let's first define what a **Biz application** is,

**Application**
  An application *in the Biz sense* is a Python module that gets a *request* and sends a *response*; it is attached to the first word of the URL path. For example, in the URL, \http://www.company.com/TheProduct?format=html, **wiki** is an application that gets ``TheProduct`` as an argument and a keyword argument ``format`` with a value ``html``. If there is no path in the URL, such as \http://www.company.com, the *index* application is invoked.


Biz Applications By Configuration
.................................

Reusability on the application level is the foremost priority of Biz; a person should be able to add/remove web applications from his/her site as quickly and easilyas possible, by modifying a configuration file or just using an administration interface. Biz tries to satisfy this aim by splitting an application into two parts: the configuration and the body. Application configuration file contains at least the place where the body can be found. For example a Biz project may have a configuration file for the *virtual folder* application like this::

  [files]
  module=biz.apps.vfolder
  vfolder.location=/home/pingu/www

The virtual folder application serves the files in the directory given in the ``vfolder.location`` option; it is a standard application bundled with the Biz package, so we use the ``module`` option to tell its place. The section name (``files`` in this case) is not used currently, but it is best to assign a meaningful name.

We should also inform Biz about the place of this configuration file, and under which name it will be attached to the URL. Assuming the application configration is saved under ``cfg`` as ``files.ini``, it is enough to add the following line to ``biz.ini`` (in the project root directory) in ``[applications]`` section::

  [applications]
  files: cfg/files.ini

Easy, isn't it?


Writing Biz Application From Scratch
------------------------------------

In the previous section, we saw how to reuse pre-written applications; in this section, we will have a look at how to write configurable applications.

"Hello, World!" revisited
.........................

A Biz application is a Python module (one Python file) or package (a group of Python files residing in a directory) which contains a class derived from ``Application`` or ``StaticApplication`` and a (optional) loader function. Let's have a look at the simplest application below::
  
  from biz import *

  class HelloApp(StaticApplication):
	  def static(self):
		  self.content = TextContent("Hello, World!")


In the example, we derived ``HelloApp`` from ``StaticApplication``; by doing so, we leave a lot of dirty work like setting the response code, content type, etc. The application is very simple, it merely displays a fixed message, so we overrided the ``static`` method of ``StaticApplication``; that method is executed only once, so you may prepare pages that will not change during the life of the application there. In ``static``, we set the content of the response, that is a *Hello, World!* message in this case. We don't want to use HTML markup right now, so we simply used ``TextContent``.





Looking Further...
------------------
