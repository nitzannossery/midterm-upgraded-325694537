"""
Multiple data sources for financial data retrieval.
Supports various APIs and web sources for up-to-date information.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import yfinance as yf
import requests
import feedparser
from bs4 import BeautifulSoup
import json
import re
import time

class DataSourceManager:
    """Manages multiple data sources for financial information."""
    
    def __init__(self):
        """Initialize data source manager."""
        self.sources_enabled = {
            "yfinance": True,
            "yahoo_news": True,
            "web_search": True,
            "alpha_vantage": False,  # Requires API key
        }
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive stock information from multiple sources."""
        data = {
            "ticker": ticker,
            "sources": [],
            "data": {}
        }
        
        # Source 1: Yahoo Finance (yfinance)
        if self.sources_enabled["yfinance"]:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get current data
                current_data = {
                    "current_price": info.get('currentPrice') or info.get('regularMarketPrice'),
                    "market_cap": info.get('marketCap'),
                    "volume": info.get('volume') or info.get('averageVolume'),
                    "pe_ratio": info.get('trailingPE'),
                    "dividend_yield": info.get('dividendYield'),
                    "52_week_high": info.get('fiftyTwoWeekHigh'),
                    "52_week_low": info.get('fiftyTwoWeekLow'),
                    "beta": info.get('beta'),
                    "revenue": info.get('totalRevenue'),
                    "net_income": info.get('netIncomeToCommon'),
                    "eps": info.get('trailingEps'),
                    "book_value": info.get('bookValue'),
                    "price_to_book": info.get('priceToBook'),
                    "gross_margin": info.get('grossMargins'),
                    "operating_margin": info.get('operatingMargins'),
                    "profit_margin": info.get('profitMargins'),
                    "debt_to_equity": info.get('debtToEquity'),
                    "current_ratio": info.get('currentRatio'),
                    "quick_ratio": info.get('quickRatio'),
                    "free_cash_flow": info.get('freeCashflow'),
                    "operating_cash_flow": info.get('operatingCashflow'),
                }
                
                # Remove None values
                current_data = {k: v for k, v in current_data.items() if v is not None}
                
                if current_data:
                    data["data"].update(current_data)
                    data["sources"].append({
                        "name": "Yahoo Finance",
                        "type": "api",
                        "url": f"https://finance.yahoo.com/quote/{ticker}",
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error fetching from yfinance: {e}")
        
        # Source 2: Yahoo Finance News
        if self.sources_enabled["yahoo_news"]:
            try:
                news = self._get_yahoo_news(ticker)
                if news:
                    data["data"]["recent_news"] = news
                    data["sources"].append({
                        "name": "Yahoo Finance News",
                        "type": "news",
                        "url": f"https://finance.yahoo.com/quote/{ticker}/news",
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error fetching Yahoo news: {e}")
        
        # Source 3: Historical data from yfinance
        try:
            hist = yf.Ticker(ticker).history(period="1mo")
            if not hist.empty:
                data["data"]["historical"] = {
                    "latest_close": float(hist['Close'].iloc[-1]),
                    "latest_date": hist.index[-1].strftime("%Y-%m-%d"),
                    "period_return": float(((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100),
                    "volatility": float(hist['Close'].pct_change().std() * (252 ** 0.5) * 100),
                    "avg_volume": float(hist['Volume'].mean()),
                }
        except Exception as e:
            print(f"Error fetching historical data: {e}")
        
        return data
    
    def _get_yahoo_news(self, ticker: str, max_news: int = 5) -> List[Dict[str, Any]]:
        """Get recent news for a ticker from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return []
            
            news_list = []
            for item in news[:max_news]:
                news_list.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "link": item.get("link", ""),
                    "published": item.get("providerPublishTime", 0),
                    "summary": item.get("summary", "")[:200] if item.get("summary") else ""
                })
            
            return news_list
        except Exception as e:
            print(f"Error fetching Yahoo news: {e}")
            return []
    
    def search_financial_web(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Search financial information on the web."""
        results = []
        
        # Try Yahoo Finance search
        try:
            search_url = f"https://finance.yahoo.com/quote/{query}"
            # This is a placeholder - in production, use proper web scraping or API
            results.append({
                "title": f"Yahoo Finance: {query}",
                "url": search_url,
                "snippet": f"Financial information for {query}",
                "source": "Yahoo Finance"
            })
        except Exception as e:
            print(f"Error in web search: {e}")
        
        return results
    
    def get_earnings_calendar(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get earnings calendar information."""
        try:
            stock = yf.Ticker(ticker)
            calendar = stock.calendar
            
            if calendar is not None and not calendar.empty:
                return {
                    "earnings_date": calendar.index[0].strftime("%Y-%m-%d") if len(calendar) > 0 else None,
                    "earnings_estimate": float(calendar.iloc[0]['Earnings Estimate']) if 'Earnings Estimate' in calendar.columns else None,
                    "revenue_estimate": float(calendar.iloc[0]['Revenue Estimate']) if 'Revenue Estimate' in calendar.columns else None,
                }
        except Exception as e:
            print(f"Error fetching earnings calendar: {e}")
        
        return None
    
    def get_recommendations(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get analyst recommendations."""
        try:
            stock = yf.Ticker(ticker)
            recommendations = stock.recommendations
            
            if recommendations is not None and not recommendations.empty:
                latest = recommendations.iloc[-1]
                return {
                    "latest_recommendation": latest.name.strftime("%Y-%m-%d") if hasattr(latest.name, 'strftime') else str(latest.name),
                    "firm": latest.get('Firm', 'Unknown') if isinstance(latest, dict) else 'Unknown',
                    "rating": latest.get('To Grade', 'Unknown') if isinstance(latest, dict) else 'Unknown',
                }
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
        
        return None
    
    def get_institutional_holders(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get institutional holders information."""
        try:
            stock = yf.Ticker(ticker)
            holders = stock.institutional_holders
            
            if holders is not None and not holders.empty:
                return holders.to_dict('records')[:10]  # Top 10
        except Exception as e:
            print(f"Error fetching institutional holders: {e}")
        
        return None
    
    def get_major_holders(self, ticker: str) -> Optional[List[Dict[str, Any]]]:
        """Get major holders information."""
        try:
            stock = yf.Ticker(ticker)
            holders = stock.major_holders
            
            if holders is not None:
                return [{"holder": h[1], "percentage": h[0]} for h in holders[:5]]
        except Exception as e:
            print(f"Error fetching major holders: {e}")
        
        return None
    
    def get_financials(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive financial statements."""
        financials = {}
        
        try:
            stock = yf.Ticker(ticker)
            
            # Income statement
            try:
                income_stmt = stock.financials
                if income_stmt is not None and not income_stmt.empty:
                    financials["income_statement"] = {
                        "total_revenue": float(income_stmt.loc['Total Revenue'].iloc[0]) if 'Total Revenue' in income_stmt.index else None,
                        "operating_income": float(income_stmt.loc['Operating Income'].iloc[0]) if 'Operating Income' in income_stmt.index else None,
                        "net_income": float(income_stmt.loc['Net Income'].iloc[0]) if 'Net Income' in income_stmt.index else None,
                        "date": income_stmt.columns[0].strftime("%Y-%m-%d") if len(income_stmt.columns) > 0 else None,
                    }
            except Exception as e:
                print(f"Error fetching income statement: {e}")
            
            # Balance sheet
            try:
                balance_sheet = stock.balance_sheet
                if balance_sheet is not None and not balance_sheet.empty:
                    financials["balance_sheet"] = {
                        "total_assets": float(balance_sheet.loc['Total Assets'].iloc[0]) if 'Total Assets' in balance_sheet.index else None,
                        "total_liabilities": float(balance_sheet.loc['Total Liab'].iloc[0]) if 'Total Liab' in balance_sheet.index else None,
                        "total_equity": float(balance_sheet.loc['Stockholders Equity'].iloc[0]) if 'Stockholders Equity' in balance_sheet.index else None,
                        "date": balance_sheet.columns[0].strftime("%Y-%m-%d") if len(balance_sheet.columns) > 0 else None,
                    }
            except Exception as e:
                print(f"Error fetching balance sheet: {e}")
            
            # Cash flow
            try:
                cashflow = stock.cashflow
                if cashflow is not None and not cashflow.empty:
                    financials["cash_flow"] = {
                        "operating_cash_flow": float(cashflow.loc['Operating Cash Flow'].iloc[0]) if 'Operating Cash Flow' in cashflow.index else None,
                        "free_cash_flow": float(cashflow.loc['Free Cash Flow'].iloc[0]) if 'Free Cash Flow' in cashflow.index else None,
                        "date": cashflow.columns[0].strftime("%Y-%m-%d") if len(cashflow.columns) > 0 else None,
                    }
            except Exception as e:
                print(f"Error fetching cash flow: {e}")
        
        except Exception as e:
            print(f"Error fetching financials: {e}")
        
        return financials
