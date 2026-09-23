# A journal submission route for the candidate-intervention study

**Decision memo | 23 September 2026 | proposed target: *Swarm and Evolutionary Computation***

## Recommendation

Build **one** paper on *trajectory-aware candidate interception in CMA-ES*.
Use the existing paired-fork results as motivation and development data, not
as the final performance evidence. The paper should introduce a measurable
decision problem and test whether a policy learned from past counterfactual
continuations improves actual future optimisation with **one true objective
evaluation per candidate slot**. A preregistered evaluation on an untouched
benchmark must decide the submission claim. Do not adjust the test split,
transformation, thresholds or main outcome after inspecting it.

This is the most credible way to turn the observed phenomenon into a substantive
method contribution. It does not assume that an improvement exists. A completed
experiment may still give a publishable measurement contribution, but a
better-performing online optimiser cannot be asserted until the blind test
supports it.

## What the closest papers have already done

| Study | Established result | Consequence for us |
|---|---|---|
| Blank & Deb, [GPSAF](https://arxiv.org/html/2204.04054v1) (2022) | Explicitly permits modifications to a host's proposals before its infill/advance interface; proposes a general surrogate wrapper and compares population hosts under small true-evaluation budgets. | The wrapper, modification interface and budget-neutral candidate replacement are prior art. |
| Hansen, [external solutions in CMA-ES](https://arxiv.org/abs/1110.4181) (2011), and the [`pycma` API](https://cma-es.github.io/apidocs-pycma/cma.evolution_strategy.CMAEvolutionStrategy.html) | External injection and safeguards for long steps are established; the API recommends `inject()` over naive direct `tell()`. | Use documented injection and compare standard safeguards; don't present them as new. |
| Consoli et al., [dynamic operator selection](https://link.springer.com/article/10.1007/s00500-016-2126-x) (2016) | Shows that offspring fitness alone can be insufficient; learns from landscape information, offspring survival and diversity. | A gate based on immediate fitness or population diversity alone has prior art. |
| Vermetten et al., [online selection of CMA-ES variants](https://arxiv.org/abs/1904.07801) (2019) | Adaptive choices yielded gains on many BBOB functions, while a proposed prior selection approach proved unreliable. | Online adaptation must beat simple and strong adaptive controls and demonstrate stability. |
| Siper et al., [*The Time Value of Evolution*](https://arxiv.org/html/2608.13297v1) (August 2026 preprint) | Defines delayed mutation value, uses held-out interventional continuations, and reports an online long-horizon policy in program search. | Neither delayed value, paired continuations, nor learning from them is new in general. Our specific continuous host-interception setting and test must add real evidence. |
| Nikolikj et al., [benchmarking footprints](https://doi.org/10.1016/j.swevo.2025.101895), *Swarm and Evolutionary Computation* (2025) | Publishes a method for explaining successes and failures of three black-box optimisers, compared with two earlier comparison methods. | A serious benchmarking methodology can be a field-journal contribution without a state-of-the-art optimiser, but it needs its own methodological advance and validation. |

The target journal explicitly covers experimental and theoretical evolutionary
computation and original methodological advances:
[journal scope](https://shop.elsevier.com/journals/swarm-and-evolutionary-computation/2210-6502).
*Information Sciences* is broad and asks for original, innovative results;
the present short descriptive draft does not yet meet that bar:
[journal scope](https://shop.elsevier.com/journals/information-sciences/0020-0255).
These venue judgments are our inference from the stated scopes and comparable
papers, not editorial decisions.

## What the current data actually establish

- The first audit covers 24 BBOB functions, three dimensions, two instances
  and two seeds per host. Conditional on an immediately better contracted
  proposal, the later CMA-ES best-so-far was worse in **134/240** forks; DE
  and PSO had **48/267** and **26/257** harmful forks, respectively.
- A fresh CMA-ES study on different BBOB instances, four seeds and three
  dimensions found **208/478** harmful direct-replacement forks and **211/478**
  harmful native-injection forks among immediately better candidates. Native
  injection won **277**, lost **273** and tied **26** paired comparisons against
  direct replacement. There is no supported claim that native injection
  improved the optimiser under this transformation.
- These experiments answer a **diagnostic** question using both potential
  first-candidate evaluations and multiple true-evaluation continuations.
  A deployed algorithm cannot know which candidate was immediately better
  unless it spends extra objective calls. The current paper does not test an
  online decision policy or standard COCO target attainment.
- All 24 BBOB functions have already informed exploration. Fresh instances
  of those same functions are useful replication, but not an untouched
  *function-level* confirmation. Two instances per condition are too few to
  justify broad algorithm rankings; even 15 runs can misrank stochastic
  optimisers, as [Vermetten et al.](https://arxiv.org/abs/2204.09353) show.

## Locked experiment to run next

### 1. Implement one deployable decision

At a checkpoint, let $x$ be the sampled CMA-ES candidate and $T(x)$ the
**fixed** contraction already studied ($0.45$ toward the current best within
bounds). The policy chooses PASS or documented native injection **before any
objective call for this slot**, using only information available at that time:
dimension, fraction of budget remaining, progress history, incumbent age,
relative candidate geometry and Mahalanobis displacement. Neither $f(x)$ nor
$f(T(x))$ is an input. Because `inject()` must run before `ask()`, use a copied
host state to preview the raw proposal without evaluating it; then apply the
chosen action to the live host. Record CPU time for the preview and learning.
Every live strategy evaluates only the resulting candidate in each slot.

Train a deliberately simple, interpretable risk model from offline paired
forks to predict the sign or calibrated magnitude of
$b^{PASS}_{t+H}-b^{INJECT}_{t+H}$ at a prespecified $H=20D$. Choose a single
threshold on training/validation data. Hold the feature list, model family,
threshold-selection rule, and transformation fixed before confirmation.
Offline diagnostic and training evaluations must be disclosed separately
from the online budget; describe where amortised offline training would make
sense and do not claim the training was free.

### 2. Separate development and confirmation

Use the existing BBOB results only to design the features and pipeline.
Collect new fork labels with an instrumented standard `pycma` implementation
at several fixed search stages, with valid state copying and recorded
random-generator state. Cross-validate by **entire function**, not by forks
from the same function: all seeds, instances and checkpoints for a function
stay in one fold. Report calibration, ranking, selection rate, and whether a
simple geometry-only or immediate-value proxy performs just as well.

For a genuine external confirmation, use the separately published
[official CEC 2022 single-objective bound-constrained suite](https://github.com/P-N-Suganthan/2022-SO-BO)
with fixed problem definitions and no policy retuning. If the exact suite
contains any functions or settings used in development, disclose that overlap
and choose another untouched suite before testing. Freeze and timestamp the
protocol and code before this run. Only after the CEC result is locked may
the corresponding BBOB test figures be discussed as supporting evidence.

### 3. Measure online performance fairly

Compare at least: (i) plain official `pycma`; (ii) always apply the same
native injection; (iii) an uninformed gate matched to the policy's injection
frequency; (iv) a same-features gate trained on immediate outcomes rather
than continuation outcomes; and (v) the trajectory-aware gate. Use matched
starting states and seeds, equal true-evaluation budgets, and an explicit
initialisation/restart rule. Report online CPU time as well as objective calls.
If a published method such as GPSAF or JANUS can be run on exactly the same
domain and budget, add it as a separate contextual baseline using its own
documented implementation, not a guessed reimplementation.

The **primary confirmation endpoint** is the equal-budget area under an
anytime log-error curve on untouched CEC 2022 functions, at a frozen budget
of $300D$ true evaluations, with 30 paired random seeds per function and
dimension (10D and 20D). Specify the target-error floor and aggregation
across functions *before* looking at results. The secondary BBOB endpoint is
target-attainment performance under the standard
[COCO performance procedure](https://numbbo.github.io/coco-doc/perf-assessment/).
Also report final error. Provide function-level and dimension-level
plots, paired effects with uncertainty that resamples independent functions
or instances as appropriate, and both wins and serious regressions. Do not
turn 100 correlated checkpoints from one run into 100 independent samples.
COCO says evaluation count is the runtime measure and prohibits passing the
function identifier to the algorithm; follow these rules:
[experimental procedure](https://numbbo.github.io/coco-doc/experimental-setup/).

### 4. Decide from one locked confirmation

Submit the online-method claim only if the untouched suite shows a practically
meaningful improvement over **both** plain CMA-ES and the immediate-outcome
gate at matched budget, the uncertainty on aggregate effect excludes zero,
and no broad landscape group suffers an unreported substantial regression.
Set the practical threshold to at least a **5% reduction in the primary
anytime error** relative to both controls. This is our internal go/no-go
criterion, not a journal rule.

If those criteria fail, do **not** tune repeatedly on the held-out set. The
separate journal option would require a demonstrably new benchmarking
instrument: independently replicated host implementations, multiple
perturbations and horizons, explicit null controls, quantified effect sizes
and a substantive comparison with existing diagnostic methods. The existing
five-page draft and two-instance tables alone are insufficient for that claim.
The outcome of the locked test, including failures, should remain visible
in the dataset and paper.

## Submission package and practical order

1. Freeze a protocol and a versioned code release; have an independent
   researcher reproduce one complete branch and its evaluation count.
2. Implement and audit the online gate and comparators, then run development
   and whole-function validation. Report all explored model settings.
3. Lock the model and execute the untouched suite **once** with adequate
   independent runs. Schedule compute before promising a deadline; COCO has
   24 functions, six standard dimensions and 15 supplied instances, and
   ranking uncertainty can remain large even with 15 runs.
4. Write a full journal manuscript with method, related work, preregistered
   hypotheses, uncertainty, failure cases, runtime and released code/data.
   Follow the chosen journal's current Guide for Authors for formatting, and
   repeat the novelty review immediately before submission.

**Decision:** Invest in this one definitive study. The present findings are
valuable pilot evidence; a positive journal performance claim remains
unproven, and no honest design can guarantee that the locked test will be
favourable.
