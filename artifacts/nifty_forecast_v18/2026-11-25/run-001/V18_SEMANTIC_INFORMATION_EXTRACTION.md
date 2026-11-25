# NIFTY V18 — Semantic information extraction

Deterministic rules map exchange subject and summary fields to events such as earnings, guidance, order wins, contract cancellations, acquisitions, divestments, expansion, financing, credit, regulation, litigation, management, dividends and buybacks. Signed text requires explicit business or risk language. Positive and negative cues can coexist, and ambiguous outcomes remain unclassified. The output retains the supporting short phrases and flags explicit amounts, implementation horizons and uncertainty. A fixed alternative uses category-level directional proxies as a falsification arm. No language model was used, so all feature values come from a shared, inspectable procedure.

The independently selected attachment audit attempted **92** disclosed PDFs and extracted readable text from **90**. The document supplied a directional cue missing from the exchange summary in **21** cases. **73** had a monetary or percentage fragment and **4** had an explicit horizon phrase. A monetary fragment alone supplies no validated label for margin, earnings or guidance. The audit retained page references and excerpt cues. Across **3** matched signed cases after the initial reaction, summary and attachment rules got **2** and **2** signs right. The attachment exercise is a small coverage and disagreement diagnostic. Its PDFs were retrieved retrospectively from historically posted URLs, so undocumented replacements remain possible. The main forecast tests use archived public descriptions and versioned structured results.

One checked example shows why sentence-level cues need context. In IndiGo's December 10, 2025 disclosure, the Q3 FY2025–26 table records an earlier expectation of high-teens capacity growth and revises it down to high-single-digit or low-double-digit growth. It also changes expected passenger unit revenue from roughly flat or slightly growing to mid-single-digit deterioration. The same page cites a **10%** mandated scheduled-flight reduction and explicitly leaves the full financial impact unquantified. The filing became eligible at **21:54:29 IST**. The inexpensive phrase rule returned a mixed signal because the table contains both old and new descriptions. This manually checked case illustrates the extraction failure and contributes no manual override to the historical model. [Filed press release, page 2](sources/disclosure-sample/2025-7470.pdf)

| horizon | cutoff | candidate | control | metric | n | disjoint | candidate loss | control loss | gain | adjusted low21 | adjusted high21 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | preauction_0855 | text_given_counts | counts | brier | 265 | 53 | 0.244526 | 0.243837 | -0.000689 | -0.008929 | 0.007551 |
| 5 | preauction_0855 | text_given_counts | counts | crps | 265 | 53 | 0.010928 | 0.010874 | -0.000055 | -0.000299 | 0.000189 |
| 5 | preauction_0855 | weighted_text | counts | brier | 265 | 53 | 0.244613 | 0.243837 | -0.000776 | -0.003378 | 0.001825 |
| 5 | preauction_0855 | weighted_text | counts | crps | 265 | 53 | 0.010906 | 0.010874 | -0.000032 | -0.000094 | 0.000031 |
| 5 | preauction_0855 | alternative_text | counts | brier | 265 | 53 | 0.244871 | 0.243837 | -0.001034 | -0.002161 | 0.000093 |
| 5 | preauction_0855 | alternative_text | counts | crps | 265 | 53 | 0.010888 | 0.010874 | -0.000015 | -0.000060 | 0.000030 |
| 5 | preauction_0855 | material_only | counts | brier | 265 | 53 | 0.246663 | 0.243837 | -0.002826 | -0.011318 | 0.005665 |
| 5 | preauction_0855 | material_only | counts | crps | 265 | 53 | 0.010930 | 0.010874 | -0.000057 | -0.000255 | 0.000142 |
| 5 | previous_1700 | text_given_counts | counts | brier | 265 | 53 | 0.241012 | 0.244096 | 0.003084 | -0.005037 | 0.011206 |
| 5 | previous_1700 | text_given_counts | counts | crps | 265 | 53 | 0.010927 | 0.010935 | 7.97e-06 | -0.000186 | 0.000202 |
| 5 | previous_1700 | weighted_text | counts | brier | 265 | 53 | 0.243901 | 0.244096 | 0.000195 | -0.002721 | 0.003110 |
| 5 | previous_1700 | weighted_text | counts | crps | 265 | 53 | 0.010936 | 0.010935 | -7.88e-07 | -0.000061 | 0.000060 |
| 5 | previous_1700 | alternative_text | counts | brier | 265 | 53 | 0.245207 | 0.244096 | -0.001111 | -0.003096 | 0.000874 |
| 5 | previous_1700 | alternative_text | counts | crps | 265 | 53 | 0.010960 | 0.010935 | -0.000025 | -0.000066 | 0.000015 |
| 5 | previous_1700 | material_only | counts | brier | 265 | 53 | 0.247236 | 0.244096 | -0.003140 | -0.014174 | 0.007894 |
| 5 | previous_1700 | material_only | counts | crps | 265 | 53 | 0.011007 | 0.010935 | -0.000072 | -0.000326 | 0.000181 |
| 21 | preauction_0855 | text_given_counts | counts | brier | 217 | 11 | 0.346838 | 0.347264 | 0.000426 | -0.005135 | 0.005987 |
| 21 | preauction_0855 | text_given_counts | counts | crps | 217 | 11 | 0.030377 | 0.030236 | -0.000141 | -0.000558 | 0.000275 |
| 21 | preauction_0855 | weighted_text | counts | brier | 217 | 11 | 0.345244 | 0.347264 | 0.002019 | -0.002919 | 0.006958 |
| 21 | preauction_0855 | weighted_text | counts | crps | 217 | 11 | 0.030224 | 0.030236 | 0.000012 | -0.000172 | 0.000195 |
| 21 | preauction_0855 | alternative_text | counts | brier | 217 | 11 | 0.348197 | 0.347264 | -0.000934 | -0.004321 | 0.002454 |
| 21 | preauction_0855 | alternative_text | counts | crps | 217 | 11 | 0.030263 | 0.030236 | -0.000027 | -0.000307 | 0.000253 |
| 21 | preauction_0855 | material_only | counts | brier | 217 | 11 | 0.348236 | 0.347264 | -0.000973 | -0.002687 | 0.000741 |
| 21 | preauction_0855 | material_only | counts | crps | 217 | 11 | 0.030286 | 0.030236 | -0.000050 | -0.000361 | 0.000262 |

[PDF coverage and source excerpts](attachment-content-audit.csv) · [Matched attachment exercise](attachment-comparison.json) · [Text evidence and labels](extraction-examples.csv) · [Text and category tests](endpoint-paired-comparisons.csv)
