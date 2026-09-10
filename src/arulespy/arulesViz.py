"""Visualization helpers backed by the R package arulesViz."""

from html import escape
from pathlib import Path
from tempfile import TemporaryDirectory

import rpy2.robjects.packages as packages
from arulespy import _import_or_install_r_package
from arulespy.arules import arules2py_decor

### activate automatic conversion of pandas dataframes to R dataframes
#pandas2ri.activate()

R_arulesViz = _import_or_install_r_package("arulesViz")

# get the generic for plot
base = packages.importr('base')
plot = arules2py_decor(base.plot)
# we use the decorator so we can set docstrings, otherwise it would only show
# the docstring for the plot generic.
plot.__doc__ = """Visualize Association Rules and Itemsets

``plot(x, method=None, measure="support", shading="lift", limit=None,
interactive=None, engine="default", data=None, control=None, **kwargs)``
    
See the `arulesViz plot reference
<https://mhahsler.r-universe.dev/arulesViz/doc/manual.html#plot>`_ for available
methods and control options.
"""

inspectDT = R_arulesViz.inspectDT
# gets doc automatically inspectDT.__doc__ = R_arulesViz.inspectDT.__doc__
inspect_dt = inspectDT


class _HTMLWidget:
    """Notebook-displayable self-contained HTML document."""

    def __init__(self, document, width, height):
        self.document = document
        self.width = width
        self.height = height

    def _repr_html_(self):
        document = escape(self.document, quote=True)
        width = escape(str(self.width), quote=True)
        height = escape(str(self.height), quote=True)
        return (
            f'<iframe srcdoc="{document}" '
            f'style="width: {width}; height: {height}px; border: 0;">'
            "</iframe>"
        )


def html_widget(widget, filename=None, width="100%", height=600):
    """Save and embed an R HTML widget in a Python notebook.

    The widget is embedded with ``srcdoc`` so rendering does not depend on
    notebook-server routing for a relative file URL.

    Args:
        widget: An R ``htmlwidget`` object, such as the result of
            :func:`inspect_dt` or ``plot(..., engine="htmlwidget")``.
        filename: Optional path at which to keep the self-contained HTML
            document. A temporary file is used when omitted.
        width: CSS width of the iframe.
        height: Height of the iframe in pixels.

    Returns:
        An object that renders as an iframe in Jupyter-compatible notebooks.
    """
    htmlwidgets = packages.importr("htmlwidgets")

    def save_and_read(path):
        htmlwidgets.saveWidget(widget, str(path), selfcontained=True)
        return path.read_text(encoding="utf-8")

    if filename is None:
        with TemporaryDirectory(prefix="arulespy-") as directory:
            document = save_and_read(Path(directory) / "widget.html")
    else:
        document = save_and_read(Path(filename))

    return _HTMLWidget(document, width, height)


def ruleExplorer(x, sidebarWidth = 2, graphHeight = '600px'):
     """Launch the interactive arulesViz rule explorer.

     Args:
         x: Rules to explore.
         sidebarWidth: Width of the Shiny sidebar.
         graphHeight: CSS height of the graph display.
     """
     app = R_arulesViz.ruleExplorer(x, sidebarWidth = sidebarWidth, graphHeight = graphHeight)
     print(app)     


rule_explorer = ruleExplorer
