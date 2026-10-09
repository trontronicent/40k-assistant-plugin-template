"""The code shape a Strategicum plugin keeps: no function that does too much, takes too many arguments or hides a
zip length mismatch (`ruff.toml`, the same limits as the app and the No Man's Sky plugin). The test runs ruff when
it is installed (the 40k Assistant's venv has it) and fails with the findings, so a smell comes back as a red test
and not as a slow decay.

This template contributes no Python today, so the check is empty — and that is the point: it is here on day one, so
the first backend module you add is already under the standard."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def _ruff() -> list[str] | None:
    """How to run ruff here: the module of this interpreter, else a ruff on the PATH, else None."""
    probe = subprocess.run([sys.executable, "-m", "ruff", "--version"], capture_output=True, text=True)
    if probe.returncode == 0:
        return [sys.executable, "-m", "ruff"]
    found = shutil.which("ruff")
    return [found] if found else None


def test_the_plugin_keeps_its_code_shape():
    """ruff (ruff.toml: complexity <= 12, <= 50 statements, <= 6 arguments, explicit zip strictness, no unused names
    or arguments) reports nothing for the whole repository.

    Expected: exit 0 with no findings. It matters because every plugin feature wants to add one more branch to the
    function that is already there; this is what stops that."""
    ruff = _ruff()
    if ruff is None:
        pytest.skip("ruff is not installed")
    res = subprocess.run([*ruff, "check", ".", "--output-format", "concise"],
                         cwd=ROOT, capture_output=True, text=True)
    assert res.returncode == 0, "code shape findings:\n" + res.stdout
