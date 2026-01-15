# How to Add Test Queries to the UI

## Location in HTML File

The test queries are located in `evaluation/ui/test_queries.html`. Each agent has its own section.

## Structure

Each test query follows this HTML structure:

```html
<div class="test-item">
    <div class="test-id">test_id_here</div>
    <div class="test-query">Your test query question here</div>
    <div class="test-meta">
        <span class="meta-badge">Metadata 1</span>
        <span class="meta-badge">Metadata 2</span>
    </div>
</div>
```

## Where to Insert New Test Queries

### 1. Market Data Agent - Hard Tests
**Location:** Around line 280-350 in `test_queries.html`

```html
<div class="test-category">
    <h3>Hard Tests <span class="test-type type-hard">Hard</span></h3>
    
    <!-- ADD NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">market_XXX</div>
        <div class="test-query">Your new test query</div>
        <div class="test-meta">
            <span class="meta-badge">Symbol: AAPL</span>
            <span class="meta-badge">Date: 2024-01-15</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

### 2. Market Data Agent - Retrieval Tests
**Location:** Around line 350-400

```html
<div class="test-category">
    <h3>Retrieval Tests <span class="test-type type-retrieval">Retrieval</span></h3>
    
    <!-- ADD NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">market_retrieval_XXX</div>
        <div class="test-query">Your retrieval test query</div>
        <div class="test-meta">
            <span class="meta-badge">Check: Ticker mentioned</span>
            <span class="meta-badge">Check: Date range correct</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

### 3. Fundamental & News Agent - LLM Tests
**Location:** Around line 450-500

```html
<div class="test-category">
    <h3>LLM Tests <span class="test-type type-llm">LLM</span></h3>
    
    <!-- ADD NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">fundamental_llm_XXX</div>
        <div class="test-query">Your LLM test query</div>
        <div class="test-meta">
            <span class="meta-badge">Type: Analysis type</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

### 4. Portfolio & Risk Agent - Hard Tests
**Location:** Around line 550-600

```html
<div class="test-category">
    <h3>Hard Tests <span class="test-type type-hard">Hard</span></h3>
    
    <!-- ADD NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">portfolio_additional_XXX</div>
        <div class="test-query">Your portfolio test query</div>
        <div class="test-meta">
            <span class="meta-badge">Analysis: Type</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

### 5. Summarizer Agent - LLM Tests
**Location:** Around line 650-700

```html
<div class="test-category">
    <h3>LLM Tests <span class="test-type type-llm">LLM</span></h3>
    
    <!-- ADD NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">summarizer_llm_XXX</div>
        <div class="test-query">Your summarizer test query</div>
        <div class="test-meta">
            <span class="meta-badge">Type: Summary type</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

### 6. System-Level Tests
**Location:** Around line 750-850

```html
<div class="test-category">
    <h3>Cross-Agent Tests <span class="test-type type-system">System</span></h3>
    
    <!-- ADD NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">system_XXX</div>
        <div class="test-query">Your system test query</div>
        <div class="test-meta">
            <span class="meta-badge">Check: Validation type</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

## Test Type Classes

Use the appropriate class for test type badge:

- `type-hard` - For hard/deterministic tests
- `type-llm` - For LLM-based tests
- `type-retrieval` - For retrieval/RAG tests
- `type-human` - For human evaluation tests
- `type-system` - For system-level tests

## Example: Adding a New Market Data Test

```html
<!-- Find the Hard Tests section for Market Data Agent (around line 278) -->
<div class="test-category">
    <h3>Hard Tests <span class="test-type type-hard">Hard</span></h3>
    
    <!-- Existing tests... -->
    
    <!-- ADD YOUR NEW TEST HERE -->
    <div class="test-item">
        <div class="test-id">market_008</div>
        <div class="test-query">What is the current market cap of AAPL?</div>
        <div class="test-meta">
            <span class="meta-badge">Symbol: AAPL</span>
            <span class="meta-badge">Metric: Market Cap</span>
        </div>
    </div>
    <!-- END OF NEW TEST -->
    
</div>
```

## Quick Reference: Line Numbers

- **Market Data - Hard Tests:** ~280-350
- **Market Data - Retrieval Tests:** ~350-400
- **Fundamental - LLM Tests:** ~450-500
- **Fundamental - Retrieval Tests:** ~500-550
- **Portfolio - Hard Tests:** ~550-600
- **Portfolio - LLM Tests:** ~600-650
- **Summarizer - LLM Tests:** ~650-700
- **Summarizer - Human Tests:** ~700-750
- **System - Cross-Agent:** ~750-800
- **System - Regression:** ~800-850
- **System - Edge Cases:** ~850-900

## Tips

1. **Keep IDs unique:** Use consistent naming (e.g., `market_XXX`, `fundamental_llm_XXX`)
2. **Add metadata badges:** Include relevant metadata for filtering/searching
3. **Maintain structure:** Follow the existing HTML structure exactly
4. **Test the search:** The search function filters by text content, so make sure your query text is descriptive

## Visual Guide

When you open `test_queries.html` in a code editor:

1. Look for comments like `<!-- Market Data Agent -->`
2. Find the `<div class="test-category">` section for the test type
3. Add your new `<div class="test-item">` inside that category
4. Save and refresh the browser to see your new test
