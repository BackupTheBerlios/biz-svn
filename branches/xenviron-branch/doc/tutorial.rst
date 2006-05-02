
============
Biz Tutorial
============

:version: 0.0.1
:author: Yüce Tekol <http://www.geocities.com/yucetekol>

.. contents::



Installing Biz
--------------


Creating a Biz ApplicationSite Project
--------------------------------------


Biz Applications By Configuration
---------------------------------


Writing Biz Application From Scratch
------------------------------------

In the previous section, we saw how to reuse pre-written applications; in this section, we will have a look at how to write configurable applications.

"Hello, World!" revisited
.........................

A Biz application is a Python module (one Python file) or package (a group of Python files residing in a directory) which contains a class derived from biz.Application and a loader function. Let's have a look at the simplest application below::
  
  import biz

  class Hello(biz.Application):
	  def static(self):
		  self.content = biz.TextContent("Hello, World!")

  def load(xenviron):
	  return Hello(xenviron)

Hello is a class derived from biz.Application; by doing so, we leave a lot of dirty work like setting the response code, content type, etc. This is a very simple application that displays a fixed message, so we override the ``static`` method of biz.Application; that method is executed only once, so you may prepare pages that will not change during the life of the application here. In ``static``, we set the content of the response, that is a *Hello, World!* message in this case. We don't want to use HTML markup right now, so we simply 



Looking Further...
------------------
