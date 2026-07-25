## WorldQuant Fast Expression Language Knowledgebase

This knowledgebase provides a concise list of operators in the WorldQuant Fast Expression language, along with brief descriptions for your understanding and usage.

**Arithmetic Operators**

1. **`add(x, y, ..., filter=false)`**: Adds all inputs. If `filter` is true, replaces all input NaNs with 0 before adding.
2. **`subtract(x, y, filter=false)`**: Subtracts y from x. If `filter` is true, replaces all input NaNs with 0 before subtracting.
3. **`multiply(x, y, ..., filter=false)`**: Multiplies all inputs. If `filter` is true, replaces all input NaNs with 1 before multiplying.
4. **`divide(x, y)`**: Divides x by y. Returns NaN if y is 0.
5. **`power(x, y, precise=false)`**: Raises x to the power of y. If `precise` is true, uses a more precise calculation method.
6. **`log_diff(x)`**: Calculates the difference between the logarithm of today's value of x and the logarithm of yesterday's value of x.
7. **`s_log_1p(x)`**: Calculates sign(x) * log(1 + abs(x)). Confines the function to a shorter range using logarithm while preserving the sign.
8. **`nan_mask(x, y)`**: Replaces x with NaN if the corresponding value of y is negative.
9. **`replace(x, target="v1 v2 ... vn", dest="d1 d2 ... dn")`**: Replaces target values in x with destination values. Can replace multiple values or replace all target values with a single destination value.
10. **`fraction(x)`**: Returns the fractional part of x, preserving the sign.
11. **`signed_power(x, y)`**: Calculates x raised to the power of y, preserving the sign of x.
12. **`nan_out(x, lower=0, upper=0)`**: Returns x if it is within the range specified by `lower` and `upper`. Otherwise, returns NaN.
13. **`purify(x)`**: Replaces all infinities in x with NaN.

**Mathematical Operators**

14. **`abs(x)`**: Returns the absolute value of x.
15. **`ceiling(x)`**: Returns the smallest integer greater than or equal to x.
16. **`floor(x)`**: Returns the largest integer less than or equal to x.
17. **`round(x)`**: Rounds x to the nearest integer.
18. **`sign(x)`**: Returns -1 if x is negative, 0 if x is 0, and 1 if x is positive.
19. **`arc_cos(x)`**: Returns the arc cosine of x.
20. **`arc_sin(x)`**: Returns the arc sine of x.
21. **`arc_tan(x)`**: Returns the arc tangent of x.
22. **`sigmoid(x)`**: Returns the sigmoid of x (1 / (1 + exp(-x))).
23. **`tanh(x)`**: Returns the hyperbolic tangent of x.

**Statistical Operators**

24. **`max(x, y, ...)`**: Returns the maximum value of all inputs.
25. **`min(x, y, ...)`**: Returns the minimum value of all inputs.
26. **`mean(x, d)`**: Returns the average value of x for the past d days.
27. **`median(x, d)`**: Returns the median value of x for the past d days.
28. **`std_dev(x, d)`**: Returns the standard deviation of x for the past d days.
29. **`skewness(x, d)`**: Returns the skewness of x for the past d days.
30. **`kurtosis(x, d)`**: Returns the kurtosis of x for the past d days.
31. **`corr(x, y, d)`**: Returns the correlation of x and y for the past d days.
32. **`covariance(x, y, d)`**: Returns the covariance of x and y for the past d days.
33. **`zscore(x)`**: Returns the z-score of x.
34. **`winsorize(x, std=4)`**: Winsorizes x to make sure that all values in x are between the lower and upper limits defined by the mean plus/minus `std` times the standard deviation.

**Time Series Operators**

