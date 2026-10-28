"""Structural audit checks catch missing sources, paths, interfaces and gates.

The positive record is authored scaffolding, not a model audit or semantic pass.
"""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'skills/right-shape/scripts'))
from validate_audit import validate_audit


def fixture():
    inventory=json.loads((ROOT/'evals/audit-forward/sources.json').read_text())
    sources=[];caps=[];routes=[];methods=[]
    for source in inventory['repositories']:
        sid=source['id'];fork=source['metadata']['fork']
        sources.append({'id':sid,'revision':source['revision'],'scope':'public',
                        'primary_disposition':'Fork'if fork else'Keep','bucket':sid+': retained existing home'})
        caps.append({'id':sid,'kind':'asset','promise':'Authored structural fixture for '+sid,'shape':'Retained asset','placement':None})
        paths=list(source['files'])
        routes.append({'capability_id':sid,'source_id':sid,'source_revision':source['revision'],
                       'source_paths':paths,'target_repo':sid,'target_path':'.','target_status':'existing',
                       'action':'Fork'if fork else'Keep','role':'reference',
                       'interface':'Retained source files; no consumer migration or new interface claimed.',
                       'reason':'Structural positive fixture only; not a proposed portfolio design.'})
        for path in paths:
            if Path(path).name.lower()=='skill.md':methods.append({'source_id':sid,'path':path,'destination':sid+': retained source','provenance':'upstream fixture'if fork else'fixture source; authorship not independently established'})
    caps.append({'id':'note-review','kind':'public','promise':'Review one note against its author’s brief.','shape':'Skill',
                 'placement':{'need':[1,1,0,0],'failed':[],'checks':[],'engine':'LLM','rung':2}})
    routes.append({'capability_id':'note-review','source_id':'workpad','source_revision':'fixture-r1','source_paths':['skills/review/SKILL.md'],
                   'target_repo':'workpad','target_path':'skills/review','target_status':'existing','action':'Keep','role':'method',
                   'interface':'Note and author brief -> source-bound observations and one reversible proposal; no send or publish.','reason':'Authored fixture exercises public placement validation.'})
    return {'schema_version':'right-shape-audit/v1','sources':sources,'capabilities':caps,'routes':routes,'method_routes':methods},inventory


class AuditRecordTests(unittest.TestCase):
    def test_authored_structural_fixture_accounts_for_sources_and_methods(self):
        report,inventory=fixture();result=validate_audit(report,inventory)
        self.assertEqual((result['sources'],result['embedded_methods']),(6,3))
        self.assertIn('semantic review',result['scope'])

    def test_missing_source_is_rejected(self):
        report,inventory=fixture();report['sources'].pop()
        with self.assertRaisesRegex(ValueError,'census coverage'):validate_audit(report,inventory)

    def test_embedded_method_drop_is_rejected(self):
        report,inventory=fixture();report['method_routes'].pop()
        with self.assertRaisesRegex(ValueError,'method coverage'):validate_audit(report,inventory)

    def test_directory_paths_can_be_checked_from_children_but_invented_paths_fail(self):
        report,inventory=fixture();report['routes'][0]['source_paths']=['src/']
        validate_audit(report,inventory)
        report['routes'][0]['source_paths']=['not-present.py']
        with self.assertRaisesRegex(ValueError,'path absent'):validate_audit(report,inventory)

    def test_empty_interface_and_unknown_target_state_are_rejected(self):
        for key,value,match in [('interface','','non-empty'),('target_status','already-migrated','target status')]:
            report,inventory=fixture();report['routes'][0][key]=value
            with self.assertRaisesRegex(ValueError,match):validate_audit(report,inventory)

    def test_fork_status_is_not_erased_by_a_generic_disposition(self):
        report,inventory=fixture();next(x for x in report['sources']if x['id']=='upstream-widget')['primary_disposition']='Separate'
        with self.assertRaisesRegex(ValueError,'Confirmed fork'):validate_audit(report,inventory)

    def test_public_placement_is_required_and_arithmetic_is_checked(self):
        for placement in [None,{'need':[3,3,3,3],'failed':['G2','G5'],'checks':[],'engine':'LLM','ceiling':7,'rung':6,'honest_move':'Lower the need.'}]:
            report,inventory=fixture();report['capabilities'][-1]['placement']=placement
            with self.assertRaises(ValueError):validate_audit(report,inventory)

    def test_source_and_route_revisions_must_match_inventory(self):
        for container in ['sources','routes']:
            report,inventory=fixture();key='revision'if container=='sources'else'source_revision';report[container][0][key]='unseen-revision'
            with self.assertRaisesRegex(ValueError,'revision mismatch'):validate_audit(report,inventory)


if __name__=='__main__':unittest.main()
