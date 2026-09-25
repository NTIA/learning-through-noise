# Inferring Votes
Datasets are shared with varying amounts of detail in their subjective test results. 
The ultimate level of detail is raw votes. Raw votes enable some types of analyses and simulations that are otherwise impossible, and from raw votes one can calculate means and measures of dispersion such as standard deviation, variance, and standard error.

When a finite set of raw votes are limited to the integers 1, 2, 3, 4, and 5, (as is very often the case), a finite number of means and standard deviations are possible.
It follows that given a mean, a standard deviation, and a number of votes, it is often possible to uniquely determine the values (1, 2, 3, 4, and 5) of those votes.

Given a mean, a standard deviation, and the knowledge that they were both calculated from the same set of $n$ votes, we proceed as follows.
First we list all possible (5 bin) histograms for $n$ votes.
(When $n=$ 10, 20, 30, or 40 votes, the numbers of histograms required are 1001, 10,626, 46,376, and 135,751, resp.)
Next we check to see if any histogram has the specified mean and standard deviation. 
At this step it is important to account for the fact that reported means and standard deviations are often rounded to just a few decimal places.

If more than one match is found, we pick one stochastically, guided by skewness.
Specifically, we calculate the skewness $s$ of each solution, assign each solution a probability that is proportional to $1-s$, then draw the final solution from this set of candidate solutions at random, according to those probabilities.
This approach is motivated by the notion that lower vote skewness is more realistic than higher vote skewness.

For one large database where $n=5$ most often, (but with some variation), we found that 87\% of the files have a single unique vote solution solution, and for 12\% of the files, two solutions are possible and we need to use the skewness-based final step for these.
The remaining 1\% of the files have 3 to 6 possible solutions and we use the skewness-based final step again here.
