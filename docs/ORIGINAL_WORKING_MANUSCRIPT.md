# When Better Candidates Hurt Search: Paired Counterfactual Audits of Candidate Replacement in DE, PSO and CMA-ES

**Working research manuscript · revised 23 September 2026 · exploratory, not submitted**

## Abstract

External modules can intercept an optimiser's proposed solution and replace it
without adding evaluations to that optimiser's online budget. Most immediate
assessment asks whether the replacement has lower objective value. We examine
whether this criterion predicts its effect on subsequent optimisation. At a
checkpoint, we clone the complete state of differential evolution (DE),
particle swarm optimisation (PSO), or covariance matrix adaptation evolution
strategy (CMA-ES), evaluate the original proposal and one transformed proposal
in separate branches, and continue both for an equal number of evaluations
using matched random streams and no further interventions. The **diagnostic
experiment itself spends additional real evaluations**. Across all 24 noiseless
COCO/BBOB functions, dimensions 5, 10 and 20, two instances and two seeds per
dimension, contraction produced a lower-fitness candidate in 240 CMA-ES forks.
Nevertheless, 134 of those 240 treated branches had a worse best-so-far value
after the continuation. The analogous fractions were 48/267 for DE and 26/257
for PSO. On previously unused instances, a separate 576-state CMA-ES audit
reproduced substantial delayed harm: 208/478 direct replacements and 211/478
replacements applied through the library's documented `inject()` API were
harmful despite matching immediately better candidates. Injection beat direct
replacement in 277 forks, lost in 273, and tied in 26. These within-host paired
effects show that candidate quality is an unreliable surrogate for trajectory
value, particularly in our tested CMA-ES setup. We release the state-clone
protocol and raw paired trajectories to support evaluation of future
candidate-interception methods. The observed cross-host differences **do not
identify the update rule as their sole cause**: the hosts generate different
populations, proposals, and search states.

## 1. Research question and prior work

**Question.** When a candidate-interception layer replaces a host proposal with
a candidate that is better *right now*, does the replacement improve the
host's best-so-far value after an equal continuation budget?

The question is narrower than inventing a new budget-neutral optimisation
algorithm. The following studies prevent us from claiming the general wrapper,
baseline-relative learning, long-horizon credit, or CMA-ES injection as new.

