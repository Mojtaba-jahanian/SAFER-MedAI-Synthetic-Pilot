"""SAFER-MedAI Stage 02C-0: prospective synthetic CPU reference implementation.

Never represent this code as recovered historical SAFER code or as clinical validation.
Only bounded patient streams in an independently specified synthetic simulator.
All 02B experiment/confirmatory seeds are forbidden by default in this module.

The policy API receives EvidenceView ONLY; latent generator worlds, target masses,
future outcomes, and scoring truth are held exclusively in SyntheticEnvironment.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

ALLOWED_POLICY_IDS = tuple(f"P{i}" for i in range(7))
ACTION_ORDER = {"A1": 0, "A2": 1, "A3": 2}
STATES = {"CERTIFY", "HIGH_RISK", "STRUCTURAL_BLOCK", "UNRESOLVED"}


def load_config(path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    assert config["id"] == "SAFER-J4-02B-SYNTHETIC-CRN-v1.0"
    assert config["delta_allocation"]["target_mass"] + config["delta_allocation"]["conditional_loss"] + config["delta_allocation"]["reference_discrepancy"] == config["delta_total"]
    return config


def derived_seed(seed: int, world_id: str, stream: str, stratum: int = -1) -> int:
    message = f"safer-j4-v1|{seed}|{world_id}|{stream}|{stratum}".encode()
    return int.from_bytes(hashlib.sha256(message).digest()[:16], "big")


def radius_hoeffding_anytime(k: int, n: int, delta_r: float):
    """Manuscript Eq.(9), K fixed *including* inaccessible prespecified strata."""
    if n <= 0:
        return 1.0
    return math.sqrt(math.log(2 * k * n * (n + 1) / delta_r) / (2 * n))


def reference_discrepancy_radius(k: int, n: int, delta_c: float):
    """Frozen 02B one-shot reference confidence, with full stratum multiplicity."""
    return math.sqrt(math.log(2 * k / delta_c) / (2 * n))


def mixture_box(counts: Tuple[int, ...], delta_w: float):
    """Manuscript Eq.(7)--(8): simultaneous box intersected with simplex."""
    m = sum(counts)
    if m <= 0:
        raise ValueError("Target mixture requires positive independent target sample")
    k = len(counts)
    eps = math.sqrt(math.log(2 * k / delta_w) / (2 * m))
    w_hat = tuple(c / m for c in counts)
    lo = tuple(max(0.0, w - eps) for w in w_hat)
    hi = tuple(min(1.0, w + eps) for w in w_hat)
    if sum(lo) > 1 + 1e-12 or sum(hi) < 1 - 1e-12:
        raise ValueError("Empty mixture feasible simplex")
    return w_hat, lo, hi


def extreme_simplex(values: Tuple[float, ...], lo: Tuple[float, ...],
                    hi: Tuple[float, ...], maximize: bool) -> float:
    """Manuscript Algorithm 1: exact bounded-simplex greedy LP."""
    if not (len(values) == len(lo) == len(hi)):
        raise ValueError("Mismatched lengths")
    if any(x < -1e-12 or x > y + 1e-12 or y > 1+1e-12 for x, y in zip(lo, hi)):
        raise ValueError("Invalid mass bounds")
    if sum(lo) > 1 + 1e-10 or sum(hi) < 1 - 1e-10:
        raise ValueError("Infeasible simplex")
    mass = list(lo)
    remaining = max(0.0, 1.0 - sum(mass))
    # Stable ties on stratum index, no policy-dependent ordering.
    order = sorted(range(len(values)), key=lambda i: (-values[i] if maximize else values[i], i))
    for i in order:
        add = min(remaining, hi[i] - mass[i])
        mass[i] += add
        remaining -= add
        if remaining < 1e-11:
            break
    if remaining > 1e-9:
        raise ValueError("Incomplete simplex allocation")
    return sum(v*w for v,w in zip(values,mass))


@dataclass(frozen=True)
class EvidenceView:
    """Non-oracle public policy interface. No world, generator or truth fields."""
    alpha: float
    budget_remaining: int
    cost_spent: int
    k: int
    delta_r: float
    delta_c: float
    w_hat: Tuple[float, ...]
    w_lo: Tuple[float, ...]
    w_hi: Tuple[float, ...]
    n: Tuple[int, ...]
    successes: Tuple[int, ...]
    source_eligible: Tuple[bool, ...]
    reference_verified: Tuple[bool, ...]
    ref_upper: Tuple[float, ...]
    a2_performed: Tuple[bool, ...]
    a3_performed: Tuple[bool, ...]
    bounds_lo: Tuple[float, ...]
    bounds_hi: Tuple[float, ...]
    risk_lo: float
    risk_hi: float
    structural_floor: float
    raw_decision: str
    a1_batch_cost: int
    a2_cost: int
    a3_cost: int
    a1_batch: int


@dataclass(frozen=True)
class Action:
    kind: str
    stratum: int
    cost: int
    predicted_utility: float = 0.0


class SyntheticEnvironment:
    """Generator and scoring truth; policy never receives this object.

    Per-world/seed stream RNGs are identical across policies and budgets.
    Independent source, reference audit, direct target patient and mass streams.
    """
    def __init__(self, world: dict, seed: int, config: dict):
        self._world = world
        self._seed = seed
        self._k = len(world["target_masses"])
        self._counts = self._draw_masses(config)
        self._rngs = {}
        self._draw_counts = {}
        self._source_patient_ids = set()
        self._direct_patient_ids = set()
        self._audit_patient_ids = set()
        self._all_patient_ids = set()

    @property
    def counts(self):
        return self._counts

    def _draw_masses(self, config):
        m = config["mixture_estimation"]["independent_target_covariate_draws_per_episode"]
        # This method is held outside policy scope; policies receive only counts.
        probs = self._world["target_masses"]
        edges = []
        acc = 0.0
        for p in probs:
            acc += p
            edges.append(acc)
        rng = random.Random(derived_seed(self._seed, self._world["id"], "target_mass"))
        counts = [0] * len(probs)
        for _ in range(m):
            u = rng.random()
            i = next((j for j, edge in enumerate(edges) if u < edge), len(edges)-1)
            counts[i] += 1
        return tuple(counts)

    def _rng(self, kind, stratum):
        key = (kind, stratum)
        if key not in self._rngs:
            self._rngs[key] = random.Random(derived_seed(self._seed, self._world["id"], kind, stratum))
            self._draw_counts[key] = 0
        return self._rngs[key]

    def _take_patient(self, kind, stratum):
        key = (kind, stratum)
        self._rng(kind, stratum)
        idx = self._draw_counts[key]
        self._draw_counts[key] += 1
        pid = (kind, stratum, idx)
        if pid in self._all_patient_ids:
            raise AssertionError("Duplicated patient within episode")
        self._all_patient_ids.add(pid)
        if kind == "source":
            self._source_patient_ids.add(pid)
        elif kind == "direct_target":
            self._direct_patient_ids.add(pid)
        elif kind == "ref_pair":
            self._audit_patient_ids.add(pid)
        return self._rngs[key], pid

    def draw_a1(self, stratum, n, direct_target: bool):
        kind = "direct_target" if direct_target else "source"
        if not direct_target and stratum in self._world["unsupported_strata"]:
            raise ValueError("Unsupported source stream cannot be sampled")
        result = 0
        for _ in range(n):
            rng, _ = self._take_patient(kind, stratum)
            weak_loss = int(rng.random() < self._world["weak_loss_probabilities"][stratum])
            if direct_target:
                mismatch = int(rng.random() < self._world["reference_mismatch_probabilities"][stratum])
                result += weak_loss ^ mismatch  # direct clinical reference outcome
            else:
                result += weak_loss            # source weak-label outcome
        return result

    def draw_a2(self, stratum, n):
        mismatches = 0
        for _ in range(n):
            rng, _ = self._take_patient("ref_pair", stratum)
            weak_loss = int(rng.random() < self._world["weak_loss_probabilities"][stratum])
            ref_disagrees = int(rng.random() < self._world["reference_mismatch_probabilities"][stratum])
            reference_loss = weak_loss ^ ref_disagrees
            mismatches += int(weak_loss != reference_loss)  # actual synthetic PAIR
        return mismatches

    def scoring_truth(self):
        # Never called from policy; called only after an episode finishes.
        true_clinical_risks = tuple(
            p*(1-q) + (1-p)*q
            for p, q in zip(self._world["weak_loss_probabilities"], self._world["reference_mismatch_probabilities"])
        )
        return sum(w*r for w, r in zip(self._world["target_masses"], true_clinical_risks)), true_clinical_risks

    def uniqueness_audit(self):
        return len(self._all_patient_ids) == sum(map(len, (self._source_patient_ids, self._direct_patient_ids, self._audit_patient_ids)))


class EvidenceLedger:
    def __init__(self, env: SyntheticEnvironment, world: dict, config: dict, budget: int):
        self._config = config
        self._env = env
        self._world_id = world["id"]
        self.k = len(world["target_masses"])
        self.alpha = float(config["alpha_primary"])
        self.delta_w = float(config["delta_allocation"]["target_mass"])
        self.delta_r = float(config["delta_allocation"]["conditional_loss"])
        self.delta_c = float(config["delta_allocation"]["reference_discrepancy"])
        self.batch = int(config["action_types"]["A1"]["batch_size"])
        self.cost_a2 = int(config["action_types"]["A2"]["cost_units"])
        self.cost_a3 = int(config["action_types"]["A3"]["cost_units"])
        self.n_ref = int(config["action_types"]["A2"]["paired_reference_n"])
        self.budget = budget
        self.cost_spent = 0
        self.n = [0]*self.k
        self.successes = [0]*self.k
        self.source_eligible = [i not in world["unsupported_strata"] for i in range(self.k)]
        self.reference_verified = [i not in world["initial_reference_blocked_strata"] for i in range(self.k)]
        self.ref_upper = [0.0 if v else 1.0 for v in self.reference_verified]
        self.a2_performed = [False]*self.k
        self.a3_performed = [False]*self.k
        self.action_history = []
        self.w_hat, self.w_lo, self.w_hi = mixture_box(env.counts, self.delta_w)
        warm_n = int(config["warm_start_labels_per_supported_stratum"])
        for i in range(self.k):
            if self.source_eligible[i]:
                self._charge(warm_n)
                self.successes[i] += self._env.draw_a1(i, warm_n, False)
                self.n[i] += warm_n
                self.action_history.append({"action": "WARM_A1", "stratum": i, "cost": warm_n, "n_post": self.n[i]})

    def _charge(self, amount: int):
        if amount < 1 or self.cost_spent + amount > self.budget:
            raise ValueError("Over-budget or zero-cost action")
        self.cost_spent += amount

    def snapshot(self):
        lo, hi = [], []
        for i in range(self.k):
            if not self.source_eligible[i] or not self.reference_verified[i] or self.n[i] == 0:
                lo.append(0.0); hi.append(1.0)
                continue
            p = self.successes[i] / self.n[i]
            b = radius_hoeffding_anytime(self.k, self.n[i], self.delta_r)
            allowance = 0.0 if self.a3_performed[i] else self.ref_upper[i]
            lo.append(max(0.0, p - b - allowance))
            hi.append(min(1.0, p + b + allowance))
        lo,hi = tuple(lo),tuple(hi)
        rlo = extreme_simplex(lo, self.w_lo, self.w_hi, maximize=False)
        rhi = extreme_simplex(hi, self.w_lo, self.w_hi, maximize=True)
        blocked = tuple(1.0 if not (self.source_eligible[i] and self.reference_verified[i]) else 0.0 for i in range(self.k))
        floor = extreme_simplex(blocked, self.w_lo, self.w_hi, maximize=True)
        if rhi <= self.alpha:
            state = "CERTIFY"
        elif rlo > self.alpha:
            state = "HIGH_RISK"
        elif floor > self.alpha:
            state = "STRUCTURAL_BLOCK"
        else:
            state = "UNRESOLVED"
        return EvidenceView(
            self.alpha, self.budget-self.cost_spent, self.cost_spent, self.k,
            self.delta_r, self.delta_c, self.w_hat, self.w_lo, self.w_hi,
            tuple(self.n), tuple(self.successes), tuple(self.source_eligible),
            tuple(self.reference_verified), tuple(self.ref_upper),
            tuple(self.a2_performed), tuple(self.a3_performed),
            lo, hi, rlo, rhi, floor, state, self.batch,
            self.cost_a2, self.cost_a3, self.batch)

    def execute(self, action: Action):
        v = self.snapshot()
        declared_cost = {"A1": self.batch, "A2": self.cost_a2, "A3": self.cost_a3}.get(action.kind)
        if declared_cost is None or action.cost != declared_cost:
            raise ValueError("Action cost inconsistent with frozen price schedule")
        if action.stratum not in range(v.k):
            raise ValueError("Illegal stratum")
        i = action.stratum
        if action.kind == "A1":
            if not v.source_eligible[i] or not v.reference_verified[i] or v.budget_remaining < self.batch:
                raise ValueError("Illegal A1")
            self._charge(self.batch)
            self.successes[i] += self._env.draw_a1(i,self.batch,self.a3_performed[i])
            self.n[i] += self.batch
        elif action.kind == "A2":
            if (not v.source_eligible[i] or v.reference_verified[i]
                    or self.a2_performed[i] or v.budget_remaining < self.cost_a2):
                raise ValueError("Illegal A2")
            self._charge(self.cost_a2)
            diff = self._env.draw_a2(i,self.n_ref)
            self.a2_performed[i] = True
            self.ref_upper[i] = min(1.0, diff/self.n_ref + reference_discrepancy_radius(self.k,self.n_ref,self.delta_c))
            self.reference_verified[i] = True  # bound is qualified, even if wide
        elif action.kind == "A3":
            if v.source_eligible[i] or self.a3_performed[i] or v.budget_remaining < self.cost_a3:
                raise ValueError("Illegal A3")
            self._charge(self.cost_a3)
            self.a3_performed[i] = True
            self.source_eligible[i] = True
            self.reference_verified[i] = True  # direct clinical-reference target stream
            self.ref_upper[i] = 0.0
            # A3 opens future A1 stream, does not provide a free outcome.
        else:
            raise ValueError("Unknown action")
        next_view = self.snapshot()
        self.action_history.append({
            "action": action.kind, "stratum": i, "cost": action.cost,
            "spent": self.cost_spent, "n_post": self.n[i],
            "lower": next_view.risk_lo, "upper": next_view.risk_hi,
            "floor": next_view.structural_floor,
            "decision": next_view.raw_decision,
            "predicted_utility": action.predicted_utility,
        })
        return next_view


def eligible_actions(v: EvidenceView, typed: bool):
    acts=[]
    for i in range(v.k):
        if (v.source_eligible[i] and v.reference_verified[i] and v.budget_remaining >= v.a1_batch_cost
                and (v.structural_floor <= v.alpha or not typed)):
            acts.append(Action("A1",i,v.a1_batch_cost))
        if typed and v.source_eligible[i] and not v.reference_verified[i] and not v.a2_performed[i] and v.budget_remaining >= v.a2_cost:
            acts.append(Action("A2",i,v.a2_cost))
        if typed and not v.source_eligible[i] and not v.a3_performed[i] and v.budget_remaining >= v.a3_cost:
            acts.append(Action("A3",i,v.a3_cost))
    return sorted(acts,key=lambda a: (ACTION_ORDER[a.kind],a.stratum))


def projected_upper(v: EvidenceView, action: Action):
    # Planning only; does not change the valid intervals used for inference.
    hi=list(v.bounds_hi)
    i=action.stratum
    if action.kind=="A1":
        nnew=v.n[i]+v.a1_batch
        posterior_mean=(v.successes[i]+1)/(v.n[i]+2)
        pnew=(v.successes[i]+v.a1_batch*posterior_mean)/nnew
        b=radius_hoeffding_anytime(v.k,nnew,v.delta_r)
        e=0.0 if v.a3_performed[i] else v.ref_upper[i]
        hi[i]=min(1.0,pnew+b+e)
    elif action.kind=="A2":
        # Fixed non-oracle prior; no access to simulated reference discrepancy.
        e_prior=min(1.0,0.5+reference_discrepancy_radius(v.k,120,v.delta_c))
        if v.n[i]:
            p=v.successes[i]/v.n[i]
            hi[i]=min(1.0,p+radius_hoeffding_anytime(v.k,v.n[i],v.delta_r)+e_prior)
        else:
            hi[i]=1.0
    elif action.kind=="A3":
        # A3 + next paid A1 batch, with mean Beta(1,1)=.5; may remain 1.
        hi[i]=min(1.0,0.5+radius_hoeffding_anytime(v.k,v.a1_batch,v.delta_r))
    else:
        raise ValueError("Unknown action")
    return extreme_simplex(tuple(hi),v.w_lo,v.w_hi,True)


def choose_action(v: EvidenceView, policy_id: str) -> Optional[Action]:
    """Pure deterministic policy. All inputs derived from observed evidence."""
    if policy_id not in ALLOWED_POLICY_IDS:
        raise ValueError("Policy must be P0..P6")
    if v.raw_decision in ("CERTIFY", "HIGH_RISK"):
        return None
    typed=policy_id in ("P4","P5")
    actions=eligible_actions(v,typed)
    if not actions:
        return None
    if policy_id=="P5":
        repairs=[a for a in actions if a.kind!="A1"]
        if repairs:
            return sorted(repairs,key=lambda a:(ACTION_ORDER[a.kind],a.stratum))[0]
        # plugin Neyman after repairs
        policy_id="P2"
    if policy_id=="P4":
        # Even when structural floor > alpha, only actual typed repairs eligible.
        pairs=[]
        for a in actions:
            price=v.a3_cost + v.a1_batch if a.kind=="A3" else a.cost
            if a.kind=="A3" and v.budget_remaining < price:
                # A3 without future A1 cannot produce usable evidence; keep legal
                # as specified, but forecast non-benefit. P5 permits A3 alone.
                utility=0.0
            else:
                utility=max(0.0,v.risk_hi-projected_upper(v,a))/price
            pairs.append((utility,a))
        best=max(u for u,a in pairs)
        tied=[a for u,a in pairs if abs(u-best)<=1e-14]
        a=min(tied,key=lambda a:(ACTION_ORDER[a.kind],a.stratum))
        return dataclasses.replace(a,predicted_utility=best)
    a1s=[a for a in actions if a.kind=="A1"]
    if not a1s:
        return None
    if policy_id=="P6":
        # Registered "SAFER without typed repairs" ablation. 02C-0 accidentally
        # aliased P6 to P0. This is corrected prospectively, BEFORE pilot seeds.
        # P4-style non-oracle gain/cost ranking restricted to legal A1 actions;
        # no A2/A3 is permitted. P4 and P5 themselves are unchanged.
        pairs=[(max(0.0,v.risk_hi-projected_upper(v,a))/a.cost,a) for a in a1s]
        best=max(u for u,a in pairs)
        a=min((a for u,a in pairs if abs(u-best)<=1e-14),key=lambda a:a.stratum)
        return dataclasses.replace(a,predicted_utility=best)
    if policy_id=="P0":
        return min(a1s,key=lambda a:(v.n[a.stratum],a.stratum))
    if policy_id=="P1":
        return min(a1s,key=lambda a:(v.n[a.stratum]/max(v.w_hat[a.stratum],1e-12),a.stratum))
    if policy_id=="P2":
        def neyman_score(a):
            i=a.stratum
            p=(v.successes[i]+1)/(v.n[i]+2)
            target=v.w_hat[i]*math.sqrt(max(p*(1-p),0.01))
            return v.n[i]/max(target,1e-12),i
        return min(a1s,key=neyman_score)
    if policy_id=="P3":
        ranked=[]
        for a in a1s:
            benefit=max(0.,v.risk_hi-projected_upper(v,a))
            ranked.append((benefit,a))
        best=max(x for x,a in ranked)
        return min((a for x,a in ranked if abs(x-best)<=1e-14),key=lambda a:a.stratum)
    raise AssertionError("Unreachable policy")


@dataclass(frozen=True)
class EpisodeMetrics:
    world: str
    seed: int
    policy: str
    budget: int
    final_state: str
    raw_state: str
    risk_lower: float
    risk_upper: float
    structural_floor: float
    valid_correct_resolution: bool
    invalid_certify: bool
    false_certify: bool
    invalid_high_risk: bool
    total_cost: int
    n_a1: int
    n_a2: int
    n_a3: int
    unique_patient_ids: bool
    truth_after_stop: float


def run_episode(config: dict, world: dict, seed: int, budget: int,
                policy_id: str, allow_registered_seeds: bool=False):
    pilot=config["randomization"]["pilot_seeds"]
    conf=config["randomization"]["confirmatory_seeds"]
    for r in (pilot,conf):
        if r["start"] <= seed < r["start"]+r["count"] and not allow_registered_seeds:
            raise ValueError("Registered experimental seeds SEALED in 02C-0")
    if policy_id not in ALLOWED_POLICY_IDS:
        raise ValueError("Unknown policy")
    if budget not in config["synthetic_budget_units"]:
        raise ValueError("Non-registered budget")
    if world["id"] not in {w["id"] for w in config["worlds"]}:
        raise ValueError("Non-registered world")
    env=SyntheticEnvironment(world,seed,config)
    ledger=EvidenceLedger(env,world,config,budget)
    max_actions=budget//min(ledger.batch,ledger.cost_a2,ledger.cost_a3)+1
    for _ in range(max_actions):
        v=ledger.snapshot()
        if v.raw_decision in ("CERTIFY","HIGH_RISK"):
            break
        action=choose_action(v,policy_id)
        if action is None:
            break
        ledger.execute(action)
    else:
        raise AssertionError("No terminating sequence")
    v=ledger.snapshot()
    terminal=v.raw_decision
    if terminal=="STRUCTURAL_BLOCK" and v.structural_floor <= v.alpha:
        raise AssertionError("Invalid structural block")
    if terminal not in STATES:
        raise AssertionError("Invalid decision")
    truth,truth_k=env.scoring_truth()    # scoring isolated after policy completes
    wrong_cert=(terminal=="CERTIFY" and truth>v.alpha)
    wrong_risk=(terminal=="HIGH_RISK" and truth<=v.alpha)
    structurally_invalid_cert = terminal=="CERTIFY" and (
        v.risk_hi>v.alpha or ledger._env._k != v.k or not all(
            (v.source_eligible[i] and v.reference_verified[i]) or v.bounds_hi[i] == 1.0
            for i in range(v.k)))
    resolved=terminal in ("CERTIFY","HIGH_RISK") and not wrong_cert and not wrong_risk and not structurally_invalid_cert
    n_a2=sum(a["action"]=="A2" for a in ledger.action_history)
    n_a3=sum(a["action"]=="A3" for a in ledger.action_history)
    assert ledger.cost_spent<=budget
    assert env.uniqueness_audit()
    assert ledger.cost_spent==sum(a["cost"] for a in ledger.action_history)
    return EpisodeMetrics(world["id"],seed,policy_id,budget,terminal,v.raw_decision,
        v.risk_lo,v.risk_hi,v.structural_floor,resolved,structurally_invalid_cert,
        wrong_cert,wrong_risk,ledger.cost_spent,sum(ledger.n),n_a2,n_a3,
        env.uniqueness_audit(),truth),ledger.action_history
