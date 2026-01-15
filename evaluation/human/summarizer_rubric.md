# Human Evaluation Rubric - Final Answer / Summarizer Agent

## Evaluation Criteria (1-5 Scale)

### 1. Usefulness (1-5)
- **5 (Excellent)**: Response provides comprehensive, actionable investment recommendation
- **4 (Good)**: Response addresses the query completely with good synthesis
- **3 (Adequate)**: Response addresses the query but may lack depth or clarity
- **2 (Poor)**: Response partially addresses the query but misses key elements
- **1 (Very Poor)**: Response does not address the query or is not useful

### 2. Trustworthiness (1-5)
- **5 (Excellent)**: All information is well-sourced, accurate, and synthesis is faithful to agent outputs
- **4 (Good)**: Information appears accurate and synthesis is mostly faithful
- **3 (Adequate)**: Information seems reasonable but synthesis may have minor issues
- **2 (Poor)**: Some information appears questionable or synthesis is not faithful
- **1 (Very Poor)**: Information appears incorrect or synthesis misrepresents agent outputs

### 3. Reasoning Quality (1-5)
- **5 (Excellent)**: Clear, logical reasoning that effectively synthesizes all agent outputs
- **4 (Good)**: Sound reasoning with good synthesis of agent outputs
- **3 (Adequate)**: Reasoning is present but synthesis may lack coherence
- **2 (Poor)**: Reasoning is unclear or synthesis is incoherent
- **1 (Very Poor)**: No clear reasoning or poor synthesis

### 4. Decision Confidence (1-5)
- **5 (Excellent)**: High confidence in the recommendation and synthesis quality
- **4 (Good)**: Good confidence with minor uncertainties acknowledged
- **3 (Adequate)**: Moderate confidence with some uncertainties
- **2 (Poor)**: Low confidence due to unclear reasoning or poor synthesis
- **1 (Very Poor)**: Very low confidence, recommendation quality is questionable

## Notes for Evaluators

- **Synthesis Quality**: The response should effectively combine insights from market data, fundamentals, and risk analysis
- **Coherence**: The final answer should be coherent and not contradictory
- **Faithfulness**: The synthesis should accurately represent the agent outputs without adding unsupported claims
- **Actionability**: The recommendation should be clear and actionable
- **Uncertainty**: If there are limitations or uncertainties, they should be explicitly stated

## Pass Criteria

- All dimension scores >= 3.0
- Synthesis is faithful to agent outputs
- Overall average score >= 3.5