35. **`ts_delay(x, d)`**: Returns the value of x d days ago.
36. **`ts_delta(x, d)`**: Returns x - ts_delay(x, d).
37. **`ts_arg_max(x, d)`**: Returns the relative index of the maximum value in the time series for the past d days.
38. **`ts_arg_min(x, d)`**: Returns the relative index of the minimum value in the time series for the past d days.
39. **`ts_co_kurtosis(y, x, d)`**: Returns the cross-kurtosis of y and x for the past d days.
40. **`ts_co_skewness(y, x, d)`**: Returns the cross-skewness of y and x for the past d days.
41. **`ts_decay_exp_window(x, d, factor=1.0, nan=True)`**: Returns the exponentially decayed value of x for the past d days with smoothing factor `factor`.
42. **`ts_decay_linear(x, d, dense=false)`**: Returns the linearly decayed value of x for the past d days. If `dense` is true, uses a denser decay.
43. **`ts_ir(x, d)`**: Returns the information ratio of x for the past d days.
44. **`ts_max(x, d)`**: Returns the maximum value of x for the past d days.
45. **`ts_min(x, d)`**: Returns the minimum value of x for the past d days.
46. **`ts_moment(x, d, k)`**: Returns the k-th central moment of x for the past d days.
47. **`ts_partial_corr(x, y, z, d)`**: Returns the partial correlation of x, y, and z for the past d days.
48. **`ts_percentage(x, d, percentage=0.5)`**: Returns the percentile value of x for the past d days.
49. **`ts_poly_regression(y, x, d, k=1)`**: Returns the k-th order polynomial regression of y on x for the past d days.
50. **`ts_product(x, d)`**: Returns the product of x for the past d days.
51. **`ts_rank(x, d, constant=0)`**: Ranks the values of x for each instrument over the past d days, then returns the rank of the current value plus `constant`.
52. **`ts_regression(y, x, d, lag=0, rettype=0)`**: Returns the regression of y on x for the past d days. `lag` specifies the lag of the independent variable, and `rettype` specifies the type of return value (e.g., slope, intercept, error term).
53. **`ts_returns(x, d, mode=1)`**: Returns the relative change in x for the past d days. `mode` specifies the calculation method.
54. **`ts_scale(x, d, constant=0)`**: Scales x to be between 0 and 1 for the past d days.
55. **`ts_skewness(x, d)`**: Returns the skewness of x for the past d days.
56. **`ts_std_dev(x, d)`**: Returns the standard deviation of x for the past d days.
57. **`ts_step(1)`**: Returns a step function with a value of 1.
58. **`ts_sum(x, d)`**: Returns the sum of x for the past d days.
59. **`ts_theilsen(x, y, d)`**: Returns the Theil-Sen slope estimator of x and y for the past d days.
60. **`ts_triple_corr(x, y, z, d)`**: Returns the triple correlation of x, y, and z for the past d days.
61. **`ts_weighted_delay(x, k=0.5)`**: Returns a weighted average of today's and yesterday's values of x.
62. **`ts_zscore(x, d)`**: Returns the z-score of x for the past d days.
63. **`ts_av_diff(x, d)`**: Returns x - ts_mean(x, d), handling NaNs carefully.
64. **`ts_entropy(x, d, buckets=10)`**: Calculates the information entropy of x for the past d days using a histogram with `buckets` number of buckets.
65. **`ts_rank_gmean_amean_diff(input1, input2, input3, ..., d)`**: Returns the difference between the geometric mean and arithmetic mean of the time series rank of all inputs over the past d days.
66. **`hump(x, hump=0.01)`**: Limits the amount and magnitude of changes in x, reducing turnover.
67. **`hump_decay(x, p=0.1, relative=False)`**: Ignores values that changed too little compared to previous ones.
68. **`jump_decay(x, d, stddev=False, sensitivity=1.0, force=0.1)`**: Applies a force to x if there is a large jump compared to the previous value.

**Cross-Sectional Operators**

69. **`normalize(x, useStd=false, limit=0.0)`**: Normalizes x using the mean and standard deviation. If `useStd` is true, divides by the standard deviation. If `limit` is not 0.0, limits the normalized values between -`limit` and `limit`.
70. **`one_side(x, side="long")`**: Shifts all instruments up or down so that the Alpha becomes long-only or short-only.
71. **`quantile(x, driver="gaussian", sigma=1.0)`**: Ranks the raw vector, shifts the ranked Alpha vector, and applies a distribution specified by `driver` (gaussian, uniform, or cauchy).
72. **`rank(x, rate=2)`**: Ranks the input among all the instruments and returns an equally distributed number between 0.0 and 1.0.
73. **`rank_by_side(x, rate=2, scale=1)`**: Ranks positive and negative input separately and scales to book size specified by `scale`.
74. **`generalized_rank(x, m=1)`**: Ranks instruments based on the difference between their values raised to the power of m.
75. **`regression_neut(y, x)`**: Conducts the cross-sectional regression on the stocks with y as the target and x as the independent variable. Returns y - (a + b * x), where a and b are the regression coefficients.
76. **`regression_proj(y, x)`**: Conducts the cross-sectional regression on the stocks with y as the target and x as the independent variable. Returns a + b * x, where a and b are the regression coefficients.
77. **`scale(x, scale=1, longscale=1, shortscale=1)`**: Scales input to book size. Can scale long and short positions separately.
78. **`scale_down(x, constant=0)`**: Scales all values in each day proportionately between 0 and 1. Subtracts `constant` from the scaled values.
79. **`truncate(x, maxPercent=0.01)`**: Truncates all values of x to `maxPercent` of the sum of all values.
80. **`vector_neut(x, y)`**: Finds a new vector x* such that x* is orthogonal to y.
81. **`vector_proj(x, y)`**: Returns the vector projection of x onto y.
82. **`rank_gmean_amean_diff(input1, input2, input3, ...)`**: Returns the difference between the geometric mean and arithmetic mean of the cross-sectional rank of all inputs.

