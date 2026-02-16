# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a trading agent system that analyzes cryptocurrency market data (BTC/ETH) using LangChain, LangGraph and Claude AI. It collects real-time market data from Binance API using parallel execution and provides AI-powered trading analysis and recommendations.

**Architecture**: LangGraph-based parallel workflow
- 4 data collection nodes execute in parallel
- State management with TypedDict
- Automatic error tracking and handling
- 3-4x faster than sequential execution

**Current Implementation**: 4 core factors
1. **Funding Rate** - Perpetual contract funding rates (market sentiment)
2. **K-line & Volume** - 24h price trends and volume analysis (technical analysis)
3. **Liquidation Data** - Large liquidation events (market panic indicator)
4. **News & Sentiment** - Crypto news, social media sentiment, and macro news (fundamental analysis)

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Set your LLM API credentials:
   - `LLM_API_BASE_URL`: API endpoint (e.g., https://api.asxs.top or official Anthropic)
   - `LLM_API_KEY`: Your API key
   - `MODEL_NAME`: Model to use (default: claude-sonnet-4-5-20250929)
   - `TEMPERATURE`: Model temperature (default: 0.3)
3. (Optional) Set Binance API credentials for real liquidation data:
   - `BINANCE_API_KEY`: Your Binance API key
   - `BINANCE_API_SECRET`: Your Binance API secret
   - If not configured, liquidation data will not be available
4. (Optional) Set news/sentiment API credentials for real news data:
   - `CRYPTOCOMPARE_API_KEY`: CryptoCompare API key (for crypto news and social data)
   - `NEWSAPI_KEY`: NewsAPI key (for macro financial news)
   - If not configured, news and sentiment data will not be available

### Running
```bash
# Analyze BTC (default)
python src/main.py

# Analyze ETH
python src/main.py --symbol ETHUSDT

# Verbose output with raw data
python src/main.py --verbose
```

## Architecture

### Core Components

**Data Collection** (`src/data_collectors/`)
- `base.py`: Abstract base collector with retry logic and error handling
- `funding_rate.py`: Collects perpetual contract funding rates from Binance
- `kline_volume.py`: Collects 24h K-line data and volume analysis
- `liquidation.py`: Collects liquidation data (returns empty data if API credentials unavailable)
- `news_sentiment.py`: Collects crypto news, social sentiment, and macro news (returns empty data if API keys unavailable)

**Workflow** (`src/workflow/`)
- `trading_graph.py`: LangGraph workflow definition with parallel data collection nodes

**Analysis** (`src/analyzers/`)
- `factor_analyzer.py`: Data formatting for LLM input

**AI Agent** (`src/agent/`)
- `trading_agent.py`: LangChain ChatAnthropic integration with custom API URL support and environment variable conflict handling
- `prompts.py`: System and analysis prompts for Claude

**Utilities** (`src/utils/`)
- `logger.py`: Loguru configuration for console and file logging
- `formatters.py`: Output formatting and data presentation

**Configuration**
- `config/settings.py`: Centralized settings management, loads from `.env`

## Key Implementation Details

### Third-Party API Support
The system supports both official Anthropic API and third-party providers:
- Uses LangChain's ChatAnthropic with `base_url` parameter for custom API endpoints
- Automatically clears conflicting environment variables (ANTHROPIC_API_KEY, CCH_API_KEY) during initialization and API calls
- This prevents authentication errors when using third-party API providers
- Automatically uses custom base_url when `LLM_API_BASE_URL` is configured
- Falls back to official API if no custom URL is provided

### Windows Compatibility
- UTF-8 encoding is explicitly set for stdout on Windows to handle Unicode characters
- This prevents encoding errors when displaying Claude's responses with special characters

### Data Collection
- Binance API calls don't require credentials for public data (funding rates, K-lines)
- Liquidation data requires API Secret; system returns empty data with warning if unavailable
- News and sentiment data require API keys; system returns empty data with warning if unavailable
- All collectors implement retry logic with configurable delays
- All data collectors include `data_available` field to indicate whether real data was obtained
- **Parallel Execution**: 4 data collection nodes run simultaneously using LangGraph, reducing total collection time by 3-4x

### LLM Integration
- Uses LangChain's ChatAnthropic for model interaction
- Formats prompts using SystemMessage and HumanMessage from langchain_core
- Handles both official Anthropic and third-party API providers transparently
- Automatically clears conflicting environment variables during initialization and API calls to prevent authentication errors
- Environment variables are temporarily removed and restored to avoid conflicts with Claude Code's CCH_API_KEY

## Common Tasks

### Add a New Data Collector
1. Create new file in `src/data_collectors/`
2. Inherit from `BaseCollector` in `base.py`
3. Implement `collect()` method returning dict with data
4. Add to `FactorAnalyzer.analyze_all_factors()` in `src/analyzers/factor_analyzer.py`
5. Update `format_for_llm()` to include new data in formatted output

### Modify Analysis Prompt
Edit `src/agent/prompts.py`:
- `SYSTEM_PROMPT`: System role definition
- `ANALYSIS_PROMPT_TEMPLATE`: Analysis template with market data placeholders

### Change Default Settings
Edit `config/settings.py`:
- `FUNDING_RATE_EXTREME_THRESHOLD`: Funding rate alert threshold (default ±0.1%)
- `LIQUIDATION_THRESHOLD`: Large liquidation amount threshold (default 100,000 USDT)
- `KLINE_INTERVAL`: K-line period (default 1h)
- `KLINE_LIMIT`: Historical data points (default 24)

## Testing

Run test scripts in `tests/` directory:
```bash
python tests/test_simple.py      # Basic system tests
python tests/test_llm_config.py  # LLM configuration verification
python tests/demo.py             # Data collection demonstration
```

## Logging

Logs are saved to `logs/trade_agent.log` with configurable level via `LOG_LEVEL` environment variable.

## Important Notes

- The system uses public Binance API data (no trading credentials needed)
- Liquidation data returns empty values when API Secret is unavailable (logged as warning)
- News and sentiment data returns empty values when API keys are unavailable (logged as warning)
- No mock/simulated data is used - if real data cannot be obtained, empty data is returned
- All analysis is for educational purposes only - not investment advice
- Claude responses may contain Unicode characters; ensure UTF-8 terminal support
- The system uses LangChain's ChatAnthropic with `base_url` parameter for custom API endpoints
- Conflicting environment variables (ANTHROPIC_API_KEY, CCH_API_KEY) are automatically cleared during initialization and API calls
- This environment variable handling is critical when using third-party API providers to prevent authentication conflicts
- Windows console encoding issues are handled by setting stdout to UTF-8 in `src/main.py`

