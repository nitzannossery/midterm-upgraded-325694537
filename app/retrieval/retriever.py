from typing import List, Optional
from app.schemas import Source
import re
import yfinance as yf
from datetime import datetime, timedelta
import json
from app.retrieval.data_sources import DataSourceManager

class Retriever:
    """
    Enhanced Retriever with support for:
    - Needle in haystack queries (finding specific information in documents)
    - Tabular data extraction (from yfinance and financial APIs)
    - Document retrieval and source citation
    """
    
    def __init__(self):
        """Initialize the retriever with document corpus and data sources."""
        # In-memory document corpus (can be replaced with vector DB)
        self.documents = []
        self._initialize_sample_corpus()
        # Initialize data source manager for multiple data sources
        self.data_source_manager = DataSourceManager()
    
    def _initialize_sample_corpus(self):
        """Initialize sample financial documents corpus."""
        # Sample earnings reports, financial filings, etc.
        self.documents = [
            {
                "id": "aapl_earnings_q4_2023",
                "title": "Apple Inc. Q4 2023 Earnings Report",
                "type": "earnings_report",
                "content": """
                Apple Inc. reported Q4 2023 earnings:
                - Revenue: $89.5 billion
                - Operating Income: $24.1 billion
                - Net Income: $22.96 billion
                - EPS: $1.46 per share
                - Gross Margin: 45.2%
                """,
                "ticker": "AAPL",
                "date": "2023-11-02"
            },
            {
                "id": "msft_10k_2023",
                "title": "Microsoft Corporation 10-K Annual Report 2023",
                "type": "annual_filing",
                "content": """
                Microsoft Corporation Annual Report FY2023:
                - Revenue: $211.9 billion
                - Operating Income: $88.5 billion
                - Net Income: $72.4 billion
                - EPS: $9.68 per share
                - Operating Margin: 41.8%
                - Free Cash Flow: $65.4 billion
                """,
                "ticker": "MSFT",
                "date": "2023-06-30"
            },
            {
                "id": "googl_quarterly_q3_2023",
                "title": "Alphabet Inc. Q3 2023 Quarterly Earnings",
                "type": "quarterly_filing",
                "content": """
                Alphabet Inc. Q3 2023 Results:
                - Revenue: $76.7 billion
                - Operating Income: $21.3 billion
                - Net Income: $19.69 billion
                - EPS: $1.55 per share
                - Operating Margin: 27.8%
                """,
                "ticker": "GOOGL",
                "date": "2023-09-30"
            }
        ]
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Source]:
        """
        Retrieve relevant sources for a query.
        Supports both document retrieval and tabular data extraction.
        Now uses multiple data sources for up-to-date information.
        """
        sources = []
        
        # Extract ticker symbols from query
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        tickers = re.findall(ticker_pattern, query)
        
        # 1. Multi-source data retrieval (NEW - comprehensive data from multiple sources)
        if tickers:
            for ticker in tickers[:2]:  # Limit to 2 tickers
                multi_source_data = self._get_comprehensive_data(ticker, query)
                sources.extend(multi_source_data)
        
        # 2. Document-based retrieval (needle in haystack)
        doc_sources = self._retrieve_from_documents(query, top_k)
        # Filter out placeholder sources
        real_doc_sources = [s for s in doc_sources if s.id != "src1" and "Example" not in s.title]
        sources.extend(real_doc_sources)
        
        # 3. Tabular data retrieval (from yfinance - legacy support)
        ticker_data = self._extract_ticker_data(query)
        if ticker_data:
            sources.append(ticker_data)
        
        # 4. Financial metric extraction (specific values from documents)
        metric_sources = self._extract_financial_metrics(query)
        sources.extend(metric_sources)
        
        # Remove duplicates and return top_k most relevant
        unique_sources = self._deduplicate_sources(sources)
        return unique_sources[:top_k]
    
    def _get_comprehensive_data(self, ticker: str, query: str) -> List[Source]:
        """Get comprehensive data from multiple sources."""
        sources = []
        query_lower = query.lower()
        
        try:
            # Get comprehensive stock info from multiple sources
            stock_data = self.data_source_manager.get_stock_info(ticker)
            
            # Create sources from the data
            data_items = []
            
            # Price and market data
            if stock_data.get("data", {}).get("current_price"):
                price = stock_data["data"]["current_price"]
                data_items.append(f"Current Price: ${price:.2f}")
            
            if stock_data.get("data", {}).get("market_cap"):
                market_cap = stock_data["data"]["market_cap"] / 1e9
                data_items.append(f"Market Cap: ${market_cap:.2f}B")
            
            if stock_data.get("data", {}).get("pe_ratio"):
                pe = stock_data["data"]["pe_ratio"]
                data_items.append(f"P/E Ratio: {pe:.2f}")
            
            if stock_data.get("data", {}).get("revenue"):
                revenue = stock_data["data"]["revenue"] / 1e9
                data_items.append(f"Revenue: ${revenue:.2f}B")
            
            if stock_data.get("data", {}).get("operating_margin"):
                margin = stock_data["data"]["operating_margin"] * 100
                data_items.append(f"Operating Margin: {margin:.2f}%")
            
            if stock_data.get("data", {}).get("free_cash_flow"):
                fcf = stock_data["data"]["free_cash_flow"] / 1e9
                data_items.append(f"Free Cash Flow: ${fcf:.2f}B")
            
            # Historical data
            if stock_data.get("data", {}).get("historical"):
                hist = stock_data["data"]["historical"]
                data_items.append(f"Latest Close: ${hist['latest_close']:.2f} ({hist['latest_date']})")
                data_items.append(f"Period Return: {hist['period_return']:+.2f}%")
                data_items.append(f"Volatility: {hist['volatility']:.2f}%")
            
            if data_items:
                sources.append(Source(
                    id=f"multi_source_{ticker}",
                    title=f"{ticker} Comprehensive Data (Multiple Sources)",
                    url=f"https://finance.yahoo.com/quote/{ticker}",
                    snippet=f"{ticker} Data: " + " | ".join(data_items[:5])  # Limit snippet length
                ))
            
            # News sources
            if stock_data.get("data", {}).get("recent_news"):
                news = stock_data["data"]["recent_news"][:3]  # Top 3 news items
                for i, news_item in enumerate(news):
                    sources.append(Source(
                        id=f"news_{ticker}_{i}",
                        title=f"{ticker} News: {news_item.get('title', '')[:50]}",
                        url=news_item.get("link", ""),
                        snippet=news_item.get("summary", "")[:150] if news_item.get("summary") else ""
                    ))
            
            # Financial statements
            financials = self.data_source_manager.get_financials(ticker)
            if financials:
                financial_items = []
                
                if financials.get("income_statement", {}).get("operating_income"):
                    op_income = financials["income_statement"]["operating_income"] / 1e9
                    financial_items.append(f"Operating Income: ${op_income:.2f}B")
                
                if financials.get("income_statement", {}).get("net_income"):
                    net_income = financials["income_statement"]["net_income"] / 1e9
                    financial_items.append(f"Net Income: ${net_income:.2f}B")
                
                if financials.get("cash_flow", {}).get("free_cash_flow"):
                    fcf = financials["cash_flow"]["free_cash_flow"] / 1e9
                    financial_items.append(f"Free Cash Flow: ${fcf:.2f}B")
                
                if financial_items:
                    sources.append(Source(
                        id=f"financials_{ticker}",
                        title=f"{ticker} Financial Statements (Latest)",
                        url=f"https://finance.yahoo.com/quote/{ticker}/financials",
                        snippet=" | ".join(financial_items)
                    ))
        
        except Exception as e:
            print(f"Error getting comprehensive data for {ticker}: {e}")
        
        return sources
    
    def _deduplicate_sources(self, sources: List[Source]) -> List[Source]:
        """Remove duplicate sources based on ID."""
        seen_ids = set()
        unique_sources = []
        
        for source in sources:
            if source.id not in seen_ids:
                seen_ids.add(source.id)
                unique_sources.append(source)
        
        return unique_sources
    
    def _retrieve_from_documents(self, query: str, top_k: int) -> List[Source]:
        """Retrieve documents matching the query (simple keyword matching for now)."""
        query_lower = query.lower()
        matched_docs = []
        
        for doc in self.documents:
            score = 0
            # Simple keyword matching (can be replaced with embeddings/vector search)
            content_lower = doc["content"].lower()
            title_lower = doc["title"].lower()
            
            # Check for ticker mentions
            ticker = doc.get("ticker", "").lower()
            if ticker and ticker in query_lower:
                score += 10
            
            # Check for query terms in title
            query_terms = query_lower.split()
            for term in query_terms:
                if term in title_lower:
                    score += 5
                if term in content_lower:
                    score += 2
            
            # Check for financial terms
            financial_terms = ["revenue", "income", "earnings", "eps", "margin", 
                             "report", "filing", "quarterly", "annual"]
            for term in financial_terms:
                if term in query_lower and term in content_lower:
                    score += 3
            
            if score > 0:
                # Extract relevant snippet (needle in haystack)
                snippet = self._extract_relevant_snippet(query, doc["content"])
                matched_docs.append({
                    "doc": doc,
                    "score": score,
                    "snippet": snippet
                })
        
        # Sort by score and return top_k
        matched_docs.sort(key=lambda x: x["score"], reverse=True)
        
        sources = []
        for match in matched_docs[:top_k]:
            doc = match["doc"]
            sources.append(Source(
                id=doc["id"],
                title=doc["title"],
                url=None,  # Can be added if documents have URLs
                snippet=match["snippet"]
            ))
        
        return sources
    
    def _extract_relevant_snippet(self, query: str, content: str, max_length: int = 200) -> str:
        """Extract the most relevant snippet from content for the query (needle in haystack)."""
        query_lower = query.lower()
        query_terms = [t for t in query_lower.split() if len(t) > 3]
        
        # Split content into sentences
        sentences = re.split(r'[.!?]\s+', content)
        
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            score = 0
            sentence_lower = sentence.lower()
            for term in query_terms:
                if term in sentence_lower:
                    score += 1
            
            # Prioritize sentences with numbers (likely contain financial data)
            if re.search(r'\d+[\d,.]*\s*(billion|million|%|per share)', sentence_lower):
                score += 5
            
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
        
        if best_sentence:
            # Truncate if too long
            if len(best_sentence) > max_length:
                best_sentence = best_sentence[:max_length] + "..."
            return best_sentence
        
        # Fallback: return first part of content
        return content[:max_length] + "..." if len(content) > max_length else content
    
    def _extract_ticker_data(self, query: str) -> Optional[Source]:
        """Extract stock ticker from query and retrieve live data."""
        # Extract ticker symbols (1-5 uppercase letters)
        ticker_pattern = r'\b([A-Z]{1,5})\b'
        matches = re.findall(ticker_pattern, query)
        
        if not matches:
            return None
        
        # Use first ticker found
        ticker = matches[0]
        
        try:
            # Get stock info
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract relevant data based on query
            data_points = []
            
            query_lower = query.lower()
            
            if "price" in query_lower or "current" in query_lower:
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                if current_price:
                    data_points.append(f"Current Price: ${current_price:.2f}")
            
            if "market cap" in query_lower or "marketcap" in query_lower:
                market_cap = info.get('marketCap')
                if market_cap:
                    market_cap_b = market_cap / 1e9
                    data_points.append(f"Market Cap: ${market_cap_b:.2f}B")
            
            if "revenue" in query_lower:
                revenue = info.get('totalRevenue')
                if revenue:
                    revenue_b = revenue / 1e9
                    data_points.append(f"Revenue: ${revenue_b:.2f}B")
            
            if "pe" in query_lower or "price to earnings" in query_lower:
                pe_ratio = info.get('trailingPE')
                if pe_ratio:
                    data_points.append(f"P/E Ratio: {pe_ratio:.2f}")
            
            # Historical data if date range mentioned
            if any(word in query_lower for word in ["history", "historical", "last", "past"]):
                hist = stock.history(period="1mo")
                if not hist.empty:
                    latest_close = hist['Close'].iloc[-1]
                    data_points.append(f"Latest Close: ${latest_close:.2f}")
            
            if data_points:
                snippet = f"{ticker} Stock Data: " + " | ".join(data_points)
                return Source(
                    id=f"yfinance_{ticker}",
                    title=f"{ticker} Stock Information (Live Data)",
                    url=f"https://finance.yahoo.com/quote/{ticker}",
                    snippet=snippet
                )
        except Exception as e:
            # If yfinance fails, return None
            pass
        
        return None
    
    def _extract_financial_metrics(self, query: str) -> List[Source]:
        """Extract specific financial metrics from query (e.g., 'What was X's revenue?')."""
        sources = []
        query_lower = query.lower()
        
        # Pattern matching for metric extraction
        metric_patterns = {
            "revenue": r"(revenue|sales)",
            "income": r"(operating income|net income|profit)",
            "eps": r"(eps|earnings per share)",
            "margin": r"(gross margin|operating margin|profit margin)",
            "debt": r"(debt|debt-to-equity)",
            "cash flow": r"(free cash flow|cash flow)"
        }
        
        for metric_name, pattern in metric_patterns.items():
            if re.search(pattern, query_lower):
                # Find documents containing this metric
                for doc in self.documents:
                    if re.search(pattern, doc["content"].lower(), re.IGNORECASE):
                        # Extract the specific value
                        metric_value = self._extract_metric_value(metric_name, doc["content"])
                        if metric_value:
                            sources.append(Source(
                                id=f"{doc['id']}_{metric_name}",
                                title=f"{doc['title']} - {metric_name.title()}",
                                url=None,
                                snippet=f"According to {doc['title']}: {metric_value}"
                            ))
                            break  # Only take first match
        
        return sources
    
    def _extract_metric_value(self, metric_name: str, content: str) -> Optional[str]:
        """Extract specific metric value from content."""
        # Look for patterns like "Revenue: $89.5 billion"
        metric_keywords = {
            "revenue": ["revenue", "sales"],
            "income": ["operating income", "net income"],
            "eps": ["eps", "earnings per share"],
            "margin": ["gross margin", "operating margin"],
            "debt": ["debt-to-equity", "total debt"],
            "cash flow": ["free cash flow"]
        }
        
        keywords = metric_keywords.get(metric_name, [metric_name])
        
        for keyword in keywords:
            # Pattern: "Keyword: $XX.X billion" or "Keyword $XX.X billion"
            pattern = rf"{keyword}[:\s]+(\$?[\d,]+\.?\d*\s*(?:billion|million|%)?)"
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def add_document(self, doc_id: str, title: str, content: str, 
                    doc_type: str = "document", ticker: Optional[str] = None, 
                    date: Optional[str] = None):
        """Add a document to the corpus."""
        self.documents.append({
            "id": doc_id,
            "title": title,
            "type": doc_type,
            "content": content,
            "ticker": ticker,
            "date": date
        })
