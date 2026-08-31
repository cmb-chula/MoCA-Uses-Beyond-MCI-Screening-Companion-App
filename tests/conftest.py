"""Autouse DUA safety-net (Batch-1) — block any REAL participant-data read during tests.

Blocks pandas readers whose resolved path is a data file under a governed data root
(absolute ``/data/...`` trees or a ``~`` expansion). Synthetic reads (in-memory,
``tmp_path``, relative fixtures under ``tests/``) are unaffected — so a correctly
written synthetic test never trips it; it fires only if code under test tries to
touch real data (e.g. a loader called with its default governed path).

Merge into a work's ``tests/conftest.py`` (append the fixture if a conftest exists).
Intentionally narrow (data-file extensions under governed roots only) so it cannot
destabilise an existing suite.
"""

import os

import pytest

_GOVERNED = ("/data/project/cuaim", "/data/home/dhupb/data")
_ALLOW = ("/tests/", "/test_templates/", "/tmp/", "/dev/null")
_DATA_EXT = (
    ".csv",
    ".xlsx",
    ".xls",
    ".sav",
    ".sas7bdat",
    ".parquet",
    ".dta",
    ".feather",
    ".h5",
    ".hdf5",
    ".npy",
    ".npz",
)


def _blocked(path):
    try:
        p = os.path.realpath(os.path.expanduser(str(path)))
    except Exception:
        return False
    if any(s in p for s in _ALLOW):
        return False
    return p.endswith(_DATA_EXT) and any(p.startswith(r) for r in _GOVERNED)


@pytest.fixture(autouse=True)
def _dua_no_real_reads(monkeypatch):
    import pandas as pd

    def wrap(name):
        fn = getattr(pd, name, None)
        if fn is None:
            return

        def guarded(path, *a, **k):
            if _blocked(path):
                raise AssertionError(
                    f"DUA: test attempted to read real data at {path!r}; "
                    "use a synthetic/tmp path."
                )
            return fn(path, *a, **k)

        monkeypatch.setattr(pd, name, guarded)

    for name in (
        "read_csv",
        "read_excel",
        "read_parquet",
        "read_sas",
        "read_stata",
        "read_table",
        "read_feather",
        "read_hdf",
    ):
        wrap(name)
    yield
