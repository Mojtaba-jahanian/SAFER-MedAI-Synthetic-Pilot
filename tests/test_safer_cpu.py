"""Stage02C-0 unit/invariant tests. NEVER uses registered pilot/confirmation seeds."""
import dataclasses
import itertools
import math
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from safer_cpu import (load_config,derived_seed,radius_hoeffding_anytime,
 reference_discrepancy_radius,mixture_box,extreme_simplex,SyntheticEnvironment,
 EvidenceLedger,Action,choose_action,eligible_actions,projected_upper,run_episode,EvidenceView)
C=load_config(ROOT/'configs'/'02B_FROZEN_DESIGN.json')
W={x['id']:x for x in C['worlds']}


def make(world='W3_reference_gap',seed=81234,budget=2600):
    ww=W[world]
    env=SyntheticEnvironment(ww,seed,C)
    return env,EvidenceLedger(env,ww,C,budget)


class ConfigTests(unittest.TestCase):
    def test_frozen_identity(self):
        self.assertEqual(C['id'],'SAFER-J4-02B-SYNTHETIC-CRN-v1.0')
    def test_budget_seeds_not_reused(self):
        p=C['randomization']['pilot_seeds']; q=C['randomization']['confirmatory_seeds']
        self.assertTrue(p['start']+p['count']<=q['start'])
        self.assertEqual([x['id'][:2] for x in C['worlds']], ['W1','W2','W3','W4','W5'])
    def test_sealed_seeds(self):
        for seed in (600000,600099,700000,700999):
            with self.assertRaisesRegex(ValueError,'SEALED'):
                run_episode(C,W['W1_supported_low'],seed,800,'P0')
    def test_deterministic_seed_derivation(self):
        self.assertEqual(derived_seed(123,'W1','source',0),derived_seed(123,'W1','source',0))
        self.assertNotEqual(derived_seed(123,'W1','source',0),derived_seed(123,'W1','ref_pair',0))
        self.assertNotEqual(derived_seed(123,'W1','source',0),derived_seed(124,'W1','source',0))
    def test_cost_schema(self):
        self.assertEqual((C['action_types']['A1']['batch_size'],C['action_types']['A2']['cost_units'],C['action_types']['A3']['cost_units']), (20,120,350))


class FormulaTests(unittest.TestCase):
    def test_time_uniform_formula(self):
        k,n,delta=3,100,.025
        want=math.sqrt(math.log(2*k*n*(n+1)/delta)/(2*n))
        self.assertAlmostEqual(radius_hoeffding_anytime(k,n,delta),want,places=14)
    def test_reference_formula(self):
        self.assertAlmostEqual(reference_discrepancy_radius(2,120,.01),math.sqrt(math.log(400)/240))
    def test_mass_bounds(self):
        wh,lo,hi=mixture_box((6800,3200),.015)
        self.assertAlmostEqual(sum(wh),1)
        self.assertTrue(all(l<=w<=h for l,w,h in zip(lo,wh,hi)))
        self.assertLessEqual(sum(lo),1)
        self.assertGreaterEqual(sum(hi),1)
    def test_simplex_manual(self):
        values=(.1,.9); lo=(.2,.1); hi=(.6,.8)
        self.assertAlmostEqual(extreme_simplex(values,lo,hi,True),.1*.2+.9*.8)
        self.assertAlmostEqual(extreme_simplex(values,lo,hi,False),.1*.6+.9*.4)
    def test_simplex_bruteforce_vertices(self):
        # independent vertex enumeration for 2-, 3-, 4-stratum bounded simplex
        for d in (2,3,4):
            for iteration in range(20):
                weights=tuple((j+1+iteration%3)/sum(range(1,d+1)) for j in range(d))
                weights=tuple(w/sum(weights) for w in weights)
                low=tuple(max(0,w-.07) for w in weights)
                high=tuple(min(1,w+.09) for w in weights)
                values=tuple((j*7+iteration*3)%17/16 for j in range(d))
                vertices=[]
                for free in range(d):
                    others=[j for j in range(d) if j!=free]
                    for choices in itertools.product((0,1),repeat=d-1):
                        v=[0.0]*d
                        for j,bit in zip(others,choices):
                            v[j]=high[j] if bit else low[j]
                        v[free]=1-sum(v)
                        if low[free]-1e-9 <= v[free] <= high[free]+1e-9:
                            vertices.append(sum(a*b for a,b in zip(v,values)))
                self.assertTrue(vertices)
                self.assertAlmostEqual(extreme_simplex(values,low,high,True),max(vertices),places=9)
                self.assertAlmostEqual(extreme_simplex(values,low,high,False),min(vertices),places=9)
    def test_infeasible_weights_fail_closed(self):
        with self.assertRaises(ValueError):
            extreme_simplex((.1,.2),(.6,.6),(.9,.9),True)


