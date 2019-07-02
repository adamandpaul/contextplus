# -*- coding: utf-8 -*-
"""Template configuration file for sphinx

Instructions:

1. Copy
2. Update ``project`` and ``author`` values as appropriate
3. Save as ``docs/conf.py``
"""

import pkg_resources
from datetime import datetime


project = 'contextplus'
author = 'Adam & Paul Pty Ltd'

autoclass_content = 'both'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
copyright = u'{}, {}'.format(datetime.now().year, author)
version = pkg_resources.get_distribution(project).version
release = version
language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
htmlhelp_basename = project
autodoc_member_order = 'bysource'
autoclass_content = 'class'

def setup(app):
    app.add_stylesheet('custom.css')
