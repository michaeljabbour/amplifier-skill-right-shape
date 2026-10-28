"""Regression tests for arithmetic errors observed in model-authored cards."""
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/right-shape/scripts'))
from validate_placement import place, read_rubric, validate


class PlacementTests(unittest.TestCase):
    def base(self,**updates):
        return {'id':'fictional','need':[3,3,3,3],'failed':['G2','G5'],
                'checks':[],'engine':'LLM','honest_move':'Require approval before irreversible calls.',**updates}

    def test_lowest_failed_cap_wins(self):
        result=validate(self.base())
        self.assertEqual((result['need_score'],result['need_rung'],result['ceiling'],result['maximum_rung']),(12,8,6,6))
        with self.assertRaisesRegex(ValueError,'claimed ceiling'):
            validate(self.base(ceiling=7))

    def test_all_failed_gates_do_not_invent_rung_one_cap(self):
        result=validate(self.base(failed=['G1','G2','G3','G4','G5','G6']))
        self.assertEqual(result['ceiling'],5)
        with self.assertRaisesRegex(ValueError,'claimed ceiling'):
            validate(self.base(failed=['G1','G2','G3','G4','G5','G6'],ceiling=1))

    def test_no_failed_gate_does_not_invent_a_ceiling(self):
        result=validate(self.base(failed=[],honest_move=''))
        self.assertEqual(result['ceiling'],9)
        with self.assertRaisesRegex(ValueError,'claimed ceiling'):
            validate(self.base(failed=[],honest_move='',ceiling=6))

    def test_composition_cannot_raise_a_cap(self):
        for checks in [[],['H1'],['H1','H2'],['H1','H2','H3','H4']]:
            with self.assertRaisesRegex(ValueError,'above'):
                validate(self.base(checks=checks,rung=7))

    def test_h4_alone_is_decompose_first(self):
        self.assertTrue(validate(self.base(checks=['H4']))['decompose_first'])

    def test_duplicate_checks_do_not_create_a_harness(self):
        with self.assertRaisesRegex(ValueError,'unique IDs'):validate(self.base(checks=['H1','H1']))

    def test_observed_application_failures_stay_failures(self):
        record=json.loads((ROOT/'docs/evaluations/2026-10-28/arithmetic-regression/observed-failures.json').read_text())
        for row in record['observations']:
            need=row['reported_need']
            with self.assertRaisesRegex(ValueError,'claimed ceiling'):
                validate(self.base(need=[need[f'N{i}']for i in range(1,5)],failed=row['reported_failed_gates'],
                                   need_score=need['total'],need_rung=need['rung'],ceiling=row['reported_ceiling'],rung=row['reported_placed_rung']))

    def test_need_claims_and_rung_types(self):
        for updates in [{'need_score':11},{'need_rung':7},{'rung':-1},{'rung':10},{'rung':True},{'need':[True,1,1,1]}]:
            with self.assertRaises(ValueError):validate(self.base(**updates))

    def test_lower_rung_needs_reason_and_honest_move(self):
        with self.assertRaisesRegex(ValueError,'tiebreak'):validate(self.base(rung=2))
        with self.assertRaisesRegex(ValueError,'honest move'):validate(self.base(honest_move=''))
        self.assertEqual(validate(self.base(rung=2,tiebreak='Use the bounded manual version.'))['placement_rung'],2)

    def test_all_need_vectors_and_gate_subsets_respect_each_cap(self):
        rules=read_rubric((ROOT/'skills/right-shape/references/rubric.md').read_text())
        for need in itertools.product(range(4),repeat=4):
            for bits in itertools.product([False,True],repeat=6):
                failed=[f'G{i+1}'for i,b in enumerate(bits)if b]
                sample=self.base(need=list(need),failed=failed,honest_move='')
                try:score,wanted,ceiling,_=place(sample,rules)
                except ValueError as error:
                    self.assertIn('honest move',str(error));sample['honest_move']='Lower the need.'
                    score,wanted,ceiling,_=place(sample,rules)
                self.assertEqual(score,sum(need))
                for gate in failed:self.assertLessEqual(ceiling,rules['caps'][gate])
                self.assertLessEqual(min(wanted,ceiling),ceiling)

    def test_cli_works_from_copied_portable_folder(self):
        from shutil import copytree
        with tempfile.TemporaryDirectory()as dest:
            folder=Path(dest)/'right-shape';copytree(ROOT/'skills/right-shape',folder,ignore=lambda p,n:['__pycache__']if'__pycache__'in n else[])
            result=subprocess.run([sys.executable,str(folder/'scripts/validate_placement.py')],input=json.dumps(self.base()),text=True,capture_output=True,cwd=dest)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['ceiling'],6)
            bad=subprocess.run([sys.executable,str(folder/'scripts/validate_placement.py')],input=json.dumps(self.base(ceiling=7)),text=True,capture_output=True,cwd=dest)
            self.assertEqual(bad.returncode,2)


if __name__=='__main__':unittest.main()