class GateAndActionTests(unittest.TestCase):
    def test_warmstart_cost_and_sample_unit(self):
        env,l=make('W1_supported_low')
        self.assertEqual(l.cost_spent,40)
        self.assertEqual(l.n,[20,20])
        self.assertTrue(env.uniqueness_audit())
    def test_reference_gap_structural(self):
        _,l=make('W3_reference_gap')
        v=l.snapshot()
        self.assertFalse(v.reference_verified[1])
        self.assertEqual(v.bounds_hi[1],1)
        self.assertGreater(v.structural_floor,.3)
        self.assertEqual(v.raw_decision,'STRUCTURAL_BLOCK')
    def test_support_gap_structural(self):
        _,l=make('W4_support_gap')
        v=l.snapshot()
        self.assertFalse(v.source_eligible[2])
        self.assertEqual(v.n[2],0)
        self.assertEqual(v.bounds_hi[2],1)
        self.assertGreater(v.structural_floor,.3)
    def test_repair_first_p5_a2(self):
        _,l=make('W3_reference_gap')
        a=choose_action(l.snapshot(),'P5')
        self.assertEqual((a.kind,a.stratum,a.cost),('A2',1,120))
    def test_cost_aware_p4_has_only_a2_on_w3(self):
        _,l=make('W3_reference_gap')
        self.assertEqual({a.kind for a in eligible_actions(l.snapshot(),True)}, {'A2'})
        self.assertEqual(choose_action(l.snapshot(),'P4').kind,'A2')
    def test_a2_observed_data_and_once_only(self):
        env,l=make('W3_reference_gap')
        before=l.snapshot()
        after=l.execute(Action('A2',1,120))
        self.assertEqual(l.cost_spent, before.cost_spent+120)
        self.assertTrue(after.a2_performed[1])
        self.assertTrue(after.reference_verified[1])
        self.assertLessEqual(0,after.ref_upper[1]);self.assertLessEqual(after.ref_upper[1],1)
        with self.assertRaises(ValueError): l.execute(Action('A2',1,120))
        self.assertTrue(env.uniqueness_audit())
    def test_a3_only_opens_access_without_free_labels(self):
        _,l=make('W4_support_gap')
        before=l.snapshot()
        after=l.execute(Action('A3',2,350))
        self.assertEqual(after.n[2],0)
        self.assertEqual(after.bounds_hi[2],1)
        self.assertTrue(after.source_eligible[2])
        self.assertEqual(l.cost_spent,before.cost_spent+350)
        l.execute(Action('A1',2,20))
        self.assertEqual(l.n[2],20)
    def test_no_a1_through_blocked_reference(self):
        _,l=make('W3_reference_gap')
        with self.assertRaises(ValueError):l.execute(Action('A1',1,20))
    def test_no_a1_through_unsupported(self):
        _,l=make('W4_support_gap')
        with self.assertRaises(ValueError):l.execute(Action('A1',2,20))
    def test_no_a3_reuse(self):
        _,l=make('W4_support_gap')
        l.execute(Action('A3',2,350))
        with self.assertRaises(ValueError):l.execute(Action('A3',2,350))
    def test_budget_never_exceeded(self):
        _,l=make('W1_supported_low',budget=800)
        for _ in range(38):
            l.execute(Action('A1',0,20))
        self.assertEqual(l.cost_spent,800)
        with self.assertRaises(ValueError):l.execute(Action('A1',0,20))
    def test_action_order_tie_break(self):
        _,l=make('W1_supported_low')
        v=l.snapshot()
        self.assertEqual((choose_action(v,'P0').kind,choose_action(v,'P0').stratum),('A1',0))
    def test_projected_a1_uses_smoothed_mean_not_truth(self):
        _,l=make('W1_supported_low')
        v=l.snapshot()
        a=Action('A1',0,20)
        project=projected_upper(v,a)
        self.assertTrue(math.isfinite(project))
        self.assertGreaterEqual(project,0)
        self.assertLessEqual(project,1)
    def test_policy_interface_has_no_generator_truth(self):
        fields={f.name for f in dataclasses.fields(EvidenceView)}
        forbidden={'weak_loss_probabilities','reference_mismatch_probabilities','target_masses','source_masses','truth','world','env','future_samples'}
        self.assertFalse(fields & forbidden)
    def test_all_four_states_constructive_math_fixtures(self):
        # Explicit formula verification, NOT simulated experimental outcomes.
        _,c=make('W1_supported_low')
        self.assertEqual(c.snapshot().raw_decision,'UNRESOLVED')
        c.n[:]=[100000,100000];c.successes[:]=[5000,5000]
        self.assertEqual(c.snapshot().raw_decision,'CERTIFY')
        c.successes[:]=[80000,70000]
        self.assertEqual(c.snapshot().raw_decision,'HIGH_RISK')
        _,blocked=make('W3_reference_gap')
        self.assertEqual(blocked.snapshot().raw_decision,'STRUCTURAL_BLOCK')

    def test_state_four_branch_precedence(self):
        _,l=make('W1_supported_low')
        v=l.snapshot()
        self.assertIn(v.raw_decision,{'CERTIFY','HIGH_RISK','STRUCTURAL_BLOCK','UNRESOLVED'})
        self.assertTrue(v.risk_lo<=v.risk_hi+1e-12)
    def test_crn_same_first_labels_across_policies(self):
        _,x=make('W1_supported_low',seed=81111)
        _,y=make('W1_supported_low',seed=81111)
        self.assertEqual(x.n,y.n)
        self.assertEqual(x.successes,y.successes)
        x.execute(Action('A1',0,20)); y.execute(Action('A1',0,20))
        self.assertEqual(x.successes,y.successes)
    def test_crn_mixture_same_for_shared_world_seed(self):
        e1,_=make('W2_composition_shift',seed=41000)
        e2,_=make('W2_composition_shift',seed=41000)
        self.assertEqual(e1.counts,e2.counts)
    def test_a1_stratum_patient_ids_unique(self):
        e,l=make('W1_supported_low',seed=81444)
        for _ in range(10): l.execute(Action('A1',0,20))
        self.assertEqual(len(e._source_patient_ids),240)
        self.assertTrue(e.uniqueness_audit())
    def test_truth_only_accessible_from_env_for_scoring(self):
        _,l=make('W3_reference_gap')
        self.assertFalse(hasattr(l.snapshot(),'truth_after_stop'))
    def test_frozen_action_price_enforced(self):
        _,l=make('W3_reference_gap')
        cost=l.cost_spent
        with self.assertRaises(ValueError):l.execute(Action('A2',1,1))
        self.assertEqual(cost,l.cost_spent)

    def test_no_false_repair_from_predictions(self):
        # Plans cannot alter reference compatibility without observed A2.
        _,l=make('W3_reference_gap')
        before=l.snapshot()
        a=choose_action(before,'P4')
        self.assertFalse(before.reference_verified[1])
        self.assertFalse(l.snapshot().reference_verified[1])
        self.assertEqual(a.kind,'A2')
        self.assertFalse(l.a2_performed[1])

    def test_independent_reference_stream_no_patient_overlap(self):
        env,l=make('W3_reference_gap')
        l.execute(Action('A2',1,120))
        self.assertEqual(len(env._audit_patient_ids),120)
        self.assertFalse(env._audit_patient_ids & env._source_patient_ids)
        self.assertTrue(env.uniqueness_audit())

    def test_bad_action_not_paid(self):
        _,l=make('W3_reference_gap')
        cost=l.cost_spent
        with self.assertRaises(ValueError):l.execute(Action('A3',0,350))
        self.assertEqual(l.cost_spent,cost)


