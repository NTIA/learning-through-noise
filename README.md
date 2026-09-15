# Learning through the noise
This repository corresponds to the paper "Learning Through the Noise: Impact of Training Objective Speech Quality Estimators with Noisy Subjective Scores" by Jaden Pieper and Stephen D. Voran.

# Abstract

# Description
This repository contains supplementary materials to the paper.
* `statistical-tests.md` describes the tests of statistical significance used to compare correlation results in the paper and determine if the difference of two correlations was significant.
* `cascaded-BinoMOS.md` describes the calculation and derivation of the effective voting power of cascaded BinoMOS, where a MOS value with $n_1$ ratings per file is used as an input to BinoMOS with $n_2$ ratings per file.

## Inferring votes from MOS statistics

`infer_votes.py` reconstructs a plausible set of integer votes from a mean opinion
score (MOS), its sample variance, and the number of votes. It searches the possible
vote histograms using ratings from 1 through 5. When multiple histograms match, one
candidate is selected using a skewness-based probability distribution.

The input CSV must contain columns named `MOS`, `MOS_Var`, and `n_votes` by default.
For example, `example_votes.csv` contains these columns along with the original
`V1` through `V10` ratings for comparison.

```bash
python infer_votes.py \
  --csv_file example_votes.csv \
  --output_file inferred_votes.csv \
  --seed 0
```

The output is a headerless CSV with one row of inferred votes per input row. The
default output path is `votes.csv`. Use the following options to work with
different column names:

| Option | Default | Description |
| --- | --- | --- |
| `--csv_file` | *(required)* | Input CSV containing MOS statistics |
| `--output_file` | `votes.csv` | Output CSV for inferred votes |
| `--mean_col` | `MOS` | Input column containing the mean |
| `--var_col` | `MOS_Var` | Input column containing the sample variance |
| `--n_votes_col` | `n_votes` | Input column containing the number of votes |
| `--seed` | `None` | Seed used when selecting among multiple candidates |
