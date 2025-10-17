import tempfile
import subprocess
import os
import shlex
import pathlib


# WARNING: This is a *minimal* sandbox. For production use, run inside a Docker container
# with resource limits and NO network access. The local sandbox below creates a tempdir,
# writes the script, and invokes it with a timeout.


def run_python_script(code: str, timeout: int = 10):
with tempfile.TemporaryDirectory() as td:
script_path = os.path.join(td, "script.py")
with open(script_path, "w", encoding="utf-8") as f:
f.write(code)
# Run with `python -I` (isolated) to reduce PYTHONPATH skinning
proc = subprocess.run(["python", "-I", script_path], capture_output=True, text=True, timeout=timeout)
return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def run_powershell_script(code: str, timeout: int = 10):
# On non-Windows hosts, powershell core may be pwsh
pwsh = shutil.which('pwsh') or shutil.which('powershell')
if pwsh is None:
return {"error": "PowerShell not found on this host."}
with tempfile.TemporaryDirectory() as td:
script_path = os.path.join(td, "script.ps1")
with open(script_path, "w", encoding="utf-8") as f:
f.write(code)
proc = subprocess.run([pwsh, "-File", script_path], capture_output=True, text=True, timeout=timeout)
return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}