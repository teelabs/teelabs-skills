import importlib.util
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).parents[1] / "scripts" / "audit_local_disclosures.py"
spec = importlib.util.spec_from_file_location("audit_local_disclosures", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class LocalDisclosureScanTests(unittest.TestCase):
    def test_detects_home_directory_without_echoing_match(self):
        source = "safe\nSee /home/example-user/work/app/config.json\n"
        findings = module.find_candidates(source)
        self.assertEqual([(2, "posix-home")], findings)
        report = module.format_findings("file-1", findings)
        self.assertIn("file-1:2", report)
        self.assertIn("posix-home", report)
        self.assertNotIn("example-user", report)
        self.assertNotIn("config.json", report)

    def test_detects_windows_user_profile(self):
        self.assertEqual([(1, "windows-profile")], module.find_candidates(r"Open C:\Users\example\AppData\Local\tool"))

    def test_detects_home_file_uri(self):
        self.assertEqual([(1, "home-file-uri")], module.find_candidates("file:///Users/example/private/data.db"))

    def test_detects_environment_expansions_without_echoing_them(self):
        source = 'Use "$HOME/data" and "$PWD/build"; account=${USER}'
        findings = module.find_candidates(source)
        self.assertEqual(
            [(1, "home-variable"), (1, "working-directory-variable"), (1, "account-variable")],
            findings,
        )
        report = module.format_findings("docs/setup.md", findings)
        self.assertNotIn("$HOME", report)
        self.assertNotIn("$PWD", report)
        self.assertNotIn("${USER}", report)

    def test_detects_additional_platform_path_variables(self):
        source = "tmp=$TMPDIR config=${XDG_CONFIG_HOME}; temp=%TEMP%; drive=%HOMEDRIVE%%HOMEPATH%"
        findings = module.find_candidates(source)
        self.assertEqual(
            [
                (1, "temporary-directory-variable"),
                (1, "xdg-config-variable"),
                (1, "windows-temp-variable"),
                (1, "windows-home-drive-variable"),
                (1, "windows-home-path-variable"),
            ],
            findings,
        )

    def test_report_withholds_sensitive_source_names(self):
        report = module.format_findings("private-project-plan.md", [(4, "posix-home")])
        self.assertNotIn("private-project-plan", report)
        self.assertIn(":4 candidate=posix-home", report)

    def test_keeps_repository_relative_paths_clean(self):
        self.assertEqual([], module.find_candidates("Read docs/setup.md and packages/storage/src/index.ts"))

    def test_stdin_report_never_contains_source_text(self):
        source = "~/private/repo/.env"
        findings = module.find_candidates(source)
        report = module.format_findings("stdin", findings)
        self.assertNotIn(source, report)
        self.assertNotIn(".env", report)

    def test_staged_scan_checks_full_blob_not_only_added_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = pathlib.Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "Audit Test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "audit@example.invalid"], cwd=repo, check=True)
            doc = repo / "README.md"
            doc.write_text("See /home/example-user/private/config.json\nold text\n")
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "baseline"], cwd=repo, check=True)
            doc.write_text("See /home/example-user/private/config.json\nupdated text\n")
            subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
            result = subprocess.run(
                ["python3", str(SCRIPT), "--staged"], cwd=repo, check=False,
                capture_output=True, text=True,
            )
            self.assertEqual(1, result.returncode)
            self.assertIn("staged-1:1 candidate=posix-home", result.stdout)
            self.assertNotIn("example-user", result.stdout)
            self.assertNotIn("config.json", result.stdout)


if __name__ == "__main__":
    unittest.main()
