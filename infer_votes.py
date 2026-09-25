import numpy as np
import pandas as pd
import scipy.stats as stats

from argparse import ArgumentParser
from tqdm import tqdm


def make_hist_list(n_votes):
    """
    make_hist_list

    Generate all possible vote histograms given n_votes

    Parameters
    ----------
    n_votes : int
        The total number of votes to distribute among the five bins.

    Returns
    -------
    np.ndarray
        An array of shape (num_patterns, 5) containing all possible vote histograms for
        the given number of votes.
    """
    vote_patterns = []
    # First bin can have up to n votes
    for i in np.arange(n_votes + 1):
        # Second bin could have all the remaining votes
        for j in np.arange(0, n_votes - i + 1):
            # Thrid bin could have all the remaining votes
            for k in np.arange(0, n_votes - (i + j) + 1):
                # Fourth bin could have all the remaining votes
                for L in np.arange(0, n_votes - (i + j + k) + 1):
                    # Fifth bin gets the rest of the votes
                    vote_pattern = [i, j, k, L, n_votes - (i + j + k + L)]
                    vote_patterns.append(vote_pattern)
                    # ptr += 1
    vote_patterns = np.array(vote_patterns)
    return vote_patterns


# Inferring vote stuff
def infer_votes(
    mean,
    var,
    n_votes,
    vote_pattern_dict,
    seed=None,
):
    """
    infer_votes

    Infer the votes that could produce a given MOS mean and vote variance estimate.

    Parameters
    ----------
    mean : float
        The target mean of the votes (MOS).
    var : float
        The target variance of the votes.
    n_votes : int
        The total number of votes.
    vote_pattern_dict : dict
        A dictionary caching previously computed vote patterns for different numbers of
        votes.
    seed : int, optional
        Random seed for reproducibility when selecting among multiple candidate vote
        patterns.

    Returns
    -------
    votes : np.ndarray
        The inferred vote distribution that matches the given mean and variance.
    candidates : list of np.ndarray
        All candidate vote distributions that match the given mean and variance.
    probs : np.ndarray or None
        The probabilities assigned to each candidate based on skewness, or None if not
        applicable.
    vote_pattern_dict : dict
        Updated dictionary of vote patterns.
    """
    if n_votes in vote_pattern_dict:
        vote_patterns = vote_pattern_dict[n_votes]
    else:
        vote_patterns = make_hist_list(n_votes)
        vote_pattern_dict[n_votes] = vote_patterns
    # Get the mean for each vote pattern
    mean_list = np.matmul(vote_patterns, np.array([1, 2, 3, 4, 5])) / n_votes
    # Calculate the variance for each vote pattern
    var_list = np.zeros_like(mean_list)
    for i, (vote_pattern, mos) in enumerate(zip(vote_patterns, mean_list)):
        var_list[i] = np.matmul(vote_pattern, (np.arange(1, 6) - mos) ** 2) / (
            n_votes - 1
        )

    # Make a list of all list locations where m and s match those of a histogram
    # Since means and stds given in datasets are often truncated they might not
    # exactly match those calculated here, so tolerance in matching becomes important
    # This can be tuned directly with rtol and atol parameters in np.isclose but we
    # start with defaults.
    close_mean = np.isclose(mean_list, mean, atol=1e-3)
    close_var = np.isclose(var_list, var, atol=1e-3)
    match_list = close_mean & close_var
    candidates = []
    if np.sum(match_list) == 0:
        print("No vote patterns found that match the given mean and variance.")
    else:
        vote_matches = vote_patterns[match_list]
        for match in vote_matches:
            temp_votes = hist2votes(match)
            candidates.append(temp_votes)
    if candidates == []:
        votes = []
        probs = None
    elif len(candidates) == 1:
        votes = candidates[0]
        probs = None
    else:
        # More than one candidate
        skews = []
        for candidate in candidates:
            skew = np.abs(stats.skew(candidate, bias=False))
            skews.append(skew)
        # Convert skewnewss to a probability where smaller skewness gives higher
        # probability of selection
        probs = (1 - skews / np.sum(skews)) / (len(skews) - 1)

        rng = np.random.default_rng(seed)

        selected_ix = rng.choice(len(candidates), p=probs)

        votes = candidates[selected_ix]
    return votes, candidates, probs, vote_pattern_dict


def hist2votes(hist):
    votes = []
    for i, count in enumerate(hist):
        # votes.extend([i + 1] * count)
        try:
            votes.extend([i + 1] * int(count))
        except:
            print(
                f"Error in hist2votes with hist: {hist}, i: {i}, count: {count}, votes:"
                f" {votes}"
            )
    return np.array(votes)


def infer_file_votes(args):
    seed = args.seed
    # Load csv and grab the means, vars, and n_votes
    df = pd.read_csv(args.csv_file)
    means = df[args.mean_col].values
    vars = df[args.var_col].values
    n_votes = df[args.n_votes_col].values
    votes_list = []
    # Dictionary to store seen histograms in
    vote_pattern_dict = dict()
    total = len(df)
    for mean, var, n in tqdm(zip(means, vars, n_votes), total=total):
        votes, candidates, probs, vote_pattern_dict = infer_votes(
            mean,
            var,
            n,
            seed=seed,
            vote_pattern_dict=vote_pattern_dict,
        )
        votes_list.append(votes)

    # Convert the list of votes to a numpy array for easier manipulation
    votes_array = np.array(votes_list)
    return votes_array


if __name__ == "__main__":
    parser = ArgumentParser()
    # argument for csv file with means, variances, and number of votes
    parser.add_argument(
        "--csv_file",
        type=str,
        required=True,
        help="Path to the CSV file containing means, variances, and number of votes.",
    )
    # argument for mean column label, default=MOS
    parser.add_argument(
        "--mean_col",
        type=str,
        required=False,
        default="MOS",
        help="Column label for the mean values in the CSV file.",
    )
    # argument for variance column label
    parser.add_argument(
        "--var_col",
        type=str,
        required=False,
        default="MOS_Var",
        help="Column label for the variance values in the CSV file.",
    )
    # argument for number of votes column label
    parser.add_argument(
        "--n_votes_col",
        type=str,
        required=False,
        default="n_votes",
        help="Column label for the number of votes in the CSV file.",
    )
    # argument for random seed
    parser.add_argument(
        "--seed",
        type=int,
        required=False,
        default=None,
        help=(
            "Random seed for reproducibility when selecting among multiple candidate"
            " vote patterns."
        ),
    )
    # Argument for output file
    parser.add_argument(
        "--output_file",
        type=str,
        required=False,
        default="votes.csv",
        help="Path to the output file where the resulting votes array will be saved.",
    )

    args = parser.parse_args()

    # Print the resulting votes array for verification
    votes_array = infer_file_votes(args)
    print(votes_array)
    # Save the resulting votes array to the output file
    np.savetxt(args.output_file, votes_array, delimiter=",", fmt="%d")