| Prior work | What its authors did | Boundary for this study |
|---|---|---|
| [GPSAF, Blank & Deb (2022)](https://arxiv.org/abs/2204.04054) | Generalised surrogate assistance over population-based optimisers using an infill/advance interface; compared multiple hosts with maximum true-evaluation budgets of 300 or fewer. The paper explicitly permits infill solutions to be modified before advance. | A host-independent wrapper, candidate replacement, and equal online evaluation budget are established ideas. |
| [JANUS, Yu et al. (August 2026 preprint)](https://arxiv.org/abs/2608.22862) | Extracted local geometry from the evaluation trace and reserved existing host candidate slots for Jacobian-guided infill. | A training-free, budget-neutral host add-on is already proposed. |
| [Injecting External Solutions Into CMA-ES, Hansen (2011)](https://arxiv.org/abs/1110.4181) | Analysed external candidate injection and renormalisation of overly long steps; included preliminary convergence experiments. | Injection and step clipping cannot be claimed as our invention. |
| [`pycma` CMA-ES API](https://cma-es.github.io/apidocs-pycma/cma.evolution_strategy.CMAEvolutionStrategy.html) | Documents the supported `inject()` route and cautions against passing bad external solutions directly to `tell()` with active covariance adaptation. | Compare direct replacement with the supported library implementation on fresh instances. |
| [Action Centered Contextual Bandits, Greenewald et al. (2017)](https://arxiv.org/abs/1711.03596) and [Conservative Contextual Linear Bandits, Kazerouni et al. (2016)](https://arxiv.org/abs/1611.06426) | Formalised baseline-relative treatment learning and safe/conservative exploration in contextual decision problems. | PASS as a control and conservative gating are not independently novel. |
| [The Time Value of Evolution, Siper et al. (August 2026 preprint)](https://arxiv.org/abs/2608.13297) | Studied the difference between immediate and delayed mutation value in program search; audited interventional values by forcing first actions at held-out states and running matched stochastic continuations. | Delayed value and counterfactual continuations are existing concepts. Their setting and intervention differ from continuous black-box candidate replacement across three hosts. |

**Proposed contribution.** A reproducible *evaluation study* of the immediate
versus continuation effect of candidate interception, with separate results by
host and operator. The state-clone technique is a measurement instrument, not
the novelty by itself. A more exhaustive literature review and independent
implementation audit are needed before asserting novelty in a submitted paper.

## 2. Paired-fork protocol

For minimisation, a host proposes $x_t$ at state $S_t$. One branch receives
$x_t$; another receives $T(x_t,S_t)$. Both evaluate exactly one candidate
at the first step. Thereafter both continue with unmodified host proposals for
$H-1$ additional evaluations. Both branches start with copied populations,
host adaptation state, proposed-candidate state, and random generator state.
Common random numbers reduce variance while allowing later states to diverge.
The recorded observables are

$$
\delta_1=f(x_t)-f(T(x_t,S_t)),\qquad
\Delta_H=b^{PASS}_{t+H}-b^{T}_{t+H},
$$

where $b$ is the best objective observed by a branch. A positive $\delta_1$
means the replacement candidate is better. A negative $\Delta_H$ means the
intervention branch has a worse *best-so-far* value after continuation. The
descriptive quantity $P(\Delta_H<0\mid\delta_1>0)$ is measurable with the
two diagnostic branches; a live optimiser could not know $\delta_1$ without
spending the extra PASS evaluation.

We use two fixed transformations: contraction
$T_C(x)=\operatorname{clip}(x+0.45(x_{best}-x))$, and reflection of the
proposal step around its parent
$T_R(x)=\operatorname{clip}(x_{parent}-0.75(x-x_{parent}))$.
The host always receives the actual evaluated candidate and its true value.

DE uses rand/1/bin with $F=0.7$, crossover probability 0.9 and an elitist
parent replacement. PSO uses a global-best velocity update with inertia 0.7
and cognitive/social coefficients 1.4; a transformed candidate becomes the
particle's next position and changes its velocity. CMA-ES uses `cma` 4.5.0
ask/tell with initial mean at the search-box centre, step size 0.3 times the
mean box width, and a population of
$\max(8,\lfloor4+3\log D\rfloor)$. The other hosts use
$\max(8,5D)$ individuals. These are basic host implementations, not
representatives of every variant or configuration.

For each of 24 BBOB functions and each dimension $D\in\{5,10,20\}$,
we used two instances and two seeds. The actual COCO instance IDs were 71–72
in 5D, 73–74 in 10D, and 77–78 in 20D. Each baseline host performed $20D$
evaluations before cloning; each of PASS, contraction and reflection then
performed another $20D$ diagnostic evaluations. The design produced 864
branch records per dimension and 806,400 true objective evaluations overall.
The extra branch evaluations are openly counted and never described as
budget-neutral online optimisation. Two independently cloned PASS runs
reproduced identical first and subsequent objective values for all three
hosts in a deterministic regression check.

## 3. Results

### 3.1 Contraction

**Harm** means a worse best-so-far value than PASS after the continuation,
conditional on the replacement candidate being immediately better. Ties are
counted only for the continuation comparison; the condition uses a 1e-9
absolute numerical threshold.

| Dimension | DE harm / immediately better | PSO | CMA-ES |
|---:|---:|---:|---:|
| 5 | 18/87 (20.7%) | 8/77 (10.4%) | **41/80 (51.3%)** |
| 10 | 18/89 (20.2%) | 10/88 (11.4%) | **47/79 (59.5%)** |
| 20 | 12/91 (13.2%) | 8/92 (8.7%) | **46/81 (56.8%)** |
| Pooled descriptive counts | 48/267 (18.0%) | 26/257 (10.1%) | **134/240 (55.8%)** |

![Conditional harm by dimension and host](fork_conditional_harm.png)

The figure's vertical intervals resample the 24 **functions** as clusters,
not individual branches. For contraction, the function-cluster descriptive
harm-rate difference between CMA-ES and DE was 0.281 (interval 0.170–0.389)
in 5D, 0.410 (0.246–0.562) in 10D, and 0.448 (0.340–0.552) in 20D.
Because each host reaches different states and uses a different proposal
distribution, these differences should be interpreted as *host-dependent
outcomes under this protocol*, not an isolated causal effect of the update
rule itself.

### 3.2 Reflection and step-cap check

Reflection shows a related pattern but generates fewer immediately better
candidates: the conditional harm counts were 7/108 for DE, 1/45 for PSO, and
59/104 for CMA-ES when pooled descriptively across dimensions.

We then ran a fresh CMA-ES-only mechanism check on instance IDs 75–76 in 5D
and 10D. A fixed alternative capped **the displacement caused by contraction**
at $0.5\sqrt D$ Mahalanobis units, measured using the current CMA-ES
distribution. This is a simple safeguard inspired by, but not a replication
of, Hansen's complete injection procedure. After continuation, capped versus
uncapped contraction was better/worse/tied in 14/17/65 five-dimensional forks
and 2/6/88 ten-dimensional forks. The cap changed the first candidate's
objective in only 31/96 and 8/96 forks respectively. **This fixed cap did not
resolve the observed harm.** Its frequent inactivity limits the conclusion;
it is not evidence against all injection safeguards.

### 3.3 Independent-instance check with native CMA-ES injection

The initial CMA-ES implementation directly substitutes the contracted point
into `tell()`. To test whether that implementation choice explains the result,
we conducted a fresh, separately analysed audit using BBOB **instance IDs
79–80** (COCO suite indices 14–15), four seeds and each of the same 24
functions in dimensions 5, 10 and 20. The CMA-ES burn-in is 104, 200 and 408
evaluations, respectively, so cloning takes place at a complete generation
boundary. The continuation remains $20D$ evaluations. Each checkpoint has
three branches: PASS, direct replacement of the first sampled proposal, and
`CMAEvolutionStrategy.inject([genotype], force=True)` before `ask()`. The
genotype uses the inverse boundary transform. Direct and injected branches
receive the same first treated candidate within floating-point tolerance and
evaluate it separately; all branches use the same continuation *budget*,
with no more interventions. Injection changes which later proposals receive
the common random draws. We therefore interpret differences across repeated
seeds rather than claiming pointwise identical later proposals.

| Dimension | Checkpoints | First candidate better than PASS | Direct: later worse than PASS | Native injection: later worse than PASS |
|---:|---:|---:|---:|---:|
| 5 | 192 | 161 | 74/161 (46.0%) | 65/161 (40.4%) |
| 10 | 192 | 153 | 63/153 (41.2%) | 66/153 (43.1%) |
| 20 | 192 | 164 | 71/164 (43.3%) | 80/164 (48.8%) |
| Descriptive pooled count | 576 | 478 | **208/478 (43.5%)** | **211/478 (44.1%)** |

![Delayed harm for direct replacement and documented injection](injection_harm_comparison.png){width=68%}

The figure's intervals resample functions as clusters. The equal-function
conditional-harm difference (direct minus injection) is −0.002, with a 95%
function-cluster bootstrap interval of −0.054 to 0.053 when dimensions are
descriptively pooled. Injection beat direct replacement after continuation in
277 checkpoints, lost in 273, and tied in 26. On this protocol the documented
API **did not consistently reduce delayed harm**. It remains the supported
method for inserting outside solutions; this study does not contradict its
documented stability purpose or test all possible proposal sources.

We measured the mean displacement, step-size ratio and covariance trace and
condition-number ratios after the first treated generation. Descriptive
medians are in `injection_analysis.txt`; they did not reveal a decisive
single-variable mechanism. The later sampled proposals differ between direct
and injected branches, so the study cannot assign a between-treatment
difference solely to covariance update safeguards. The new audit produced
1,728 branch records and used **539,904 true objective evaluations**, including
all baseline and continuation calls. This is an independently indexed
replication of the phenomenon on functions already examined, not a wholly
independent new function suite.

## 4. Interpretation and publication boundary

The paired branches establish a causal *within-host, within-checkpoint*
contrast for the tested transformation: the only prescribed initial difference
is PASS versus interception. An immediately better candidate often fails to
produce a better later trajectory. The pattern is especially strong in this
CMA-ES implementation and remains visible at three dimensions. It is
plausible that distribution adaptation, as opposed to elitist survival or
personal-best memory, contributes to the difference. We have **not isolated
that mechanism** from other host and state differences. The fresh-instance
experiment rules out the narrower assertion that using `tell()` directly is
necessary for the observed delayed harm. It does not show that `inject()` and
direct replacement have identical distributions or that either reliably
improves the host.

This paper should **not** be submitted as “EvoUplift beats existing
optimisers” or “a novel causal bandit.” Our previous held-out experiment did
not support either claim. A defensible provisional title is the title above;
its claim is a measurable failure mode and an evaluation protocol for
candidate-interception layers.

Before journal submission, the most important remaining work is:

1. Replicate on independent, standard DE/PSO/CMA-ES implementations and more
   seeds and instances; account for noise and stochastic objectives where
   identical calls cannot be assumed to have identical values.
2. Replicate the direct-versus-injected contrast with more seeds, host
   configurations and independent implementations; use controlled ablations
   to separate changes in sampling, covariance adaptation and step size. Our
   recorded aggregate state measures do not isolate a mechanism.
3. Report target-based COCO runtimes and anytime curves alongside the paired
   diagnostic outcomes. Establish a real application if claiming practical
   value, and compare any **new** corrective policy to GPSAF and existing
   host-specific injection methods at matched online budgets.
4. Review related work systematically, especially the August 2026 delayed
   value preprint, before making originality claims.

The present material is suitable for a **transparent working paper or
specialist workshop submission draft** after an independent code audit. The
data do not guarantee peer-reviewed acceptance or justify a claim of a new
state-of-the-art optimiser.

## 5. Reproduction

Install Python 3.12, NumPy, `coco-experiment`, `cma>=4`, SciPy and Matplotlib.
Run `trajectory_forks.py` with the configurations specified in
`REPRODUCE_FORKS.md`; then run `fork_analysis.py` and
`make_fork_figure.py`. The native injection follow-up uses
`cma_injection_audit.py`, `analyze_injection.py` and `plot_injection.py`.
Raw paired branches and both figure sources are supplied. COCO's
`instance_indices` selects **suite indices**, not printed instance IDs; the
reproduction instructions use the correct index ranges.

## References

1. Blank, J. & Deb, K. (2022). [GPSAF](https://arxiv.org/abs/2204.04054).
2. Hansen, N. (2011). [Injecting External Solutions Into CMA-ES](https://arxiv.org/abs/1110.4181).
3. Siper, M., Khalifa, A. & Togelius, J. (2026). [The Time Value of Evolution](https://arxiv.org/abs/2608.13297), preprint.
4. Yu, H. et al. (2026). [JANUS: Online Jacobian-Aligned Infill for Black-Box Optimization](https://arxiv.org/abs/2608.22862), preprint.
5. Greenewald, K. et al. (2017). [Action Centered Contextual Bandits](https://arxiv.org/abs/1711.03596).
6. Kazerouni, A. et al. (2016). [Conservative Contextual Linear Bandits](https://arxiv.org/abs/1611.06426).
