"""Python interface to the R packages arules and arulesViz.

Importing :mod:`arulespy` itself deliberately does not initialize R, change R
options, or install packages. Core and visualization objects are loaded only
when they are first accessed.
"""

from importlib import import_module


__version__ = "0.2.0"

_CORE_EXPORTS = {
    "R_arules",
    "arules2py",
    "arules_to_py",
    "parameters",
    "Associations",
    "ItemMatrix",
    "Rules",
    "Itemsets",
    "Transactions",
    "concat",
    "apriori",
    "eclat",
    "discretizeDF",
    "discretize_df",
}
_VISUALIZATION_EXPORTS = {
    "R_arulesViz",
    "plot",
    "inspectDT",
    "inspect_dt",
    "html_widget",
    "ruleExplorer",
    "rule_explorer",
}

__all__ = sorted(
    {"__version__", "install_r_packages"}
    | _CORE_EXPORTS
    | _VISUALIZATION_EXPORTS
)


def install_r_packages(package_names=("arules", "arulesViz"), **kwargs):
    """Explicitly install missing R packages required by arulespy.

    Args:
        package_names: Names of R packages to check and install.
        **kwargs: Additional arguments passed to R's ``install.packages``.

    Returns:
        A list containing the names of packages that were installed.
    """
    import rpy2.robjects.packages as rpackages
    from rpy2.robjects.vectors import StrVector

    missing = [name for name in package_names if not rpackages.isinstalled(name)]
    if missing:
        utils = rpackages.importr("utils")
        utils.install_packages(StrVector(missing), **kwargs)
    return missing


def _import_or_install_r_package(package_name):
    """Import an R package, installing it from CRAN when it is missing."""
    import rpy2.robjects.packages as rpackages

    try:
        return rpackages.importr(package_name)
    except rpackages.PackageNotInstalledError:
        try:
            install_r_packages(
                (package_name,), repos="https://cloud.r-project.org"
            )
            return rpackages.importr(package_name)
        except Exception as exc:
            raise ImportError(
                f"The R package {package_name!r} is required and could not be "
                "installed automatically. Install it in R with "
                f"install.packages({package_name!r})."
            ) from exc


def __getattr__(name):
    if name in _CORE_EXPORTS:
        module = import_module(".arules", __name__)
    elif name in _VISUALIZATION_EXPORTS:
        module = import_module(".arulesViz", __name__)
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    value = getattr(module, name)
    globals()[name] = value
    return value
