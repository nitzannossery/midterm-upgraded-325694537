from typing import Dict, Any, List, Optional
from app.agents.base import Agent
from app.schemas import AgentOutput, Source
from app.llm.google_client import GoogleLLMClient
import yfinance as yf
import re
from datetime import datetime, timedelta
import pandas as pd

class MarketDataAgent(Agent):
    name = "Market Data Agent"
    
    def __init__(self):
        """Initialize agent with Google LLM client."""
        try:
            self.llm_client = GoogleLLMClient()
            self.use_llm = True
        except Exception:
            self.llm_client = None
            self.use_llm = False

    def run(self, query: str, context: Dict[str, Any]) -> AgentOutput:
        """Process market data query with support for tabular data extraction."""
        sources = context.get("sources", [])
        
        # CRITICAL: Filter out placeholder sources
        real_sources = [s for s in sources if s.id != "src1" and "Example" not in s.title]
        
        # Extract and process market data from query (ALWAYS runs - gets real data)
        market_data_result = self._extract_market_data(query)
        
        # Combine with sources (prioritize real data sources)
        all_sources = (market_data_result.get("sources", [])) + list(real_sources)
        
        # If we have real data, use it immediately
        if market_data_result.get("data_summary"):
            # Return data immediately with real sources
            return AgentOutput(
                agent=self.name,
                content=market_data_result["data_summary"],
                sources=all_sources
            )
        
        if self.use_llm and self.llm_client:
            # Build prompt with retrieved data
            data_context = market_data_result.get("data_summary", "")
            
            prompt = f"""Analyze market data for the following query:
Query: {query}

Retrieved Market Data:
{data_context if data_context else "No specific market data retrieved."}

Available sources:
{chr(10).join([f"- {s.title}: {s.snippet or 'No snippet'}" for s in all_sources]) if all_sources else "No sources available"}

Provide:
1. Key market metrics analysis
2. Price data interpretation
3. Trend analysis if applicable
4. Risk indicators"""
            
            try:
                content = self.llm_client.generate(
                    prompt=prompt,
                    system_prompt="You are a market data analyst specializing in financial market analysis. Always cite sources when referencing specific data points.",
                    temperature=0.3,
                    max_tokens=500
                )
                
                # Prepend actual data if available
                if data_context:
                    content = f"## Market Data Retrieved\n{data_context}\n\n## Analysis\n{content}"
            except Exception as e:
                content = market_data_result.get("data_summary", "Market data analysis prepared.")
                if "error" in str(e).lower():
                    content += f"\n(LLM analysis unavailable: {str(e)})"
        else:
            # Use retrieved data directly
            content = market_data_result.get("data_summary", 
                "Market snapshot prepared. (Google API not configured - using placeholder.)")
            if market_data_result.get("data_summary"):
                content = market_data_result["data_summary"]
        
        return AgentOutput(agent=self.name, content=content, sources=all_sources)
    
    def _extract_market_data(self, query: str) -> Dict[str, Any]:
        """Extract market data from query (tabular data extraction)."""
        result = {
            "data_summary": "",
            "sources": [],
            "tabular_data": None
        }
        
        # Extract ticker symbols
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        tickers = re.findall(ticker_pattern, query)
        
        if not tickers:
            return result
        
        query_lower = query.lower()
        data_parts = []
        
        for ticker in tickers[:3]:  # Limit to 3 tickers
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                ticker_data = []
                
                # Price data
                if any(word in query_lower for word in ["price", "current", "close", "closing"]):
                    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                    if current_price:
                        ticker_data.append(f"**Current Price**: ${current_price:.2f}")
                        
                        # Add to sources
                        result["sources"].append(Source(
                            id=f"yfinance_price_{ticker}",
                            title=f"{ticker} Current Price (Live Data)",
                            url=f"https://finance.yahoo.com/quote/{ticker}",
                            snippet=f"{ticker} current price: ${current_price:.2f}"
                        ))
                
                # Historical data
                if any(word in query_lower for word in ["history", "historical", "past", "last", "days", "months"]):
                    # Determine period
                    period = "1mo"
                    if "year" in query_lower or "12 months" in query_lower:
                        period = "1y"
                    elif "6 months" in query_lower:
                        period = "6mo"
                    elif "3 months" in query_lower or "quarter" in query_lower:
                        period = "3mo"
                    elif "week" in query_lower:
                        period = "1wk"
                    
                    hist = stock.history(period=period)
                    if not hist.empty:
                        latest_close = hist['Close'].iloc[-1]
                        first_close = hist['Close'].iloc[0]
                        return_pct = ((latest_close - first_close) / first_close) * 100
                        volatility = hist['Close'].pct_change().std() * (252 ** 0.5) * 100  # Annualized
                        
                        ticker_data.append(f"\n**Historical Data ({period})**:")
                        ticker_data.append(f"  - Latest Close: ${latest_close:.2f}")
                        ticker_data.append(f"  - Period Return: {return_pct:+.2f}%")
                        ticker_data.append(f"  - Volatility: {volatility:.2f}%")
                        
                        # Create tabular summary
                        summary_stats = hist[['Open', 'High', 'Low', 'Close', 'Volume']].tail(5)
                        result["tabular_data"] = summary_stats.to_dict('records') if len(summary_stats) > 0 else None
                        
                        result["sources"].append(Source(
                            id=f"yfinance_hist_{ticker}",
                            title=f"{ticker} Historical Data ({period})",
                            url=f"https://finance.yahoo.com/quote/{ticker}/history",
                            snippet=f"{ticker} historical data: Latest close ${latest_close:.2f}, Return {return_pct:+.2f}%"
                        ))
                
                # Market cap
                if "market cap" in query_lower or "marketcap" in query_lower:
                    market_cap = info.get('marketCap')
                    if market_cap:
                        market_cap_b = market_cap / 1e9
                        ticker_data.append(f"**Market Cap**: ${market_cap_b:.2f}B")
                
                # Volume
                if "volume" in query_lower:
                    volume = info.get('volume') or info.get('averageVolume')
                    if volume:
                        volume_m = volume / 1e6
                        ticker_data.append(f"**Average Volume**: {volume_m:.2f}M shares")
                
                # P/E Ratio
                if "pe" in query_lower or "price to earnings" in query_lower:
                    pe_ratio = info.get('trailingPE')
                    if pe_ratio:
                        ticker_data.append(f"**P/E Ratio**: {pe_ratio:.2f}")
                
                if ticker_data:
                    data_parts.append(f"\n### {ticker} Market Data")
                    data_parts.extend(ticker_data)
                
            except Exception as e:
                data_parts.append(f"\n### {ticker} - Error retrieving data: {str(e)}")
        
        if data_parts:
            result["data_summary"] = "\n".join(data_parts)
        
        return result