class EpisodeSmokeTests(unittest.TestCase):
    def test_smoke_two_worlds_policy_actions(self):
        # Distinct internal preflight seeds; NOT registered pilot seeds.
        for name,policy in [('W1_supported_low','P4'),('W3_reference_gap','P5'),('W4_support_gap','P4')]:
            metric,trace=run_episode(C,W[name],91234,800,policy)
            self.assertLessEqual(metric.total_cost,metric.budget)
            self.assertTrue(metric.unique_patient_ids)
            self.assertIn(metric.final_state,{'CERTIFY','HIGH_RISK','STRUCTURAL_BLOCK','UNRESOLVED'})
            self.assertEqual(metric.n_a2,sum(x['action']=='A2' for x in trace))
            self.assertEqual(metric.n_a3,sum(x['action']=='A3' for x in trace))
    def test_reproducibility_same_inputs(self):
        a,ta=run_episode(C,W['W3_reference_gap'],81234,800,'P4')
        b,tb=run_episode(C,W['W3_reference_gap'],81234,800,'P4')
        self.assertEqual(a,b)
        self.assertEqual(ta,tb)
    def test_p6_is_safer_a1_only_not_uniform_alias(self):
        # Fixed observable test state constructed without registered seeds.
        _, ledger = make('W1_supported_low', seed=81239)
        v = ledger.snapshot()
        from dataclasses import replace
        # The non-uniform state makes P0 prefer stratum 0 by count,
        # while the P4 one-step improvement should prefer stratum 1.
        v=replace(v, n=(20,40), successes=(0,20),
                  bounds_hi=(0.7,0.9), risk_hi=0.93)
        a=choose_action(v,'P6')
        self.assertEqual(a.kind,'A1')
        a1s=[x for x in eligible_actions(v,False) if x.kind=='A1']
        gains=[(max(0.,v.risk_hi-projected_upper(v,x))/x.cost,x.stratum) for x in a1s]
        top=max(y[0] for y in gains)
        expected=min(i for u,i in gains if abs(u-top)<=1e-14)
        self.assertEqual(a.stratum,expected)
        self.assertTrue(all(x.kind=='A1' for x in eligible_actions(v,False)))

    def test_all_policy_names_small_smoke(self):
        for policy in ('P0','P1','P2','P3','P4','P5','P6'):
            result,_=run_episode(C,W['W1_supported_low'],81235,800,policy)
            self.assertTrue(result.unique_patient_ids)


if __name__=='__main__': unittest.main(verbosity=2)
