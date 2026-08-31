"""Import-safety test (Batch-1): importable library modules must import with NO
import-time real-data read.

Runs under the autouse DUA guard in ``tests/conftest.py``. If any of these modules
performed a real participant-data read at import (a governed-root data file), the
guard would raise ``AssertionError`` and this test would go RED. It passes because
the data loaders are lazy — they read only when their ``load_*()`` function is
called, never at import (``utils/data_loader.py``); ``utils/sidebar.py`` reads its
logo only inside ``render_sidebar()``; ``utils/styling.py`` and ``utils/plotting.py``
are pure constants + function definitions.

Deliberately EXCLUDED:
  * Streamlit page scripts (``pages/*.py``, ``app.py``) — entrypoints executed by the
    Streamlit runtime, not importable library modules; their top-level file reads are
    the intended page render and touch only aggregate JSON / figure images, never
    participant rows.
  * ``animations/*.py`` — ``manim`` is not installed in the analysis container, so an
    import failure there would be unrelated to data safety (they, too, read only the
    aggregate ``survival_curves.json`` and only inside a function).
"""

import importlib
import os
import sys

import pytest

# Ensure the repo root (parent of tests/) is importable so ``utils`` resolves under
# pytest regardless of its sys.path import mode.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

# Side-effect-free library modules that must be safe to import at collection time.
IMPORTABLE_MODULES = [
    "utils.styling",
    "utils.plotting",
    "utils.data_loader",
    "utils.sidebar",
    "utils.cell_floor",
]
# utils.wave2 is a cuaim-harvest helper and is not in the public tree.


@pytest.mark.parametrize("modname", IMPORTABLE_MODULES)
def test_module_imports_without_real_data_read(modname):
    # Drop any cached copy so the module's top-level code re-executes under the
    # active autouse DUA guard (a stray governed-root read -> AssertionError -> RED).
    sys.modules.pop(modname, None)
    mod = importlib.import_module(modname)
    assert mod is not None
