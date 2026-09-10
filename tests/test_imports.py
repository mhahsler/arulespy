import importlib
import subprocess
import sys
from pathlib import Path
from unittest import mock

import pytest
import rpy2.robjects.packages as rpackages

import arulespy


def run_python(source):
    return subprocess.run(
        [sys.executable, "-c", source],
        check=False,
        capture_output=True,
        text=True,
    )


def test_package_import_is_lazy():
    result = run_python(
        "import sys, arulespy; "
        "assert 'rpy2' not in sys.modules; "
        "assert 'arulespy.arules' not in sys.modules; "
        "assert 'arulespy.arulesViz' not in sys.modules"
    )

    assert result.returncode == 0, result.stderr


def test_core_import_preserves_r_options_and_library_paths():
    result = run_python(
        "import rpy2.robjects as ro; "
        "before = tuple(ro.r('.libPaths()')); "
        "ro.r('options(warn=1)'); "
        "from arulespy import Transactions; "
        "assert ro.r('getOption(\"warn\")')[0] == 1; "
        "assert tuple(ro.r('.libPaths()')) == before"
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("module_name", "missing_name"),
    [
        ("arulespy.arules", "arules"),
        ("arulespy.arulesViz", "arulesViz"),
    ],
)
def test_missing_r_packages_are_installed_on_submodule_import(
    module_name, missing_name
):
    source = f"""
import importlib
import rpy2.robjects.packages as packages

state = {{"installed": False, "install_calls": []}}
original = packages.importr
def importr(name, *args, **kwargs):
    if name == "utils":
        class Utils:
            def install_packages(self, names, **install_kwargs):
                state["install_calls"].append((list(names), install_kwargs))
                state["installed"] = True
        return Utils()
    if name == {missing_name!r}:
        if not state["installed"]:
            raise packages.PackageNotInstalledError(name)
    return original(name, *args, **kwargs)

packages.importr = importr
packages.isinstalled = lambda name, **kwargs: state["installed"] if name == {missing_name!r} else True
importlib.import_module({module_name!r})
assert state["install_calls"] == [(
    [{missing_name!r}],
    {{"repos": "https://cloud.r-project.org"}},
)]
"""
    result = run_python(source)

    assert result.returncode == 0, result.stderr


def test_failed_automatic_r_package_install_has_actionable_error():
    source = """
import importlib
import rpy2.robjects.packages as packages

original = packages.importr
def importr(name, *args, **kwargs):
    if name == "arules":
        raise packages.PackageNotInstalledError(name)
    if name == "utils":
        class Utils:
            def install_packages(self, names, **install_kwargs):
                raise RuntimeError("installation failed")
        return Utils()
    return original(name, *args, **kwargs)

packages.importr = importr
packages.isinstalled = lambda name, **kwargs: False if name == "arules" else True
try:
    importlib.import_module("arulespy.arules")
except ImportError as error:
    assert "could not be installed automatically" in str(error)
else:
    raise AssertionError("expected an actionable ImportError")
"""
    result = run_python(source)

    assert result.returncode == 0, result.stderr


@pytest.mark.skipif(
    not rpackages.isinstalled("arulesViz"),
    reason="R package arulesViz is not installed",
)
def test_visualization_import():
    module = importlib.import_module("arulespy.arulesViz")
    assert callable(module.plot)
    assert callable(module.html_widget)
    assert module.inspect_dt is module.inspectDT
    assert module.rule_explorer is module.ruleExplorer


def test_python_style_function_aliases():
    from arulespy import arules2py, arules_to_py, discretizeDF, discretize_df

    assert arules_to_py is arules2py
    assert discretize_df is discretizeDF
    assert "arules_to_py" in arulespy.__all__
    assert "discretize_df" in arulespy.__all__
    assert "inspect_dt" in arulespy.__all__
    assert "html_widget" in arulespy.__all__
    assert "rule_explorer" in arulespy.__all__


@pytest.mark.skipif(
    not rpackages.isinstalled("arulesViz"),
    reason="R package arulesViz is not installed",
)
def test_html_widget_embeds_saved_document(tmp_path):
    module = importlib.import_module("arulespy.arulesViz")
    saved = tmp_path / "widget.html"
    htmlwidgets = mock.Mock()

    def save_widget(widget, filename, selfcontained):
        assert widget == "widget"
        assert selfcontained is True
        Path(filename).write_text(
            '<script>const message = "hello";</script>', encoding="utf-8"
        )

    htmlwidgets.saveWidget.side_effect = save_widget
    with mock.patch.object(module.packages, "importr", return_value=htmlwidgets):
        rendered = module.html_widget(
            "widget", saved, width="75%", height=480
        )._repr_html_()

    assert saved.exists()
    assert 'style="width: 75%; height: 480px; border: 0;"' in rendered
    assert "&lt;script&gt;" in rendered


def test_install_r_packages_skips_installed_packages():
    with (
        mock.patch.object(rpackages, "isinstalled", return_value=True),
        mock.patch.object(rpackages, "importr") as importr,
    ):
        assert arulespy.install_r_packages() == []
        importr.assert_not_called()


def test_install_r_packages_installs_only_missing_packages():
    utils = mock.Mock()
    with (
        mock.patch.object(
            rpackages,
            "isinstalled",
            side_effect=lambda name: name == "arules",
        ),
        mock.patch.object(rpackages, "importr", return_value=utils),
    ):
        missing = arulespy.install_r_packages(("arules", "arulesViz"), quiet=True)

    assert missing == ["arulesViz"]
    installed_names = list(utils.install_packages.call_args.args[0])
    assert installed_names == ["arulesViz"]
    assert utils.install_packages.call_args.kwargs == {"quiet": True}
