# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a trading agent system that analyzes cryptocurrency market data (BTC/ETH) using LangChain and Claude AI. It collects real-time market data from Binance API and provides AI-powered trading analysis and recommendations.

**MVP Implementation**: 3 core factors
1. **Funding Rate** - Perpetual contract funding rates (market sentiment)
2. **K-line & Volume** - 24h price trends and volume analysis (technical analysis)
3. **Liquidation Data** - Large liquidation events (market panic indicator)

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
- `liquidation.py`: Collects liquidation data (uses mock data if API Secret unavailable)

**Analysis** (`src/analyzers/`)
- `factor_analyzer.py`: Integrates all data collectors and formats data for LLM

**AI Agent** (`src/agent/`)
- `trading_agent.py`: LangChain ChatAnthropic integration with custom API URL support
- `prompts.py`: System and analysis prompts for Claude

**Utilities** (`src/utils/`)
- `logger.py`: Loguru configuration for console and file logging
- `formatters.py`: Output formatting and data presentation

**Configuration**
- `config/settings.py`: Centralized settings management, loads from `.env`

## Key Implementation Details

### Third-Party API Support
The system supports both official Anthropic API and third-party providers:
- Uses `base_url` parameter in ChatAnthropic for custom API endpoints
- Automatically uses custom base_url when `LLM_API_BASE_URL` is configured
- Falls back to official API if no custom URL is provided

### Windows Compatibility
- UTF-8 encoding is explicitly set for stdout on Windows to handle Unicode characters
- This prevents encoding errors when displaying Claude's responses with special characters

### Data Collection
- Binance API calls don't require credentials for public data (funding rates, K-lines)
- Liquidation data requires API Secret; system gracefully falls back to mock data with warning
- All collectors implement retry logic with configurable delays

### LLM Integration
- Uses LangChain's ChatAnthropic for model interaction
- Creates analysis chains using prompt templates and LLM
- Handles both official Anthropic and third-party API providers transparently

## Common Tasks

### Add a New Data Collector
1. Create new file in `src/data_collectors/`
2. Inherit from `BaseCollector` in `base.py`
3. Implement `collect()` method returning dict with data
4. Add to `FactorAnalyzer.analyze_all_factors()` in `src/analyzers/factor_analyzer.py`
5. Update `format_for_llm()` to include new data in formatted output

### Modify Analysis Prompt
Edit `src/agent/prompts.py`:
- `get_system_prompt()`: System role definition
- `get_analysis_prompt()`: Analysis template with market data placeholders

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
- Liquidation data uses mock values when API Secret is unavailable
- All analysis is for educational purposes only - not investment advice
- Claude responses may contain Unicode characters; ensure UTF-8 terminal support
- The `base_url` parameter in ChatAnthropic is the correct way to specify custom API endpoints
- Windows console encoding issues are handled by setting stdout to UTF-8 in `src/main.py`

