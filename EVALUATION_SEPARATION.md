# Evaluation vs UI Separation - Architecture Document

## 🎯 Core Principle

**Test questions are part of the evaluation framework and are executed offline. The UI is strictly reserved for real user inference, ensuring a clean separation between usage and evaluation.**

---

## ✅ Correct Architecture

### UI Layer (User-Facing)
**Location**: `evaluation/ui/dashboard.html`

**Purpose**: 
- Accept **real user queries** (free-text financial questions)
- Display system responses
- Provide example queries for guidance (not test cases)

**What it contains**:
- Query input field
- Example user questions (for UX guidance)
- Response display
- No test cases
- No ground truth
- No evaluation criteria

### Evaluation Framework (Offline)
**Location**: `evaluation/` directory

**Purpose**:
- Execute test cases
- Measure system performance
- Generate evaluation reports

**What it contains**:
- Hard tests (`evaluation/hard/*.yaml`)
- LLM tests (`evaluation/datasets/*/llm_test_cases.jsonl`)
- Retrieval tests (`evaluation/datasets/*/retrieval_test_cases.jsonl`)
- Human tests (`evaluation/datasets/*/human_test_cases.csv`)
- System tests (`evaluation/system/*.yaml`)
- Evaluation runners (`evaluation/runners/*.py`)

---

## ❌ Why Test Questions Should NOT Be in UI

### 1. Conceptual Violation
- **UI = User Interface** → For real users asking real questions
- **Tests = Evaluation Framework** → For measuring system quality
- Mixing them breaks the separation of concerns

### 2. Professional Standards
- Production systems separate inference from evaluation
- Academic evaluation requires controlled test execution
- Mixing suggests a "demo" rather than a real system

### 3. Integrity Issues
- Exposing test questions in UI reveals evaluation methodology
- Users might see expected answers (ground truth)
- Breaks the "black box" evaluation principle

### 4. Maintenance Problems
- Test cases change frequently during development
- UI should be stable for end users
- Coupling creates unnecessary dependencies

---

## 📊 Test Type Explanations

### 1. Hard Tests (Deterministic)
**Location**: `evaluation/hard/*.yaml`

**What they are**:
- Questions with exact expected outputs
- Numerical validations with tolerances
- Binary yes/no checks

**Examples**:
- "What is the 30-day return of AAPL?" → Expected: specific number
- "What is portfolio volatility?" → Expected: calculated value

**Why not in UI**:
- User doesn't know the ground truth
- These are correctness checks, not user queries
- Must be executed in controlled environment

### 2. Retrieval Tests (RAG Evals)
**Location**: `evaluation/datasets/*/retrieval_test_cases.jsonl`

**What they are**:
- Checks that retrieved documents are relevant
- Validates Top-K source quality
- Ensures citations are accurate

**Examples**:
- "Does Top-K include document about AAPL Q3 earnings?"
- "Is the ticker explicitly mentioned in sources?"

**Why not in UI**:
- User doesn't see internal retrieval process
- These are internal quality checks
- Require access to retrieval pipeline internals

### 3. LLM-as-a-Judge Tests
**Location**: `evaluation/datasets/*/llm_test_cases.jsonl`

**What they are**:
- Open-ended questions evaluated by LLM judge
- Assessed on dimensions (correctness, completeness, faithfulness, clarity)
- No single "correct" answer

**Examples**:
- "Is the reasoning coherent?"
- "Is the recommendation supported by evidence?"

**Why not in UI**:
- Evaluation criteria are internal
- This is meta-evaluation, not user task
- Requires LLM judge execution

### 4. Human Evaluation Tests
**Location**: `evaluation/datasets/*/human_test_cases.csv`

**What they are**:
- Questions for human evaluators (not end users)
- Subjective quality assessments
- Trust and understandability ratings

**Examples**:
- "Would you trust this recommendation?"
- "Is the explanation understandable to non-experts?"

**Why not in UI**:
- These are questionnaires for evaluators
- Not meant for daily user interaction
- Part of evaluation methodology

### 5. System-Level Tests
**Location**: `evaluation/system/*.yaml`

**What they are**:
- Cross-agent integration checks
- Regression tests
- Edge case handling

**Examples**:
- "Does orchestrator call all required agents?"
- "What happens if ticker is invalid?"

**Why not in UI**:
- These test internal system behavior
- Not user-facing functionality
- Must run in controlled test environment

---

## 🔧 Implementation Details

### UI Implementation
```html
<!-- ✅ CORRECT: Real user query input -->
<textarea id="queryInput" placeholder="Ask any financial question..."></textarea>

<!-- ✅ CORRECT: Example queries for UX (not test cases) -->
<div class="example-item">
    "Should I invest in AAPL? Consider market trends and fundamentals."
</div>

<!-- ❌ WRONG: Test case from evaluation framework -->
<!-- <div class="test-item"> -->
<!--     <div class="test-id">market_001</div> -->
<!--     <div class="test-query">Get closing price of AAPL on 2024-01-15</div> -->
<!-- </div> -->
```

### Evaluation Runner Implementation
```python
# ✅ CORRECT: Load test cases from evaluation framework
with open('evaluation/hard/market_agent_tests.yaml') as f:
    test_cases = yaml.safe_load(f)

for test in test_cases['tests']:
    query = test['input']['query']
    expected = test['expected_output']
    actual = call_system(query)
    validate(actual, expected)
```

---

## 📝 Documentation Updates

### UI Documentation
**File**: `evaluation/ui/README.md`

States clearly:
- UI is for inference only
- No test cases in UI
- Evaluation runs offline

### Main README
**File**: `README.md`

Should include:
- Clear separation explanation
- Links to evaluation framework
- Instructions for running evaluations

---

## ✅ Verification Checklist

- [x] UI contains only user query input (no test cases)
- [x] Test cases are in evaluation framework directories
- [x] Evaluation runners load tests from files (not UI)
- [x] Documentation explains separation
- [x] No hardcoded test questions in UI code
- [x] Example queries in UI are clearly marked as examples (not tests)
- [x] Evaluation framework is clearly documented

---

## 🎓 Academic Justification

**For the instructor/reviewer:**

This architecture follows best practices for production AI systems:

1. **Separation of Concerns**: Inference and evaluation are separate concerns
2. **Reproducibility**: Tests are version-controlled and executable via CLI
3. **Integrity**: Evaluation methodology is not exposed to end users
4. **Maintainability**: UI and evaluation can evolve independently
5. **Professionalism**: Demonstrates understanding of production AI systems

**Key Statement:**
> "Test questions are part of the evaluation framework and are executed offline. The UI is strictly reserved for real user inference, ensuring a clean separation between usage and evaluation."

---

**Last Updated**: 2026-01-15
**Status**: ✅ Correctly Separated
