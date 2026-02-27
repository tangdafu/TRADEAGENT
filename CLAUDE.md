# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a trading agent system that analyzes cryptocurrency market data (BTC/ETH) using LangChain, LangGraph and Claude AI. It collects real-time market data from Binance API using parallel execution and provides AI-powered trading analysis and recommendations.

**Architecture**: LangGraph-based parallel workflow
- 4 data collection nodes execute in parallel
- Market signal detection for smart AI analysis triggering
- State management with TypedDict
- Automatic error tracking and handling
- 3-4x faster than sequential execution

**Current Implementation**: 4 core factors + Market Signal Detection
1. **Funding Rate** - Perpetual contract funding rates (market sentiment)
2. **K-line & Volume** - 24h price trends and volume analysis (technical analysis)
3. **Market Pressure** - Open interest, long/short ratio, taker buy/sell volume (market pressure indicator)
4. **News & Sentiment** - Crypto news, social media sentiment, and macro news (fundamental analysis)
5. **Market Signal Detection** - Pre-analysis filtering to reduce unnecessary AI calls

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
3. (Optional) Set news/sentiment API credentials for real news data:
   - `CRYPTOCOMPARE_API_KEY`: CryptoCompare API key (for crypto news and social data)
   - `NEWSAPI_KEY`: NewsAPI key (for macro financial news)
   - If not configured, news and sentiment data will not be available
4. (Optional) Configure market signal detection:
   - `MARKET_SIGNAL_DETECTION_ENABLED`: Enable/disable smart filtering (default: true)
   - `MIN_SIGNAL_COUNT`: Minimum signals required to trigger AI analysis (default: 2)
   - `PRICE_CHANGE_THRESHOLD`: Price volatility threshold in % (default: 5.0)
   - `FUNDING_RATE_CHANGE_THRESHOLD`: Funding rate change threshold (default: 0.0005)
   - `VOLUME_SURGE_RATIO`: Volume surge multiplier (default: 2.0)
   - `NEWS_SENTIMENT_THRESHOLD`: News sentiment score threshold (default: 0.5)

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
- `liquidation.py`: Collects market pressure data using public APIs (open interest, long/short ratio, taker volume)
- `news_sentiment.py`: Collects crypto news, social sentiment, and macro news (returns empty data if API keys unavailable)

**Workflow** (`src/workflow/`)
- `trading_graph.py`: LangGraph workflow definition with parallel data collection nodes and market signal detection

**Analysis** (`src/analyzers/`)
- `factor_analyzer.py`: Data formatting for LLM input
- `market_signal_detector.py`: Market signal detection for smart AI analysis triggering

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
- Binance API calls don't require credentials for public data (funding rates, K-lines, market pressure data)
- Market pressure data uses public APIs: open interest, long/short ratio, and taker buy/sell volume
- News and sentiment data require API keys; system returns empty data with warning if unavailable
- All collectors implement retry logic with configurable delays
- All data collectors include `data_available` field to indicate whether real data was obtained
- **Parallel Execution**: 4 data collection nodes run simultaneously using LangGraph, reducing total collection time by 3-4x

**Note**: Binance liquidation data API has been deprecated. The system now uses market pressure indicators (open interest, long/short ratio, taker volume) as a more reliable alternative.

### Market Signal Detection (Smart AI Triggering)
The system includes intelligent market signal detection to reduce unnecessary AI API calls:
- **Configurable**: Can be enabled/disabled via `MARKET_SIGNAL_DETECTION_ENABLED` setting
- **Multi-factor Analysis**: Evaluates 5 types of signals:
  1. **Funding Rate Signals**: Extreme rates or rapid changes indicating market sentiment shifts
  2. **Price Volatility Signals**: Significant price movements (default: ±5% in 24h)
  3. **Volume Anomaly Signals**: Unusual trading volume surges (default: 2x average)
  4. **Market Pressure Signals**: Extreme long/short ratios or buy/sell imbalances indicating overcrowding
  5. **News Sentiment Signals**: Extreme positive/negative news sentiment
- **Threshold-based Triggering**: AI analysis only runs when minimum signal count is reached (default: 2 signals)
- **Cost Optimization**: Skips AI analysis during low-volatility periods, saving API costs
- **Detailed Logging**: All signal detections are logged with strength indicators (strong/medium)

**Signal Detection Workflow**:
```
Data Collection (Parallel) → Market Signal Detection → Format Data → AI Analysis (Conditional)
                                        ↓
                              If signals < threshold: Skip AI, return "No opportunity"
                              If signals ≥ threshold: Proceed to AI analysis
```

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
- `KLINE_INTERVAL`: K-line period (default 1h)
- `KLINE_LIMIT`: Historical data points (default 24)

### Configure Market Signal Detection
Edit `.env` file to customize signal detection behavior:
- `MARKET_SIGNAL_DETECTION_ENABLED=true`: Enable/disable smart filtering
- `MIN_SIGNAL_COUNT=2`: Minimum signals to trigger AI analysis
- `PRICE_CHANGE_THRESHOLD=5.0`: Price change % threshold
- `FUNDING_RATE_CHANGE_THRESHOLD=0.0005`: Funding rate change threshold
- `VOLUME_SURGE_RATIO=2.0`: Volume surge multiplier
- `NEWS_SENTIMENT_THRESHOLD=0.5`: News sentiment score threshold

**Example**: To make the system more sensitive (trigger AI more often):
```bash
MIN_SIGNAL_COUNT=1              # Trigger with just 1 signal
PRICE_CHANGE_THRESHOLD=3.0      # Lower price threshold (3% instead of 5%)
VOLUME_SURGE_RATIO=1.5          # Lower volume threshold
```

**Example**: To make the system more conservative (reduce AI calls):
```bash
MIN_SIGNAL_COUNT=3              # Require 3 signals
PRICE_CHANGE_THRESHOLD=8.0      # Higher price threshold
VOLUME_SURGE_RATIO=3.0          # Higher volume threshold
```

## Testing

Run test scripts in `tests/` directory:
```bash
python tests/test_simple.py           # Basic system tests
python tests/test_llm_config.py       # LLM configuration verification
python tests/test_market_pressure.py  # Market pressure data collection test
python tests/demo.py                  # Data collection demonstration
```

## Logging

Logs are saved to `logs/trade_agent.log` with configurable level via `LOG_LEVEL` environment variable.

## Important Notes

- The system uses public Binance API data (no API credentials needed for core functionality)
- Market pressure data (open interest, long/short ratio, taker volume) is collected via public APIs
- News and sentiment data returns empty values when API keys are unavailable (logged as warning)
- No mock/simulated data is used - if real data cannot be obtained, empty data is returned
- All analysis is for educational purposes only - not investment advice
- Claude responses may contain Unicode characters; ensure UTF-8 terminal support
- The system uses LangChain's ChatAnthropic with `base_url` parameter for custom API endpoints
- Conflicting environment variables (ANTHROPIC_API_KEY, CCH_API_KEY) are automatically cleared during initialization and API calls
- This environment variable handling is critical when using third-party API providers to prevent authentication conflicts
- Windows console encoding issues are handled by setting stdout to UTF-8 in `src/main.py`

**Note on Liquidation Data**: Binance's liquidation data API (`/fapi/v1/allForceOrders`) has been deprecated. The system now uses alternative market pressure indicators that provide more reliable and comprehensive market analysis without requiring API credentials.

