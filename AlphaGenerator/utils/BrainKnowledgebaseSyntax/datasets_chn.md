| Field             | Description                                      | Type   | Coverage | Users | Alphas | Dataset                           |
|-------------------|--------------------------------------------------|--------|----------|-------|--------|-----------------------------------|
| adv20             | Average daily volume in past 20 days             | Matrix | 100%     | 889   | 6790   | Price/Volume Data for Equity      |
| cap               | Daily market capitalization (in millions)        | Matrix | 100%     | 1321  | 9335   | Price/Volume Data for Equity      |
| close             | Daily close price                                | Matrix | 100%     | 1648  | 17357  | Price/Volume Data for Equity      |
| country           | Country grouping                                 | Group  | 100%     | 84    | 973    | Price/Volume Data for Equity      |
| dividend          | Dividend                                         | Matrix | 100%     | 90    | 919    | Price/Volume Data for Equity      |
| exchange          | Exchange grouping                                | Group  | 100%     | 139   | 2608   | Price/Volume Data for Equity      |
| high              | Daily high price                                 | Matrix | 100%     | 504   | 6839   | Price/Volume Data for Equity      |
| industry          | Industry grouping                                | Group  | 100%     | 466   | 3168   | Price/Volume Data for Equity      |
| low               | Daily low price                                  | Matrix | 100%     | 414   | 3672   | Price/Volume Data for Equity      |
| market            | Market grouping                                  | Group  | 100%     | 352   | 1631   | Price/Volume Data for Equity      |
| open              | Daily open price                                 | Matrix | 100%     | 488   | 4261   | Price/Volume Data for Equity      |
| returns           | Daily returns                                    | Matrix | 100%     | 745   | 4564   | Price/Volume Data for Equity      |
| sector            | Sector grouping                                  | Group  | 100%     | 1522  | 4387   | Price/Volume Data for Equity      |
| sharesout         | Daily outstanding shares (in millions)           | Matrix | 100%     | 2564  | 5553   | Price/Volume Data for Equity      |
| split             | Stock split ratio                                | Matrix | 100%     | 122   | 1869   | Price/Volume Data for Equity      |
| subindustry       | Subindustry grouping                             | Group  | 100%     | 505   | 2651   | Price/Volume Data for Equity      |
| volume            | Daily volume                                     | Matrix | 100%     | 2918  | 11788  | Price/Volume Data for Equity      |
| vwap              | Daily volume weighted average price              | Matrix | 100%     | 847   | 9286   | Price/Volume Data for Equity      |
| scl12_buzz        | Relative sentiment volume                        | Matrix | 39%      | 16    | 114    | Sentiment Data for Equity         |
| scl12_sentiment   | Sentiment                                        | Matrix | 39%      | 6     | 23     | Sentiment Data for Equity         |
| cashflow_dividends| Cash Dividends (Cash Flow)                       | Matrix | 93%      | 40    | 85     | Company Fundamental Data          |
| cashflow          | Cashflow                                         | Matrix | 100%     | 17    | 87     | Company Fundamental Data          |
| cash              | Cash                                             | Matrix | 100%     | 42    | 88     | Company Fundamental Data          |
| inventory         | Inventories - Total                              | Matrix | 100%     | 26    | 99     | Company Fundamental Data          |
| accounts_payable  | Account Payable/Creditors - Trade                | Matrix | 100%     | 41    | 104    | Company Fundamental Data          |
| liabilities_curr  | Current Liabilities - Total                      | Matrix | 100%     | 44    | 112    | Company Fundamental Data          |
| enterprise_value  | Enterprise Value                                 | Matrix | 82%      | 52    | 115    | Company Fundamental Data          |
| sga_expense       | Selling, General and Administrative Expenses     | Matrix | 100%     | 43    | 116    | Company Fundamental Data          |
| cashflow_fin      | Financing Activities - Net Cash Flow             | Matrix | 97%      | 43    | 128    | Company Fundamental Data          |
| cash_st           | Cash and Short-Term Investments                  | Matrix | 100%     | 33    | 132    | Company Fundamental Data          |
| ppent             | Property Plant and Equipment - Total (Net)       | Matrix | 100%     | 36    | 132    | Company Fundamental Data          |
| cashflow_invst    | Investing Activities - Net Cash Flow             | Matrix | 97%      | 39    | 135    | Company Fundamental Data          |
| operating_income  | Operating Income After Depreciation - Quarterly  | Matrix | 46%      | 104   | 151    | Company Fundamental Data          |
| ebitda            | Earnings Before Interest                         | Matrix | 100%     | 77    | 168    | Company Fundamental Data          |
| ebit              | Earnings Before Interest and Taxes               | Matrix | 99%      | 84    | 190    | Company Fundamental Data          |
| assets_curr       | Current Assets - Total                           | Matrix | 100%     | 74    | 206    | Company Fundamental Data          |
| liabilities       | Liabilities - Total                              | Matrix | 100%     | 66    | 207    | Company Fundamental Data          |
| debt              | Debt                                             | Matrix | 90%      | 71    | 214    | Company Fundamental Data          |
| operating_expense | Operating Expense - Total                        | Matrix | 100%     | 59    | 248    | Company Fundamental Data          |
| cogs              | Cost of Goods Sold                               | Matrix | 100%     | 60    | 276    | Company Fundamental Data          |
| receivable        | Receivables - Total                              | Matrix | 100%     | 38    | 323    | Company Fundamental Data          |
| capex             | Capital Expenditures                             | Matrix | 97%      | 122   | 395    | Company Fundamental Data          |
| income_tax        | Income Taxes - Total                             | Matrix | 100%     | 86    | 468    | Company Fundamental Data          |
| equity            | Common/Ordinary Equity - Total                   | Matrix | 100%     | 80    | 504    | Company Fundamental Data          |
| revenue           | Revenue - Total                                  | Matrix | 100%     | 101   | 504    | Company Fundamental Data          |
| assets            | Assets - Total                                   | Matrix | 100%     | 236   | 834    | Company Fundamental Data          |
| sales             | Sales/Turnover (Net)                             | Matrix | 100%     | 660   | 1262   | Company Fundamental Data          |
| income_beforeextra| Income Before Extraordinary Items                | Matrix | 100%     | 144   | 1598   | Company Fundamental Data          |
| pretax_income     | Pretax Income                                    | Matrix | 100%     | 1103  | 1862   | Company Fundamental Data          |
| retained_earnings | Retained Earnings                                | Matrix | 100%     | 2201  | 2990   | Company Fundamental Data          |
| ani4_afv4_div_median | Dividend per share - median of estimations | Matrix | 66% | 11 | 14 | Analyst Estimate Data          |
| ani4_netprofit_flag | Net profit - forecast type (revision/new/..) | Matrix | 92% | 9 | 14 | Analyst Estimate Data          |
| ani4_afv4_cfps_low | Cash Flow Per Share - The lowest estimation | Matrix | 71% | 15 | 16 | Analyst Estimate Data          |
| ani4_epsr_flag | GAAP Earnings: estimation type (revision/new/..), per share | Matrix | 100% | 5 | 16 | Analyst Estimate Data          |
| ani4_afv4_cfps_median | Cash Flow Per Share - Median value among forecasts | Matrix | 71% | 13 | 17 | Analyst Estimate Data          |
| ani4_afv4_dfs_spe | Earnings per share - std of estimations | Matrix | 54% | 12 | 17 | Analyst Estimate Data          |
| ani4_custom_eps_flag | Earnings per share Non-GAAP - forecast type (revision/new/..) | Matrix | 100% | 7 | 20 | Analyst Estimate Data          |
| ani4_gfv4_median_eps | EPS - aggregation on estimations, 50th-percentile | Matrix | 49% | 12 | 20 | Analyst Estimate Data          |
| ani4_fcfps_flag | Free cash flow per share - forecast type (revision/new/..) | Matrix | 100% | 6 | 20 | Analyst Estimate Data          |
| ani4_afv4_cfps_mean | Cash Flow Per Share - average of estimations | Matrix | 71% | 18 | 22 | Analyst Estimate Data          |
| ani4_tot_gov_fr | Total Goodwill - forecast type (revision/new/..) | Matrix | 100% | 8 | 24 | Analyst Estimate Data          |
| ani4_cfi_flag | Cash Flow From Investing - forecast type (revision/new/..) | Matrix | 100% | 5 | 25 | Analyst Estimate Data          |
| ani4_afv4_eps_number | Earnings per share - number of estimations | Matrix | 88% | 17 | 25 | Analyst Estimate Data          |
| ani4_ffo_flag | Funds from operation - forecast type (revision/new/..) | Matrix | 100% | 6 | 25 | Analyst Estimate Data          |
| ani4_ptp_flag | Pretax income - forecast type (revision/new/..) | Matrix | 96% | 7 | 26 | Analyst Estimate Data          |
| ani4_gfv4_eps_high | Earnings per share - The highest estimation | Matrix | 49% | 17 | 27 | Analyst Estimate Data          |
| ani4_fcf_flag | Free cash flow - forecast type (revision/new/..) | Matrix | 100% | 8 | 29 | Analyst Estimate Data          |
| ani4_afv4_cfps_high | Cash Flow - The highest estimation, per share | Matrix | 71% | 19 | 30 | Analyst Estimate Data          |
| ani4_capex_flag | Capital Expenditures - forecast type (revision/new/..) | Matrix | 100% | 14 | 38 | Analyst Estimate Data          |
| ani4_afv4_eps_low | Earnings per share - The lowest estimation | Matrix | 88% | 23 | 43 | Analyst Estimate Data          |
| ani4_gric_flag | Gross income- forecast type (revision/new/..) | Matrix | 100% | 5 | 44 | Analyst Estimate Data          |
| est_ebit | Earnings before interest and taxes - mean of estimations | Matrix | 35% | 19 | 46 | Analyst Estimate Data          |
| ani4_totassets_flag | Total Assets - forecast type (revision/new/..) | Matrix | 100% | 9 | 47 | Analyst Estimate Data          |
| ani4_afv4_div_std | Dividend per share - std of estimations | Matrix | 29% | 7 | 56 | Analyst Estimate Data          |
| est_netprofit | Net profit: mean of estimations | Matrix | 45% | 28 | 58 | Analyst Estimate Data          |
| ani4_afv4_eps_mean | Earnings per share - mean of estimations | Matrix | 88% | 34 | 80 | Analyst Estimate Data          |
| ani4_adjusted_netincome_ft | Adjusted net income - forecast type (revision/new/..) | Matrix | 100% | 18 | 88 | Analyst Estimate Data          |
| ani4_afv4_median_eps | EPS - aggregation on estimations, 50th-percentile | Matrix | 88% | 34 | 94 | Analyst Estimate Data          |
| ani4_afv4_eps_high | Earnings per share - The highest estimation | Matrix | 88% | 39 | 113 | Analyst Estimate Data          |
| ani4_afv4_div_number | Dividend per share - number of estimations | Matrix | 66% | 16 | 139 | Analyst Estimate Data          |
| ani4_ffoa_flag | Adjusted funds from operation - forecast type (revision/new/..) | Matrix | 100% | 2 | 3 | Analyst Estimate Data          |
| ani4_ebit_median | Earnings before interest and taxes - median of estimations | Matrix | 35% | 4 | 4 | Analyst Estimate Data          |
| ani4_ptp_median | Pretax income- median of estimations | Matrix | 33% | 1 | 4 | Analyst Estimate Data          |
| ani4_ptor_flag | Reported Pretax income - forecast type (revision/new/..) | Matrix | 100% | 3 | 4 | Analyst Estimate Data          |
| ani4_rd_exp_flag | Research and Development Expense - forecast type (revision/new/..) | Matrix | 100% | 3 | 4 | Analyst Estimate Data          |
| est_ptp | Pretax income- mean of estimations | Matrix | 33% | 5 | 5 | Analyst Estimate Data          |
| ani4_gfv4_eps_number | Earnings per share - number of estimations | Matrix | 49% | 4 | 5 | Analyst Estimate Data          |
| ani4_cff_flag | Cash Flow From Financing Activities - forecast type (revision/new/..) | Matrix | 100% | 6 | 6 | Analyst Estimate Data          |
| ani4_afv4_div_high | Dividend per share - The highest estimation | Matrix | 66% | 5 | 6 | Analyst Estimate Data          |
| ani4_ptp_low | Pretax income- The lowest estimation | Matrix | 33% | 5 | 6 | Analyst Estimate Data          |
| ani4_cfo_flag | Cash Flow From Operations - forecast type (revision/new/..) | Matrix | 100% | 5 | 7 | Analyst Estimate Data          |
| ani4_afv4_dfs_spe | Cash Flow Per Share - std of estimations | Matrix | 35% | 4 | 7 | Analyst Estimate Data          |
| ani4_netprofit_low | Net profit- The lowest estimation | Matrix | 45% | 5 | 7 | Analyst Estimate Data          |
| ani4_flag_erbitbtax | Earnings before interest and taxes - forecast type (revision/new/..) | Matrix | 95% | 5 | 8 | Analyst Estimate Data          |
| ani4_gfv4_eps_low | Earnings per share - The lowest estimation | Matrix | 49% | 5 | 8 | Analyst Estimate Data          |
| ani4_gfv4_eps_mean | Earnings per share - mean of estimations | Matrix | 49% | 7 | 9 | Analyst Estimate Data          |
| ani4_netdebt_flag | Net debt - forecast type (revision/new/..) | Matrix | 100% | 4 | 9 | Analyst Estimate Data          |
| ani4_ptp_high | Pretax income- The highest estimation | Matrix | 33% | 5 | 9 | Analyst Estimate Data          |
| ani4_ptp_number | Pretax income- number of estimations | Matrix | 33% | 4 | 9 | Analyst Estimate Data          |
| ani4_afv4_cfps_number | Cash Flow Per Share - number of estimations | Matrix | 71% | 6 | 10 | Analyst Estimate Data          |
| ani4_ebitda_flag | Earnings before interest, taxes, depreciation and amortization - forecast type (revision/new/..) | Matrix | 100% | 5 | 10 | Analyst Estimate Data          |
| ani4_epsa_flag | Earnings per share adjusted by excluding extraordinary items and stock option expenses - forecast type (revision/new/..) | Matrix | 100% | 6 | 10 | Analyst Estimate Data          |
| ani4_netprofit_high | Net profit- The highest estimation | Matrix | 45% | 9 | 10 | Analyst Estimate Data          |
| mdl175_netocloscr | 10-day moving average to close Price Ratio | Matrix | 100% | 25 | 197 | Fundamentals and Technicals |
| mdl175_etop | Earnings to price | Matrix | 100% | 47 | 205 | Fundamentals and Technicals |
| mdl175_olrcc | 10-day commodity channel index | Matrix | 100% | 34 | 206 | Fundamentals and Technicals |
| mdl175_lcap | Natural logarithm of total market values | Matrix | 100% | 16 | 209 | Fundamentals and Technicals |
| mdl175_bias10 | 10-day Bias Ratio / BIAS | Matrix | 100% | 30 | 210 | Fundamentals and Technicals |
| mdl175_grossprofittm | Gross Profit, TTM | Matrix | 100% | 36 | 218 | Fundamentals and Technicals |
| mdl175_ps1yf | Forecast earnings by analyst to market values | Matrix | 90% | 31 | 220 | Fundamentals and Technicals |
| mdl175_realizedvolatility | Realized Volatility | Matrix | 100% | 69 | 225 | Fundamentals and Technicals |
| mdl175_nparentcompanyrgrowrate | Growth rate of net income attributable to shareholders of parent company | Matrix | 100% | 29 | 226 | Fundamentals and Technicals |
| mdl175_edtsvt | 6-day turnover value standard deviation | Matrix | 100% | 70 | 232 | Fundamentals and Technicals |
| mdl175_operatingprofitgrowrate | Operating profit growth rate | Matrix | 100% | 39 | 243 | Fundamentals and Technicals |
| mdl175_02dbsv | 20-day volume standard deviation | Matrix | 100% | 95 | 258 | Fundamentals and Technicals |
| mdl175_grev | Change tendency of forecast earnings by analyst | Matrix | 82% | 41 | 281 | Fundamentals and Technicals |
| mdl175_eatmt | 6-day turnover value moving average | Matrix | 100% | 77 | 284 | Fundamentals and Technicals |
| mdl175_01ame | 10-day exponential moving average | Matrix | 100% | 61 | 288 | Fundamentals and Technicals |
| mdl175_epstm | Earning per share, TTM | Matrix | 100% | 64 | 288 | Fundamentals and Technicals |
| mdl175_beta120 | 120-day Beta value of individual stocks | Matrix | 100% | 39 | 290 | Fundamentals and Technicals |
| mdl175_gor | Return on assets | Matrix | 100% | 54 | 294 | Fundamentals and Technicals |
| mdl175_02dbsvt | 20-day turnover value standard deviation | Matrix | 100% | 111 | 333 | Fundamentals and Technicals |
| mdl175_darev | Changes of forecast earnings by analyst | Matrix | 78% | 81 | 341 | Fundamentals and Technicals |
| mdl175_beta252 | 252-day Beta value of individual stocks | Matrix | 100% | 54 | 422 | Fundamentals and Technicals |
| mdl175_01am | 10-day moving average | Matrix | 100% | 77 | 454 | Fundamentals and Technicals |
| mdl175_beta60 | 60-day beta value of individual stocks | Matrix | 100% | 61 | 491 | Fundamentals and Technicals |
| mdl175_01amev | 10-day Exponential moving average of volume | Matrix | 100% | 96 | 531 | Fundamentals and Technicals |
| mdl175_moneyflow20 | 20-day money flow | Matrix | 100% | 121 | 547 | Fundamentals and Technicals |
| mdl175_beta20 | 20-day Beta value of individual stocks | Matrix | 100% | 81 | 574 | Fundamentals and Technicals |
| mdl175_01dbsv | 10-day volume standard deviation | Matrix | 100% | 243 | 727 | Fundamentals and Technicals |
| mdl175_revenuettm | Revenue, TTM | Matrix | 100% | 1496 | 2030 | Fundamentals and Technicals |
| mdl175_02amvt | 20-day turnover value moving average | Matrix | 100% | 1491 | 2261 | Fundamentals and Technicals |
| mdl175_volatility | Volatility of daily turnover during the last 20 days | Matrix | 100% | 1649 | 2948 | Fundamentals and Technicals |
| mdl175_opercashflowps | Net cashflow from operation activities per share | Matrix | 100% | 52 | 119 | Fundamentals and Technicals |
| mdl175_chaikinoscillator | Chaikin oscillator | Matrix | 100% | 34 | 121 | Fundamentals and Technicals |
| mdl175_roaebitttm | ROA calculated by EBIT, TTM | Matrix | 100% | 24 | 122 | Fundamentals and Technicals |
| mdl175_21amev | 12-day Exponential moving average of volume | Matrix | 100% | 29 | 122 | Fundamentals and Technicals |
| mdl175_davw | William's variable accumulation distribution | Matrix | 100% | 23 | 123 | Fundamentals and Technicals |
| mdl175_swingindex | Swing index | Matrix | 100% | 26 | 123 | Fundamentals and Technicals |
| mdl175_revenuettm | Total Revenue, TTM | Matrix | 100% | 68 | 124 | Fundamentals and Technicals |
| mdl175_torps | Total revenue per share | Matrix | 100% | 37 | 129 | Fundamentals and Technicals |
| mdl175_dasrev | Changes of forecast sales by analyst (to 60 days ago) | Matrix | 72% | 40 | 130 | Fundamentals and Technicals |
| mdl175_gainlossvarinceratio20 | 20-day Gain Loss Variance Ratio | Matrix | 100% | 26 | 130 | Fundamentals and Technicals |
| mdl175_peindu | (PE-PE industry average) to PE industry standard deviation | Matrix | 100% | 46 | 130 | Fundamentals and Technicals |
| mdl175_netprofitttm | Net Profit, TTM | Matrix | 100% | 47 | 134 | Fundamentals and Technicals |
| mdl175_6crlp | 6-day price linear regression coefficient | Matrix | 100% | 36 | 134 | Fundamentals and Technicals |
| mdl175_pehist120 | PE to Average PE over the last six months | Matrix | 100% | 28 | 134 | Fundamentals and Technicals |
| mdl175_operatingrevenuegrowrate | Operating revenue growth rate | Matrix | 100% | 25 | 136 | Fundamentals and Technicals |
| mdl175_tvp | Price and volume trend | Matrix | 100% | 25 | 136 | Fundamentals and Technicals |
| mdl175_adminexpensettm | Administration expense, TTM | Matrix | 100% | 40 | 137 | Fundamentals and Technicals |
| mdl175_02am | 20-day moving average | Matrix | 100% | 30 | 143 | Fundamentals and Technicals |
| mdl175_5amev | 5-day Exponential moving average of volume | Matrix | 100% | 34 | 143 | Fundamentals and Technicals |
| mdl175_npparentcompanycutyoy | Net Profit after non-recurring gains and losses year on year | Matrix | 100% | 24 | 146 | Fundamentals and Technicals |
| mdl175_retainedearnings | Total retained earnings | Matrix | 100% | 103 | 149 | Fundamentals and Technicals |
| mdl175_egibslong | Long-term predicted earnings growth | Matrix | 93% | 35 | 152 | Fundamentals and Technicals |
| mdl175_021am | 120-day moving average | Matrix | 100% | 30 | 152 | Fundamentals and Technicals |
| mdl175_artdays | Accounts receivable turnover days | Matrix | 100% | 22 | 152 | Fundamentals and Technicals |
| mdl175_pehist250 | PE to Average PE over the past year | Matrix | 100% | 22 | 158 | Fundamentals and Technicals |
| mdl175_price3m | The current share price is divided by the stock price average over the past three months: -1 | Matrix | 100% | 24 | 161 | Fundamentals and Technicals |
| mdl175_minusdi | Minus directional indicator | Matrix | 100% | 17 | 161 | Fundamentals and Technicals |
| mdl175_62amev | 26-day Exponential moving average of volume | Matrix | 100% | 39 | 166 | Fundamentals and Technicals |
| mdl175_gsrev | Change tendency of forecast sales by analyst, Sum of 60 days' DASREV | Matrix | 77% | 44 | 176 | Fundamentals and Technicals |
| mdl175_rcndd | Downside correlation | Matrix | 100% | 44 | 185 | Fundamentals and Technicals |
| mdl175_sbipe | Forecast earnings by analyst to market values | Matrix | 90% | 28 | 118 | Fundamentals and Technicals |
| mdl175_6tra | 6-day average true range | Matrix | 100% | 24 | 116 | Fundamentals and Technicals |
| mdl175_bullpower | Mediator in calculating Elder, Bull power indicator | Matrix | 100% | 28 | 115 | Fundamentals and Technicals |
| mdl175_operatingprofitps | Operating Profit per share | Matrix | 100% | 34 | 115 | Fundamentals and Technicals |
| mdl175_fearng | Forecasted growth rate of earnings | Matrix | 90% | 35 | 113 | Fundamentals and Technicals |
| mdl175_operateprofitttm | Operating Profit, TTM | Matrix | 100% | 28 | 112 | Fundamentals and Technicals |
| mdl175_mktvalue | Total market value | Matrix | 100% | 37 | 110 | Fundamentals and Technicals |
| mdl175_orgs | Five-year sales growth | Matrix | 100% | 21 | 109 | Fundamentals and Technicals |
| mdl175_02ame | 20-day exponential moving average | Matrix | 100% | 37 | 107 | Fundamentals and Technicals |
| mdl175_5am | 5-day moving average | Matrix | 100% | 26 | 107 | Fundamentals and Technicals |
| mdl175_da | Accumulation / Distribution Line | Matrix | 100% | 26 | 106 | Fundamentals and Technicals |
| mdl175_vmacd | Volume moving average convergence and divergence | Matrix | 100% | 22 | 106 | Fundamentals and Technicals |
| mdl175_gainlossvarianceratio60 | 60-day Gain Loss Variance Ratio | Matrix | 100% | 19 | 104 | Fundamentals and Technicals |
| mdl175_gainlossvarianceratio120 | 120-day Gain Loss Variance Ratio | Matrix | 100% | 26 | 103 | Fundamentals and Technicals |
| mdl175_hbeta | Historical daily beta | Matrix | 100% | 32 | 102 | Fundamentals and Technicals |
| mdl175_skewness | Skewness of price druing the last 20 days | Matrix | 100% | 22 | 100 | Fundamentals and Technicals |
| mdl175_bias5 | 5-day Bias Ratio / BIAS | Matrix | 100% | 22 | 99 | Fundamentals and Technicals |
| mdl175_021ame | 120-day exponential moving average | Matrix | 100% | 48 | 98 | Fundamentals and Technicals |
| mdl175_orge | Five-year earnings growth | Matrix | 100% | 16 | 96 | Fundamentals and Technicals |
| mdl175_netprofitapttm | Net Profit attributable to parent company owners, TTM | Matrix | 100% | 25 | 92 | Fundamentals and Technicals |
| mdl175_volumn3m | The volume over the last five days divided by the five-day volume average over the past three months and then multiplied by the yield over the last three months | Matrix | 100% | 28 | 92 | Fundamentals and Technicals |
| mdl175_cashdividendcover | Cash Dividend Cover | Matrix | 89% | 70 | 92 | Fundamentals and Technicals |
| mdl175_ctop | Cash flow to price | Matrix | 87% | 29 | 91 | Fundamentals and Technicals |
| mdl175_6dca | 6-day accumulation / Distribution | Matrix | 100% | 45 | 90 | Fundamentals and Technicals |
| mdl175_retainedearningsps | Retained Earnings per share | Matrix | 100% | 52 | 89 | Fundamentals and Technicals |
| mdl175_debtassetratio | Debt to total assets | Matrix | 100% | 69 | 88 | Fundamentals and Technicals |
| mdl175_netassetps | Net assets per share | Matrix | 100% | 20 | 87 | Fundamentals and Technicals |
| mdl175_zid | Mediator in calculating DDI | Matrix | 100% | 18 | 86 | Fundamentals and Technicals |
| mdl175_cibb | BBI / Close price | Matrix | 100% | 26 | 85 | Fundamentals and Technicals |