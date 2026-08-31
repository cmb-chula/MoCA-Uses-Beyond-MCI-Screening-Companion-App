"""Meta-test (DUA guard): no test file reads real, non-synthetic participant data.

Static scan of the test tree. Tests must read only synthetic frames built in-memory
or written under ``tmp_path`` / the committed ``tests/`` fixture tree — never an
absolute/home/governed path. This has teeth without any runtime monkeypatching, so
it cannot destabilise an existing suite.

Portable: drop this file into any work's ``tests/`` directory unchanged.
"""
import pathlib
import re

_HERE = pathlib.Path(__file__).resolve().parent

# a data reader whose FIRST positional arg is an absolute path ("/..."), a home path
# ("~..."), or the governed data root ("/data/...") — i.e. not tmp_path / a relative
# fixture. String-prefix chars (f/r/u/b) are tolerated before the quote.
_BAD = re.compile(
    r"(read_csv|read_excel|read_parquet|read_sas|read_stata|read_table|read_sav|"
    r"read_feather|read_hdf|np\.load|h5py\.File|open)\("
    r"\s*[frub]*[\"'](/|~)"
)


def test_no_real_data_reads_in_tests():
    offenders = []
    for f in _HERE.rglob("test_*.py"):
        if f.name == pathlib.Path(__file__).name:
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        for m in _BAD.finditer(txt):
            # allow explicit /tmp scratch (still synthetic)
            frag = txt[m.start():m.start() + 80]
            if re.search(r"[\"'](/tmp|/dev/null)", frag):
                continue
            offenders.append(f"{f.relative_to(_HERE)}: {frag.splitlines()[0][:70]}")
    assert not offenders, (
        "Tests must read only synthetic / tmp_path data (DUA). Offending reads:\n  "
        + "\n  ".join(offenders)
    )
