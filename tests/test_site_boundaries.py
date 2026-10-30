import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class SiteBoundaryTests(unittest.TestCase):
    def test_native_builder_setting_preserves_native_entrypoints(self):
        wrapper = load('native_capability_wrapper', 'capability.py')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'capability.json').write_text(json.dumps({'id':'example','display_name':'Example','kind':'skill','promise':'Example','site_builder':'native'}))
            for operation in ('build', 'check'):
                with patch.object(wrapper, 'ROOT', root), patch.object(sys, 'argv', ['capability.py',operation]), patch.object(wrapper.subprocess, 'run') as run:
                    run.return_value.returncode = 7
                    self.assertEqual(wrapper.main(), 7)
                    self.assertEqual(run.call_args.args[0], [sys.executable,str(root / 'scripts' / (operation+'.py'))])

    def test_private_research_is_outside_release_hygiene_scan(self):
        checker = load('site_privacy_checker', 'check.py')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'.research/market').mkdir(parents=True)
            (root/'.research/market/private.md').write_text('fictional' + chr(64) + 'example.test')
            (root/'README.md').write_text('Public fictional example')
            with patch.object(checker,'ROOT',root):
                self.assertEqual(checker.check_personal_information(),1)

    def test_hygiene_error_does_not_echo_credential_like_text(self):
        checker = load('site_redacted_checker', 'check.py')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            marker='fictional_fixture_value_12345'
            (root/'README.md').write_text('token='+marker)
            with patch.object(checker,'ROOT',root), self.assertRaises(AssertionError) as error:
                checker.check_personal_information()
            self.assertIn('credential',str(error.exception))
            self.assertNotIn(marker,str(error.exception))

if __name__=='__main__':unittest.main()
