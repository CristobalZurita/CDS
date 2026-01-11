import os
import subprocess


def test_scan_unsafe_script_runs_and_finds_no_issues():
    """Run tools/scan_unsafe.sh and ensure it exits 0 (no matches).
    This protects against committing unsafe patterns like eval/new Function/innerHTML.
    """
    here = os.path.dirname(__file__)
    script = os.path.abspath(os.path.join(here, '..', 'tools', 'scan_unsafe.sh'))
    # fall back to repo-level tools/ path if tests are executed from other working dirs
    if not os.path.exists(script):
        script = os.path.abspath(os.path.join(here, '..', '..', 'tools', 'scan_unsafe.sh'))

    proc = subprocess.run(["bash", script])
    assert proc.returncode == 0, "tools/scan_unsafe.sh detected unsafe patterns; fix or justify them"
