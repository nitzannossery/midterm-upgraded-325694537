"""
Example: How to integrate your agents with the evaluation framework

This file shows example implementations of the _call_agent methods
that you need to add to the evaluation runners.
"""

# Example 1: Market Data Agent Integration
def example_market_data_agent_call(input_data: dict) -> dict:
    """
    Example implementation for calling Market Data Agent.
    
    Replace this with your actual agent implementation.
    """
    # Extract input parameters
    query = input_data.get("query", "")
    symbol = input_data.get("symbol", "")
    date = input_data.get("date", "")
    
    # Call your actual agent
    # from your_project.agents.market_data import MarketDataAgent
    # agent = MarketDataAgent()
    # result = agent.get_price(symbol, date)
    
    # Example response structure (replace with actual agent output)
    return {
        "status": "success",
        "symbol": symbol,
        "date": date,
        "close_price": 150.25,  # Replace with actual price
        "volume": 50000000,
        "data_source": "yahoo_finance"
    }


# Example 2: Fundamental Agent Integration
def example_fundamental_agent_call(input_data: dict) -> dict:
    """
    Example implementation for calling Fundamental & News Agent.
    """
    query = input_data.get("query", "")
    symbol = input_data.get("symbol", "")
    statement_type = input_data.get("statement_type", "")
    period = input_data.get("period", "")
    
    # Call your actual agent
    # from your_project.agents.fundamental import FundamentalAgent
    # agent = FundamentalAgent()
    # result = agent.get_financial_statement(symbol, statement_type, period)
    
    # Example response structure
    return {
        "status": "success",
        "symbol": symbol,
        "statement_type": statement_type,
        "period": period,
        "revenue": 1000000000.0,
        "net_income": 250000000.0,
        "eps": 1.50,
        "data_source": "sec_filings"
    }


# Example 3: Portfolio Agent Integration
def example_portfolio_agent_call(input_data: dict) -> dict:
    """
    Example implementation for calling Portfolio & Risk Agent.
    """
    query = input_data.get("query", "")
    portfolio = input_data.get("portfolio", [])
    metric = input_data.get("metric", "")
    
    # Call your actual agent
    # from your_project.agents.portfolio import PortfolioAgent
    # agent = PortfolioAgent()
    # result = agent.calculate_risk_metric(portfolio, metric)
    
    # Example response structure
    return {
        "status": "success",
        "metric": metric,
        "value": 0.15,  # e.g., volatility
        "portfolio": portfolio,
        "calculation_method": "historical_volatility"
    }


# Example 4: LLM Evaluation - String Response
def example_llm_agent_call(agent_name: str, query: str) -> str:
    """
    Example implementation for LLM evaluations.
    Returns a string response that will be evaluated by LLM-as-judge.
    """
    if agent_name == "market_data":
        # Call market data agent and format as text
        # result = market_data_agent.process_query(query)
        # return result.format_as_text()
        return "The closing price of AAPL on 2024-01-15 was $150.25. Data retrieved from Yahoo Finance."
    
    elif agent_name == "fundamental_news":
        # Call fundamental agent and format as text
        # result = fundamental_agent.process_query(query)
        # return result.format_as_text()
        return "AAPL's P/E ratio is 28.5, which is above the industry average of 25.0. This suggests the stock may be slightly overvalued."
    
    elif agent_name == "portfolio_risk":
        # Call portfolio agent and format as text
        # result = portfolio_agent.process_query(query)
        # return result.format_as_text()
        return "The portfolio volatility is 15.2% (annualized). This is moderate risk. The Sharpe ratio is 1.2, indicating good risk-adjusted returns."
    
    elif agent_name == "summarizer":
        # Call summarizer agent
        # result = summarizer_agent.synthesize(market_data, fundamental, portfolio)
        # return result.format_as_text()
        return "Based on market data, fundamentals, and risk analysis, AAPL appears to be a solid investment with moderate risk and good growth potential."
    
    return "Agent response not available."


# Example 5: How to modify run_hard_evals.py
"""
In run_hard_evals.py, replace the _call_agent method with:

def _call_agent(self, agent_name: str, input_data: Dict) -> Dict:
    from your_project.agents import (
        MarketDataAgent,
        FundamentalAgent,
        PortfolioAgent
    )
    
    if agent_name == "market_data":
        agent = MarketDataAgent()
        return agent.process(input_data)
    
    elif agent_name == "fundamental_news":
        agent = FundamentalAgent()
        return agent.process(input_data)
    
    elif agent_name == "portfolio_risk":
        agent = PortfolioAgent()
        return agent.process(input_data)
    
    else:
        return {"status": "error", "error": f"Unknown agent: {agent_name}"}
"""


# Example 6: How to modify run_llm_evals.py
"""
In run_llm_evals.py, replace the _call_agent method with:

def _call_agent(self, agent_name: str, query: str) -> str:
    from your_project.agents import (
        MarketDataAgent,
        FundamentalAgent,
        PortfolioAgent,
        SummarizerAgent
    )
    
    if agent_name == "market_data":
        agent = MarketDataAgent()
        response = agent.process_query(query)
        return response.format_as_text()
    
    elif agent_name == "fundamental_news":
        agent = FundamentalAgent()
        response = agent.process_query(query)
        return response.format_as_text()
    
    elif agent_name == "portfolio_risk":
        agent = PortfolioAgent()
        response = agent.process_query(query)
        return response.format_as_text()
    
    elif agent_name == "summarizer":
        agent = SummarizerAgent()
        response = agent.synthesize(query)
        return response.format_as_text()
    
    return "Agent not available."
"""


if __name__ == "__main__":
    print("This is an example file showing how to integrate your agents.")
    print("See the comments in this file for implementation guidance.")
    print("\nTo use:")
    print("1. Copy the _call_agent implementations to the respective runner files")
    print("2. Replace example code with your actual agent calls")
    print("3. Ensure agent responses match expected formats in test cases")
