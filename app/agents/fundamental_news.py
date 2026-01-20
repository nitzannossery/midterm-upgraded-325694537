from typing import Dict, Any, List
from app.agents.base import Agent
from app.schemas import AgentOutput, Source
from app.llm.google_client import GoogleLLMClient
import yfinance as yf
import re

class FundamentalNewsAgent(Agent):
    name = "Fundamental & News Agent"
    
    def __init__(self):
        """Initialize agent with Google LLM client."""
        try:
            self.llm_client = GoogleLLMClient()
            self.use_llm = True
        except Exception:
            self.llm_client = None
            self.use_llm = False

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        """Process fundamental analysis query with needle-in-haystack support."""
        sources = context.get("sources", [])
        
        # CRITICAL: Filter out placeholder sources
        real_sources = [s for s in sources if s.id != "src1" and "Example" not in s.title]
        
        # Extract fundamental metrics from query (needle extraction)
        fundamental_data = self._extract_fundamental_metrics(query, real_sources)
        
        # Combine sources
        all_sources = list(real_sources) + fundamental_data.get("new_sources", [])
        
        # If no real sources, try to get data directly
        if not all_sources or all([s.id == "src1" or "Example" in s.title for s in all_sources]):
            # Force data extraction
            direct_data = self._get_direct_financial_data(query)
            if direct_data:
                all_sources.extend(direct_data.get("sources", []))
                if direct_data.get("content"):
                    # Return direct data immediately
                    return AgentOutput(
                        agent=self.name,
                        content=direct_data["content"],
                        sources=all_sources
                    )
        
        if self.use_llm and self.llm_client:
            # Build comprehensive prompt with extracted data
            fundamental_context = fundamental_data.get("metrics_summary", "")
            
            # Build sources context for needle-in-haystack
            sources_context = []
            for s in all_sources:
                if s.snippet:
                    # Highlight the "needle" (specific value) in the snippet
                    sources_context.append(f"**{s.title}**: {s.snippet}")
                else:
                    sources_context.append(f"**{s.title}**: Available")
            
            prompt = f"""Analyze the following financial query focusing on fundamental analysis and news:
Query: {query}

Extracted Fundamental Metrics:
{fundamental_context if fundamental_context else "No specific metrics extracted from query."}

Retrieved Sources (Documents/Reports):
{chr(10).join(sources_context) if sources_context else "No sources available"}

For each source, identify the specific value or information requested (needle in haystack):
- What exact metric or value was requested?
- Where is it found in the source?
- Is the value quoted correctly?

Provide:
1. **Specific Metrics Extracted**: List the exact values found (if any)
2. **Key Fundamental Metrics**: Additional metrics relevant to the query
3. **Financial Statement Insights**: Balance sheet, income statement, cash flow insights
4. **Risk Factors**: Risks identified from filings or reports
5. **Source Citations**: Always cite sources when referencing specific numbers"""
            
            try:
                content = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt="""You are a financial analyst specializing in fundamental analysis and news interpretation.
                    
CRITICAL: When referencing specific financial metrics or values, you MUST:
1. Quote the exact value from the source
2. Cite the source explicitly
3. If a value is not found in sources, explicitly state: "No verified source found for this claim"
4. Never invent or estimate values - only use data from retrieved sources""",
                    temperature=0.3,  # Lower temperature for more accurate data extraction
                    max_tokens=700
                )
                
                # Prepend extracted metrics if available
                if fundamental_context:
                    content = f"## Extracted Fundamental Metrics\n{fundamental_context}\n\n## Comprehensive Analysis\n{content}"
            except Exception as e:
                content = fundamental_data.get("metrics_summary", 
                    "Fundamental analysis prepared.")
                if "error" in str(e).lower():
                    content += f"\n(LLM analysis unavailable: {str(e)})"
        else:
            # Use extracted data directly
            content = fundamental_data.get("metrics_summary", "")
            
            # If still no content, try direct data extraction
            if not content or len(content) < 50:
                direct_data = self._get_direct_financial_data(query)
                if direct_data and direct_data.get("content"):
                    content = direct_data["content"]
                    all_sources.extend(direct_data.get("sources", []))
            
            # Final fallback - must have real content
            if not content or len(content) < 50:
                content = "⚠️ Unable to retrieve financial data. Please ensure data sources are configured."
        
        return AgentOutput(agent=self.name, content=content, sources=all_sources)
    
    def _get_direct_financial_data(self, query: str) -> Dict[str, Any]:
        """Get financial data directly from APIs when sources fail."""
        import yfinance as yf
        import re
        
        result = {"content": "", "sources": []}
        query_lower = query.lower()
        
        # Extract ticker
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        tickers = re.findall(ticker_pattern, query)
        
        if not tickers:
            return result
        
        ticker = tickers[0]
        
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract what was asked
            content_parts = []
            
            if "operating income" in query_lower:
                # Try to get from financials
                try:
                    financials = stock.financials
                    if financials is not None and not financials.empty:
                        if 'Operating Income' in financials.index:
                            op_income = financials.loc['Operating Income'].iloc[0]
                            op_income_b = op_income / 1e9
                            content_parts.append(f"**Operating Income**: ${op_income_b:.2f}B (from latest financial statement)")
                            result["sources"].append(Source(
                                id=f"yfinance_financials_{ticker}",
                                title=f"{ticker} Financial Statements",
                                url=f"https://finance.yahoo.com/quote/{ticker}/financials",
                                snippet=f"Operating Income: ${op_income_b:.2f}B"
                            ))
                except:
                    pass
                
                # Fallback to info
                if not content_parts:
                    op_income = info.get('operatingCashflow') or info.get('ebitda')
                    if op_income:
                        op_income_b = op_income / 1e9
                        content_parts.append(f"**Operating Income**: ${op_income_b:.2f}B (estimated from operating cash flow)")
            
            if "revenue" in query_lower:
                revenue = info.get('totalRevenue')
                if revenue:
                    revenue_b = revenue / 1e9
                    content_parts.append(f"**Revenue**: ${revenue_b:.2f}B")
            
            if "eps" in query_lower or "earnings per share" in query_lower:
                eps = info.get('trailingEps')
                if eps:
                    content_parts.append(f"**EPS**: ${eps:.2f}")
            
            if content_parts:
                result["content"] = "\n".join(content_parts)
                result["sources"].append(Source(
                    id=f"yfinance_direct_{ticker}",
                    title=f"{ticker} Financial Data (Live)",
                    url=f"https://finance.yahoo.com/quote/{ticker}",
                    snippet=f"Live financial data for {ticker}"
                ))
        
        except Exception as e:
            print(f"Error in direct data extraction: {e}")
        
        return result
    
    def _extract_fundamental_metrics(self, query: str, sources: List[Source]) -> Dict[str, Any]:
        """Extract specific fundamental metrics from query and sources (needle in haystack)."""
        result = {
            "metrics_summary": "",
            "new_sources": [],
            "extracted_values": {}
        }
        
        query_lower = query.lower()
        extracted_metrics = []
        
        # Extract ticker symbols
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        tickers = re.findall(ticker_pattern, query)
        
        # Metrics to look for
        metric_keywords = {
            "revenue": ["revenue", "sales", "total revenue"],
            "operating_income": ["operating income", "operating profit"],
            "net_income": ["net income", "net profit", "earnings"],
            "eps": ["eps", "earnings per share"],
            "gross_margin": ["gross margin"],
            "operating_margin": ["operating margin"],
            "debt_to_equity": ["debt-to-equity", "debt to equity"],
            "free_cash_flow": ["free cash flow", "fcf"],
            "current_ratio": ["current ratio"],
            "pe_ratio": ["pe ratio", "price to earnings", "p/e"]
        }
        
        # 1. Search in retrieved sources (needle in haystack)
        for source in sources:
            if source.snippet:
                for metric_name, keywords in metric_keywords.items():
                    for keyword in keywords:
                        if keyword in query_lower:
                            # Look for this metric in the source snippet
                            pattern = rf"{keyword}[:\s]+(\$?[\d,]+\.?\d*\s*(?:billion|million|%)?)"
                            match = re.search(pattern, source.snippet, re.IGNORECASE)
                            if match:
                                value = match.group(0)
                                extracted_metrics.append(
                                    f"**{keyword.title()}** (from {source.title}): {value}"
                                )
                                result["extracted_values"][metric_name] = {
                                    "value": value,
                                    "source": source.title,
                                    "citation": source.id
                                }
                                break
        
        # 2. Get live data from yfinance if ticker found
        for ticker in tickers[:2]:  # Limit to 2 tickers
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                ticker_metrics = []
                
                for metric_name, keywords in metric_keywords.items():
                    for keyword in keywords:
                        if keyword in query_lower:
                            # Get metric from yfinance
                            metric_value = None
                            
                            if metric_name == "revenue":
                                metric_value = info.get('totalRevenue')
                                if metric_value:
                                    metric_value = f"${metric_value/1e9:.2f}B"
                            elif metric_name == "operating_income":
                                metric_value = info.get('operatingCashflow') or info.get('ebitda')
                                if metric_value:
                                    metric_value = f"${metric_value/1e9:.2f}B"
                            elif metric_name == "net_income":
                                metric_value = info.get('netIncomeToCommon')
                                if metric_value:
                                    metric_value = f"${metric_value/1e9:.2f}B"
                            elif metric_name == "eps":
                                metric_value = info.get('trailingEps')
                                if metric_value:
                                    metric_value = f"${metric_value:.2f}"
                            elif metric_name == "gross_margin":
                                metric_value = info.get('grossMargins')
                                if metric_value:
                                    metric_value = f"{metric_value*100:.2f}%"
                            elif metric_name == "pe_ratio":
                                metric_value = info.get('trailingPE')
                                if metric_value:
                                    metric_value = f"{metric_value:.2f}"
                            elif metric_name == "debt_to_equity":
                                metric_value = info.get('debtToEquity')
                                if metric_value:
                                    metric_value = f"{metric_value:.2f}"
                            
                            if metric_value:
                                ticker_metrics.append(
                                    f"**{keyword.title()}** ({ticker}): {metric_value}"
                                )
                                result["new_sources"].append(Source(
                                    id=f"yfinance_{metric_name}_{ticker}",
                                    title=f"{ticker} {keyword.title()} (Live Data)",
                                    url=f"https://finance.yahoo.com/quote/{ticker}",
                                    snippet=f"{ticker} {keyword}: {metric_value}"
                                ))
                                break
                
                if ticker_metrics:
                    extracted_metrics.extend(ticker_metrics)
            
            except Exception as e:
                pass
        
        if extracted_metrics:
            result["metrics_summary"] = "\n".join([f"- {m}" for m in extracted_metrics])
        else:
            result["metrics_summary"] = "No specific fundamental metrics extracted. Analyzing available sources..."
        
        return result
