# Human Evaluation Rubric - Fundamental & News Agent

## Evaluation Criteria (1-5 Scale)

### 1. Usefulness (1-5)
- **5 (Excellent)**: Response provides comprehensive fundamental analysis with actionable insights
- **4 (Good)**: Response addresses the query completely with good analysis
- **3 (Adequate)**: Response addresses the query but may lack depth or context
- **2 (Poor)**: Response partially addresses the query but misses key elements
- **1 (Very Poor)**: Response does not address the query or is not useful

### 2. Trustworthiness (1-5)
- **5 (Excellent)**: All financial data is clearly sourced, accurate, and verifiable. No hallucinations.
- **4 (Good)**: Data appears accurate with clear sources. No obvious errors.
- **3 (Adequate)**: Data seems reasonable but sources may be unclear or some uncertainty exists
- **2 (Poor)**: Some data appears questionable, unsourced, or potentially invented
- **1 (Very Poor)**: Data appears incorrect, invented, or completely unsourced. Hallucinations present.

### 3. Reasoning Quality (1-5)
- **5 (Excellent)**: Clear, logical reasoning with well-explained methodology and calculations
- **4 (Good)**: Sound reasoning with adequate explanation of methodology
- **3 (Adequate)**: Reasoning is present but may lack detail or clarity in methodology
- **2 (Poor)**: Reasoning is unclear, flawed, or methodology is not explained
- **1 (Very Poor)**: No clear reasoning or methodology provided

### 4. Decision Confidence (1-5)
- **5 (Excellent)**: High confidence in the analysis quality and accuracy
- **4 (Good)**: Good confidence with minor uncertainties acknowledged
- **3 (Adequate)**: Moderate confidence with some uncertainties or limitations noted
- **2 (Poor)**: Low confidence due to unclear data, methodology, or potential errors
- **1 (Very Poor)**: Very low confidence, analysis quality is questionable

## Notes for Evaluators

- **Hallucinations**: CRITICAL - Any invented financial numbers, ratios, or unsupported claims should result in automatic failure
- **Financial Statement Accuracy**: Ratios and financial metrics must be correctly calculated or clearly marked as estimates
- **News Sentiment**: Sentiment analysis should be based on actual news, not invented articles
- **Sources**: All financial data should be traceable to sources or clearly marked as estimates
- **Uncertainty**: If data is uncertain or unavailable, the agent must explicitly state this

## Pass Criteria

- All dimension scores >= 3.0
- No hallucinations detected
- Overall average score >= 3.5
