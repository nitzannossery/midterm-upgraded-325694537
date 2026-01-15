# Human Evaluation Rubric - Market Data Agent

## Evaluation Criteria (1-5 Scale)

### 1. Usefulness (1-5)
- **5 (Excellent)**: Response provides exactly what was requested with additional valuable context
- **4 (Good)**: Response addresses the query completely and is actionable
- **3 (Adequate)**: Response addresses the query but may lack some context or detail
- **2 (Poor)**: Response partially addresses the query but misses key elements
- **1 (Very Poor)**: Response does not address the query or is not useful

### 2. Trustworthiness (1-5)
- **5 (Excellent)**: All data is clearly sourced, accurate, and verifiable
- **4 (Good)**: Data appears accurate with clear sources or methodology
- **3 (Adequate)**: Data seems reasonable but sources may be unclear
- **2 (Poor)**: Some data appears questionable or unsourced
- **1 (Very Poor)**: Data appears incorrect, invented, or completely unsourced

### 3. Reasoning Quality (1-5)
- **5 (Excellent)**: Clear, logical reasoning with well-explained methodology
- **4 (Good)**: Sound reasoning with adequate explanation
- **3 (Adequate)**: Reasoning is present but may lack detail or clarity
- **2 (Poor)**: Reasoning is unclear or flawed
- **1 (Very Poor)**: No clear reasoning or methodology provided

### 4. Decision Confidence (1-5)
- **5 (Excellent)**: High confidence in the data quality and accuracy
- **4 (Good)**: Good confidence with minor uncertainties acknowledged
- **3 (Adequate)**: Moderate confidence with some uncertainties
- **2 (Poor)**: Low confidence due to unclear data or methodology
- **1 (Very Poor)**: Very low confidence, data quality is questionable

## Notes for Evaluators

- **Hallucinations**: Any invented numbers, unsupported claims, or fabricated data should result in automatic failure
- **Uncertainty**: If data is uncertain, the agent should explicitly state this
- **Sources**: All financial data should be traceable or clearly marked as estimates
- **Completeness**: Response should address all aspects of the query

## Pass Criteria

- All dimension scores >= 3.0
- No hallucinations detected
- Overall average score >= 3.5