**Group Operators**

83. **`group_backfill(x, group, d, std=4.0)`**: If a value of x is NaN for a certain date and instrument, calculates the winsorized mean of all non-NaN values of x for instruments in the same group over the past d days.
84. **`group_coalesce(original_group, group2, group3, ...)`**: Returns the first non-NaN value from the input groups for each instrument and date. Useful for combining grouping fields while ensuring non-overlapping groups.
85. **`group_count(x, group)`**: Returns the number of instruments in the same group that have valid (non-NaN) values of x.
86. **`group_extra(x, weight, group)`**: Replaces NaN values of x with the weighted mean of x for instruments in the same group.
87. **`group_max(x, group)`**: Returns the maximum value of x for all instruments in the same group.
88. **`group_mean(x, weight, group)`**: Returns the weighted mean of x for all instruments in the same group.
89. **`group_median(x, group)`**: Returns the median value of x for all instruments in the same group.
90. **`group_min(x, group)`**: Returns the minimum value of x for all instruments in the same group.
91. **`group_neutralize(x, group)`**: Neutralizes x against groups by subtracting the group mean from each element in the group.
92. **`group_normalize(x, group, constantCheck=false, tolerance=0.01, scale=1)`**: Normalizes x within each group so that the absolute sum of values in each group is 1.
93. **`group_percentage(x, group, percentage=0.5)`**: Returns the percentile value of x within each group.
94. **`group_rank(x, group)`**: Assigns a rank to each element in a group based on its value within the group.
95. **`group_scale(x, group)`**: Scales the values of x within each group to be between 0 and 1.
96. **`group_std_dev(x, group)`**: Returns the standard deviation of x for all instruments in the same group.
97. **`group_sum(x, group)`**: Returns the sum of x for all instruments in the same group.
98. **`group_vector_neut(x, y, g)`**: Returns the vector neutralization of x onto y for each group g.
99. **`group_vector_proj(x, y, g)`**: Returns the vector projection of x onto y for each group g.
100. **`group_zscore(x, group)`**: Calculates the z-score of x within each group.

**Utility Operators**

101. **`convert(x, mode="dollar2share")`**: Converts dollars to shares or shares to dollars.
102. **`inst_pnl(x)`**: Generates the P&L per instrument based on the alpha signal x.
103. **`pasteurize(x)`**: Returns x if x is finite and the underlying instrument is in the Alpha universe. Otherwise, returns NaN.
104. **`bucket(x, buckets="v1 v2 ... vn", range="start, end, step", skipBegin=False, skipEnd=False, skipBoth=False, NANGroup=False)`**: Converts float values into indexes for user-specified buckets. Can define buckets using specific values (`buckets`) or a range (`range`). Options for handling values outside the defined range and NaN values are available.
105. **`kth_element(x, d, k="1", ignore="NAN 0")`**: Returns the k-th value of x from the past d days, ignoring specified values in `ignore`. Useful for backfilling missing data.
106. **`trade_when(x, y, z)`**: Trades the alpha signal y when the trigger condition x is true. Exits the trade when the exit condition z is true.
107. **`left_tail(x, maximum=0)`**: Returns x if x is less than or equal to `maximum`. Otherwise, returns NaN.
108. **`right_tail(x, minimum=0)`**: Returns x if x is greater than or equal to `minimum`. Otherwise, returns NaN.
109. **`tail(x, lower=0, upper=0, newval=0)`**: Returns `newval` if x is within the range specified by `lower` and `upper`. Otherwise, returns x.
110. **`keep(x, f, period=5)`**: Outputs the value of x when f changes and continues to do that for `period` days after f stopped changing. Returns NaN after `period` days since the last change of f.
111. **`filter(x, h="1, 2, 3, 4", t="0.5, 0.05, 0.005")`**: Filters the value using a combination of weighted moving average (h) and recursive part (t). Allows for creating different kinds of filters like linear or exponential decay.
112. **`clamp(x, lower=0, upper=0, inverse=False, mask="")`**: Limits input value between lower and upper bound in `inverse=false` mode (default). When `inverse=true`, values between bounds are replaced with `mask`, while values outside bounds are left as is. `mask` can be 'nearest_bound', 'mean', 'NAN', or any floating point number.
113. **`densify(x)`**: Converts a grouping field with many buckets into a smaller number of buckets, making it computationally efficient. Maps unique values in x to a range from 0 to (n-1), where n is the number of unique values.