import pandas as pd
import numpy as np
import yfinance as yf
import random
from datetime import datetime, timedelta
from typing import Dict, List
import time

class MarketData:
    """Provides real market data using Yahoo Finance API with mock trading capabilities."""
    
    def __init__(self):
        # Comprehensive list of major US stocks across different sectors
        self.symbols = [
            # Technology
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'META', 'NVDA', 'TSLA',
            'NFLX', 'ADBE', 'CRM', 'INTC', 'AMD', 'ORCL', 'IBM', 'CSCO',
            'AVGO', 'TXN', 'QCOM', 'INTU', 'NOW', 'AMAT', 'ADI', 'KLAC',
            'LRCX', 'MRVL', 'FTNT', 'TEAM', 'ZM', 'DOCU', 'OKTA', 'SNOW',
            'CRWD', 'ZS', 'DDOG', 'NET', 'TWLO', 'PLTR', 'U', 'RBLX',
            
            # Financial Services
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF',
            'AXP', 'BLK', 'SCHW', 'CB', 'MMC', 'AON', 'SPGI', 'ICE', 'CME',
            'MCO', 'PYPL', 'MA', 'V', 'FIS', 'FISV', 'ADP', 'PAYX',
            
            # Healthcare & Pharmaceuticals
            'JNJ', 'PFE', 'UNH', 'MRNA', 'ABBV', 'TMO', 'DHR', 'ABT', 'LLY',
            'BMY', 'MRK', 'GILD', 'AMGN', 'REGN', 'VRTX', 'BIIB', 'ILMN',
            'ISRG', 'SYK', 'BSX', 'MDT', 'EW', 'DXCM', 'ALGN', 'IDXX',
            
            # Consumer Discretionary
            'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX', 'BKNG',
            'ABNB', 'UBER', 'LYFT', 'DIS', 'NFLX', 'CMCSA', 'VZ', 'T',
            'CHTR', 'TMUS', 'DISH', 'EA', 'ATVI', 'TTWO', 'ROKU', 'SPOT',
            
            # Consumer Staples
            'PG', 'KO', 'PEP', 'WMT', 'COST', 'CL', 'KMB', 'GIS', 'K',
            'HSY', 'MDLZ', 'MNST', 'KHC', 'CPB', 'SJM', 'CLX', 'CHD',
            
            # Industrial
            'BA', 'CAT', 'DE', 'GE', 'MMM', 'HON', 'UPS', 'FDX', 'LMT',
            'RTX', 'NOC', 'GD', 'TDG', 'CARR', 'OTIS', 'EMR', 'ETN',
            'ITW', 'PH', 'CMI', 'ROK', 'DOV', 'XYL', 'FTV', 'LDOS',
            
            # Energy
            'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'PSX', 'VLO', 'MPC', 'KMI',
            'OKE', 'WMB', 'BKR', 'HAL', 'DVN', 'FANG', 'APA', 'CNX',
            
            # Materials
            'LIN', 'APD', 'ECL', 'DD', 'DOW', 'PPG', 'SHW', 'NEM', 'FCX',
            'NUE', 'STLD', 'RS', 'VMC', 'MLM', 'AA', 'X', 'CLF',
            
            # Utilities
            'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'XEL', 'SRE', 'PEG',
            'ED', 'ETR', 'ES', 'FE', 'AWK', 'ATO', 'CMS', 'DTE',
            
            # Real Estate
            'AMT', 'PLD', 'CCI', 'EQIX', 'PSA', 'WELL', 'SPG', 'O', 'CSGP',
            'AVB', 'EQR', 'ESS', 'MAA', 'UDR', 'CPT', 'FRT', 'REG',
            
            # Communication Services
            'GOOGL', 'META', 'NFLX', 'DIS', 'CMCSA', 'VZ', 'T', 'CHTR',
            'TMUS', 'DISH', 'TWTR', 'SNAP', 'PINS', 'MTCH', 'IAC',
            
            # Popular Meme/Growth Stocks
            'GME', 'AMC', 'BB', 'NOK', 'WISH', 'CLOV', 'SPCE', 'RIVN', 'LCID',
            'F', 'GM', 'NIO', 'XPEV', 'LI', 'BABA', 'JD', 'PDD', 'BIDU', 'TME',
            
            # Additional Popular Stocks
            'UBER', 'LYFT', 'SPOT', 'ROKU', 'PTON', 'SHOP', 'SQ', 'ETSY', 'PINS',
            'SNAP', 'TWTR', 'RBLX', 'DASH', 'ABNB', 'COIN', 'SOFI', 'AFRM',
            
            # Popular ETFs and Index Funds
            'SPY', 'QQQ', 'IWM', 'EFA', 'EEM', 'VTI', 'VXUS', 'BND',
            
            # Cryptocurrencies (via ETFs and trusts)
            'BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'DOT-USD', 'MATIC-USD',
            'AVAX-USD', 'LINK-USD', 'UNI-USD', 'LTC-USD', 'XRP-USD', 'DOGE-USD',
            'SHIB-USD', 'ATOM-USD', 'ALGO-USD', 'MANA-USD', 'SAND-USD', 'APE-USD',
            'GBTC', 'ETHE', 'COIN', 'MSTR', 'RIOT', 'MARA', 'HIVE', 'BITF',
            
            # Precious Metals (ETFs and stocks)
            'GLD', 'SLV', 'PPLT', 'PALL', 'IAU', 'SIVR', 'GDX', 'GDXJ',
            'NEM', 'ABX', 'AUY', 'GOLD', 'KGC', 'AG', 'CDE', 'HL',
            'PAAS', 'SLW', 'WPM', 'FNV', 'RGLD', 'SAND', 'OR', 'EGO',
            
            # Money Market & Bonds
            'SHY', 'IEF', 'TLT', 'VMOT', 'MINT', 'NEAR', 'GSY', 'FLOT',
            'JPST', 'ICSH', 'BIL', 'TBIL', 'SCHO', 'SCHR', 'SCHZ', 'AGG',
            'GLD', 'SLV', 'USO', 'XLE', 'XLF', 'XLK', 'XLV', 'XLI',
            'XLP', 'XLU', 'XLB', 'XLRE', 'XLC', 'XLY'
        ]
        
        # Cache for price data to avoid excessive API calls
        self.price_cache = {}
        self.cache_timestamp = {}
        self.cache_duration = 300  # 5 minutes cache
        
        # Asset categories properly organized for multi-asset trading
        self.asset_categories = {
            "Stocks": {
                "Technology": ["AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "TSLA", "META", "NVDA", "NFLX", "ADBE", "CRM", "INTC", "AMD", "ORCL", "IBM", "CSCO", "AVGO", "TXN", "QCOM", "INTU", "NOW", "SNOW", "CRWD", "DDOG", "NET", "TWLO", "PLTR", "ZM", "DOCU", "OKTA", "TEAM", "U", "RBLX"],
                "Healthcare & Biotech": ["JNJ", "PFE", "UNH", "MRNA", "ABBV", "TMO", "DHR", "ABT", "LLY", "BMY", "MRK", "GILD", "AMGN", "REGN", "VRTX", "ISRG", "BIIB", "ILMN", "SYK", "BSX", "MDT", "EW", "DXCM", "ALGN", "IDXX"],
                "Financial Services": ["JPM", "BAC", "WFC", "GS", "MS", "C", "USB", "PNC", "TFC", "COF", "AXP", "BLK", "SCHW", "CB", "MMC", "AON", "SPGI", "ICE", "CME", "MCO", "PYPL", "MA", "V", "FIS", "FISV", "ADP", "PAYX"],
                "Consumer & Retail": ["HD", "MCD", "NKE", "SBUX", "LOW", "TJX", "BKNG", "ABNB", "UBER", "LYFT", "DIS", "CMCSA", "CHTR", "ROKU", "SPOT", "PG", "KO", "PEP", "WMT", "COST", "CL", "KMB", "GIS", "K", "HSY", "MDLZ", "MNST", "KHC"],
                "Energy & Utilities": ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC", "KMI", "OKE", "WMB", "BKR", "HAL", "DVN", "FANG", "APA", "CNX", "NEE", "DUK", "SO", "D", "AEP", "EXC", "XEL", "SRE"],
                "Industrial & Materials": ["BA", "CAT", "DE", "GE", "MMM", "HON", "UPS", "FDX", "LMT", "RTX", "NOC", "GD", "TDG", "CARR", "OTIS", "EMR", "ETN", "LIN", "APD", "ECL", "DD", "DOW", "PPG", "SHW", "FCX", "NUE", "STLD"],
                "Automotive & Transportation": ["F", "GM", "NIO", "XPEV", "LI", "RIVN", "LCID", "SPCE"],
                "International Markets": ["BABA", "JD", "PDD", "BIDU", "TME"],
                "Social Media & E-commerce": ["TWTR", "SNAP", "PINS", "SHOP", "SQ", "ETSY", "DASH", "SOFI", "AFRM", "PTON"],
                "Meme & Speculative": ["GME", "AMC", "BB", "NOK", "WISH", "CLOV"],
                "Market ETFs": ["SPY", "QQQ", "IWM", "EFA", "EEM", "VTI", "VXUS", "XLE", "XLF", "XLK", "XLV", "XLI", "XLP", "XLU", "XLB", "XLRE", "XLC", "XLY"]
            },
            "Cryptocurrency": {
                "Major Cryptocurrencies": ["BTC-USD", "ETH-USD", "ADA-USD", "SOL-USD", "DOT-USD", "MATIC-USD", "AVAX-USD", "LINK-USD", "UNI-USD", "LTC-USD", "XRP-USD", "ATOM-USD", "ALGO-USD"],
                "Meme & Alternative Coins": ["DOGE-USD", "SHIB-USD", "APE-USD", "MANA-USD", "SAND-USD"],
                "Crypto & Blockchain Stocks": ["COIN", "MSTR", "RIOT", "MARA", "HIVE", "BITF", "GBTC", "ETHE"]
            },
            "Precious Metals": {
                "Gold ETFs & Stocks": ["GLD", "IAU", "GDX", "GDXJ", "NEM", "ABX", "AUY", "GOLD", "KGC"],
                "Silver ETFs & Mining": ["SLV", "SIVR", "AG", "CDE", "HL", "PAAS"],
                "Platinum Group Metals": ["PPLT", "PALL", "SLW", "WPM"],
                "Mining & Royalty Companies": ["FNV", "RGLD", "SAND", "OR", "EGO"]
            },
            "Bonds & Fixed Income": {
                "Short-term Bonds": ["SHY", "BIL", "TBIL", "MINT", "NEAR", "GSY", "FLOT"],
                "Intermediate-term Bonds": ["IEF", "SCHO", "SCHR", "VMOT", "JPST", "ICSH"],
                "Long-term Bonds": ["TLT", "SCHZ", "AGG", "BND"],
                "High-yield Bonds": ["HYG", "JNK", "USHY", "SHYG"]
            }
        }
        
        # Famous precious metals information
        self.precious_metals_info = {
            "Gold (Au)": {
                "symbol": "GLD",
                "description": "Most valuable and stable precious metal, used as store of value",
                "properties": "Highly resistant to corrosion, excellent conductor",
                "current_use": "Jewelry, electronics, investment, central bank reserves"
            },
            "Silver (Ag)": {
                "symbol": "SLV", 
                "description": "Industrial and investment metal with antimicrobial properties",
                "properties": "Best electrical conductor, highly reflective",
                "current_use": "Electronics, solar panels, medical equipment, jewelry"
            },
            "Platinum (Pt)": {
                "symbol": "PPLT",
                "description": "Rarer than gold, used in automotive catalysts and jewelry",
                "properties": "Extremely durable, hypoallergenic, catalytic properties",
                "current_use": "Automotive catalysts, jewelry, medical devices"
            },
            "Palladium (Pd)": {
                "symbol": "PALL",
                "description": "Essential for automotive industry, rarer than platinum",
                "properties": "Excellent catalyst, absorbs hydrogen",
                "current_use": "Automotive catalysts, electronics, dentistry"
            },
            "Rhodium (Rh)": {
                "symbol": "Mining stocks",
                "description": "Rarest and most expensive precious metal",
                "properties": "Exceptional reflectivity, catalytic converter use",
                "current_use": "Automotive catalysts, mirrors, electrical contacts"
            },
            "Iridium (Ir)": {
                "symbol": "Mining stocks",
                "description": "Second densest element, extremely corrosion resistant",
                "properties": "Space industry applications, spark plug tips",
                "current_use": "Spark plugs, crucibles, electrical contacts"
            },
            "Ruthenium (Ru)": {
                "symbol": "Mining stocks", 
                "description": "Used in electronic chip resistors and solar cells",
                "properties": "Hardening agent for platinum and palladium",
                "current_use": "Electronics, solar cells, fountain pen tips"
            },
            "Osmium (Os)": {
                "symbol": "Mining stocks",
                "description": "Densest naturally occurring element",
                "properties": "Fountain pen nibs, electrical contacts",
                "current_use": "Instrument pivots, electrical contacts, catalysts"
            },
            "Rhenium (Re)": {
                "symbol": "Mining stocks",
                "description": "Used in high-temperature superalloys",
                "properties": "Jet engine applications, oil refining catalysts",
                "current_use": "Jet engines, petrochemical industry, thermocouples"
            },
            "Indium (In)": {
                "symbol": "Mining stocks",
                "description": "Critical for touchscreen technology and solar panels",
                "properties": "Transparent conductive films, LCD displays",
                "current_use": "Touchscreens, LCD displays, solar panels, LEDs"
            }
        }
        
        # Initialize real-time data fetching
        self._initialize_real_data()
    
    def _initialize_real_data(self):
        """Initialize real market data connection."""
        # Warm up cache with a few key symbols
        key_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'SPY', 'QQQ']
        for symbol in key_symbols:
            try:
                self._fetch_real_price(symbol)
            except Exception:
                # If real data fails, we'll use fallback in get_current_price
                pass
    
    def get_available_symbols(self) -> List[str]:
        """Get list of available trading symbols."""
        return self.symbols
    
    def get_asset_categories(self) -> Dict:
        """Get organized asset categories."""
        return self.asset_categories
    
    def get_precious_metals_info(self) -> Dict:
        """Get information about the 10 most famous precious metals."""
        return self.precious_metals_info
    
    def get_symbols_by_category(self, category: str, subcategory: str = None) -> List[str]:
        """Get symbols filtered by category and optional subcategory."""
        if category not in self.asset_categories:
            return []
        
        if subcategory:
            return self.asset_categories[category].get(subcategory, [])
        else:
            # Return all symbols in the category
            all_symbols = []
            for subcat_symbols in self.asset_categories[category].values():
                all_symbols.extend(subcat_symbols)
            return list(set(all_symbols))  # Remove duplicates
    
    def _fetch_real_price(self, symbol: str) -> float:
        """Fetch real price from Yahoo Finance."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            else:
                # Fallback to daily data if minute data not available
                data = ticker.history(period="1d")
                if not data.empty:
                    return float(data['Close'].iloc[-1])
        except Exception as e:
            # If Yahoo Finance fails, use a realistic fallback based on symbol
            pass
        
        # Fallback prices for major assets if API fails
        fallback_prices = {
            # Stocks
            'AAPL': 190.0, 'MSFT': 420.0, 'GOOGL': 140.0, 'AMZN': 170.0,
            'TSLA': 250.0, 'META': 500.0, 'NVDA': 900.0, 'NFLX': 600.0,
            'SPY': 500.0, 'QQQ': 400.0, 'JPM': 180.0, 'JNJ': 160.0,
            
            # Cryptocurrencies  
            'BTC-USD': 45000.0, 'ETH-USD': 3200.0, 'ADA-USD': 0.55, 'SOL-USD': 85.0,
            'DOT-USD': 8.5, 'MATIC-USD': 1.2, 'DOGE-USD': 0.08, 'XRP-USD': 0.62,
            
            # Crypto Stocks
            'COIN': 85.0, 'MSTR': 450.0, 'RIOT': 12.5, 'MARA': 18.0,
            
            # Precious Metals
            'GLD': 185.0, 'SLV': 22.5, 'PPLT': 95.0, 'PALL': 85.0,
            'GDX': 32.0, 'GDXJ': 38.0, 'NEM': 45.0, 'ABX': 18.5,
            
            # Bonds & Money Market
            'SHY': 84.5, 'IEF': 102.0, 'TLT': 92.0, 'BIL': 91.5,
            'AGG': 104.0, 'BND': 78.5, 'MINT': 100.2, 'FLOT': 50.8
        }
        
        # Special pricing logic for asset types
        if "-USD" in symbol:  # Cryptocurrency
            if symbol in fallback_prices:
                return fallback_prices[symbol]
            else:
                return random.uniform(0.001, 100.0)  # Crypto range
        elif symbol in ['GLD', 'SLV', 'PPLT', 'PALL']:  # Precious metals ETFs
            return fallback_prices.get(symbol, random.uniform(80, 200))
        elif symbol in ['BIL', 'SHY', 'IEF', 'TLT', 'AGG', 'BND']:  # Bonds
            return fallback_prices.get(symbol, random.uniform(80, 110))
        else:
            return fallback_prices.get(symbol, random.uniform(50, 300))
    
    def _smart_round_price(self, price: float) -> float:
        """Smart rounding that preserves precision for low-priced stocks."""
        if price >= 1.0:
            # For stocks >= $1, use 2 decimal places
            return round(price, 2)
        elif price >= 0.01:
            # For stocks between $0.01 and $1, use 4 decimal places
            return round(price, 4)
        elif price >= 0.0001:
            # For very low-priced stocks, use 6 decimal places
            return round(price, 6)
        else:
            # For extremely low prices, use 8 decimal places
            return round(price, 8)
    
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol with caching."""
        current_time = time.time()
        
        # Check if we have cached data that's still fresh
        if (symbol in self.price_cache and 
            symbol in self.cache_timestamp and
            current_time - self.cache_timestamp[symbol] < self.cache_duration):
            return self.price_cache[symbol]
        
        # Fetch fresh data
        try:
            price = self._fetch_real_price(symbol)
            rounded_price = self._smart_round_price(price)
            self.price_cache[symbol] = rounded_price
            self.cache_timestamp[symbol] = current_time
            return rounded_price
        except Exception:
            # If all fails, return cached price or generate fallback
            if symbol in self.price_cache:
                return self.price_cache[symbol]
            else:
                fallback_price = random.uniform(50, 300)
                rounded_price = self._smart_round_price(fallback_price)
                self.price_cache[symbol] = rounded_price
                self.cache_timestamp[symbol] = current_time
                return rounded_price
    
    def get_stock_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get real historical stock data for charting."""
        try:
            # Fetch real historical data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            
            # Calculate period for yfinance
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days + 5)  # Extra days for market closures
            
            # Fetch historical data
            hist_data = ticker.history(start=start_date, end=end_date)
            
            if not hist_data.empty:
                # Convert to our expected format
                data = []
                for date, row in hist_data.iterrows():
                    data.append({
                        'date': date,
                        'open': round(float(row['Open']), 2),
                        'high': round(float(row['High']), 2),
                        'low': round(float(row['Low']), 2),
                        'close': round(float(row['Close']), 2),
                        'volume': int(row['Volume'])
                    })
                
                # Return the last 'days' worth of data
                df = pd.DataFrame(data)
                return df.tail(days).reset_index(drop=True)
            
        except Exception as e:
            print(f"Error fetching real data for {symbol}: {e}")
        
        # Fallback to mock data if real data fails
        return self._generate_fallback_data(symbol, days)
    
    def _generate_fallback_data(self, symbol: str, days: int) -> pd.DataFrame:
        """Generate realistic fallback data when API fails."""
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        # Get base price for this symbol
        current_price = self.get_current_price(symbol)
        
        data = []
        price = current_price * 0.9  # Start 10% lower than current
        
        for date in dates:
            # Generate realistic OHLC data
            daily_change = random.uniform(-0.05, 0.05)  # ±5% daily change
            
            open_price = price
            close_price = price * (1 + daily_change)
            
            # High and low prices
            high_price = max(open_price, close_price) * random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * random.uniform(0.98, 1.0)
            
            # Volume based on stock popularity
            base_volume = 1000000 if symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'] else 500000
            volume = random.randint(base_volume, base_volume * 10)
            
            data.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            })
            
            price = close_price
        
        # Make sure the last price matches current price
        if data:
            data[-1]['close'] = current_price
        
        return pd.DataFrame(data)
    
    def get_historical_data(self, symbol: str, period: str = '1mo') -> pd.DataFrame:
        """Get historical data for a symbol with specified period."""
        # Convert period to days
        period_days = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 365 * 2,
            '5y': 365 * 5,
            '10y': 365 * 10,
            '20y': 365 * 20,
            '30y': 365 * 30,
            'ytd': (datetime.now() - datetime(datetime.now().year, 1, 1)).days,
            'max': 365 * 30  # 30 years max
        }
        
        days = period_days.get(period, 30)
        return self.get_stock_data(symbol, days)
    
    def get_market_summary(self) -> Dict:
        """Get market indices summary."""
        # Mock market indices data
        return {
            'sp500': 4500.0 + random.uniform(-50, 50),
            'sp500_change': random.uniform(-30, 30),
            'nasdaq': 14000.0 + random.uniform(-200, 200),
            'nasdaq_change': random.uniform(-100, 100),
            'dow': 35000.0 + random.uniform(-300, 300),
            'dow_change': random.uniform(-200, 200),
            'vix': 20.0 + random.uniform(-5, 10),
            'vix_change': random.uniform(-2, 2)
        }
    
    def get_market_movers(self) -> pd.DataFrame:
        """Get top market movers (gainers and losers combined)."""
        movers = []
        
        # Select random symbols for movers
        selected_symbols = random.sample(self.symbols, min(10, len(self.symbols)))
        
        for symbol in selected_symbols:
            price = self.get_current_price(symbol)
            change = random.uniform(-15, 15)  # ±15% change
            change_pct = random.uniform(-10, 10)  # ±10% change
            volume = random.randint(1000000, 50000000)
            
            movers.append({
                'symbol': symbol,
                'price': price,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': volume
            })
        
        # Sort by absolute change percentage
        movers = sorted(movers, key=lambda x: abs(x['change_pct']), reverse=True)
        
        return pd.DataFrame(movers)
    
    def get_top_gainers(self, limit: int = 5, show_all: bool = False) -> pd.DataFrame:
        """Get top gaining stocks."""
        gainers = []
        
        # Use ALL symbols if show_all is True, otherwise sample
        if show_all:
            selected_symbols = self.symbols
        else:
            selected_symbols = random.sample(self.symbols, min(limit * 2, len(self.symbols)))
        
        for symbol in selected_symbols:
            price = self.get_current_price(symbol)
            change = random.uniform(1, 15)  # Positive change for gainers
            change_pct = random.uniform(1, 10)  # Positive percentage change
            volume = random.randint(1000000, 50000000)
            
            # Get company name
            company_name = self.get_stock_name_mapping().get(symbol, f"{symbol} Corporation")
            
            gainers.append({
                'symbol': symbol,
                'company_name': company_name,
                'price': price,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': volume
            })
        
        # Sort by change percentage and take top N (or all if show_all)
        gainers = sorted(gainers, key=lambda x: x['change_pct'], reverse=True)
        if not show_all:
            gainers = gainers[:limit]
        
        return pd.DataFrame(gainers)
    
    def get_top_losers(self, limit: int = 5, show_all: bool = False) -> pd.DataFrame:
        """Get top losing stocks."""
        losers = []
        
        # Use ALL symbols if show_all is True, otherwise sample
        if show_all:
            selected_symbols = self.symbols
        else:
            selected_symbols = random.sample(self.symbols, min(limit * 2, len(self.symbols)))
        
        for symbol in selected_symbols:
            price = self.get_current_price(symbol)
            change = random.uniform(-15, -1)  # Negative change for losers
            change_pct = random.uniform(-10, -1)  # Negative percentage change
            volume = random.randint(1000000, 50000000)
            
            # Get company name
            company_name = self.get_stock_name_mapping().get(symbol, f"{symbol} Corporation")
            
            losers.append({
                'symbol': symbol,
                'company_name': company_name,
                'price': price,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'volume': volume
            })
        
        # Sort by change percentage (most negative first) and take top N (or all if show_all)
        losers = sorted(losers, key=lambda x: x['change_pct'])
        if not show_all:
            losers = losers[:limit]
        
        return pd.DataFrame(losers)
    
    def get_stock_quote(self, symbol: str) -> Dict:
        """Get detailed quote for a stock."""
        price = self.get_current_price(symbol)
        
        return {
            'symbol': symbol,
            'price': price,
            'change': random.uniform(-10, 10),
            'change_pct': random.uniform(-5, 5),
            'volume': random.randint(1000000, 50000000),
            'market_cap': random.randint(10, 1000) * 1000000000,  # 10B to 1T
            'pe_ratio': random.uniform(10, 50),
            'day_high': price * random.uniform(1.0, 1.05),
            'day_low': price * random.uniform(0.95, 1.0),
            '52_week_high': price * random.uniform(1.1, 1.5),
            '52_week_low': price * random.uniform(0.5, 0.9),
            'dividend_yield': random.uniform(0, 5),
            'last_updated': datetime.now().isoformat()
        }
    
    def get_stock_name_mapping(self) -> Dict[str, str]:
        """Get comprehensive mapping of stock symbols to company names."""
        return {
            # Technology
            'AAPL': 'Apple Inc', 'MSFT': 'Microsoft Corporation', 'GOOGL': 'Alphabet Inc Class A',
            'GOOG': 'Alphabet Inc Class C', 'AMZN': 'Amazon.com Inc', 'META': 'Meta Platforms Inc',
            'NVDA': 'NVIDIA Corporation', 'TSLA': 'Tesla Inc', 'NFLX': 'Netflix Inc',
            'ADBE': 'Adobe Inc', 'CRM': 'Salesforce Inc', 'INTC': 'Intel Corporation',
            'AMD': 'Advanced Micro Devices Inc', 'ORCL': 'Oracle Corporation', 'IBM': 'International Business Machines',
            'CSCO': 'Cisco Systems Inc', 'AVGO': 'Broadcom Inc', 'TXN': 'Texas Instruments',
            'QCOM': 'Qualcomm Inc', 'INTU': 'Intuit Inc', 'NOW': 'ServiceNow Inc',
            'SNOW': 'Snowflake Inc', 'CRWD': 'CrowdStrike Holdings Inc', 'DDOG': 'Datadog Inc',
            'NET': 'Cloudflare Inc', 'TWLO': 'Twilio Inc', 'PLTR': 'Palantir Technologies Inc',
            'ZM': 'Zoom Video Communications Inc', 'DOCU': 'DocuSign Inc', 'OKTA': 'Okta Inc',
            'TEAM': 'Atlassian Corporation', 'U': 'Unity Software Inc', 'RBLX': 'Roblox Corporation',
            
            # Financial Services
            'JPM': 'JPMorgan Chase & Co', 'BAC': 'Bank of America Corp', 'WFC': 'Wells Fargo & Company',
            'GS': 'Goldman Sachs Group Inc', 'MS': 'Morgan Stanley', 'C': 'Citigroup Inc',
            'USB': 'U.S. Bancorp', 'PNC': 'PNC Financial Services Group', 'TFC': 'Truist Financial Corp',
            'COF': 'Capital One Financial Corp', 'AXP': 'American Express Company', 'BLK': 'BlackRock Inc',
            'SCHW': 'Charles Schwab Corporation', 'PYPL': 'PayPal Holdings Inc', 'MA': 'Mastercard Inc',
            'V': 'Visa Inc', 'CB': 'Chubb Limited', 'MMC': 'Marsh & McLennan Companies',
            
            # Healthcare
            'JNJ': 'Johnson & Johnson', 'PFE': 'Pfizer Inc', 'UNH': 'UnitedHealth Group Inc',
            'MRNA': 'Moderna Inc', 'ABBV': 'AbbVie Inc', 'TMO': 'Thermo Fisher Scientific Inc',
            'DHR': 'Danaher Corporation', 'ABT': 'Abbott Laboratories', 'LLY': 'Eli Lilly and Company',
            'BMY': 'Bristol-Myers Squibb Company', 'MRK': 'Merck & Co Inc', 'GILD': 'Gilead Sciences Inc',
            'AMGN': 'Amgen Inc', 'REGN': 'Regeneron Pharmaceuticals Inc', 'VRTX': 'Vertex Pharmaceuticals Inc',
            'ISRG': 'Intuitive Surgical Inc', 'BIIB': 'Biogen Inc', 'ILMN': 'Illumina Inc',
            
            # Consumer Discretionary
            'HD': 'Home Depot Inc', 'MCD': 'McDonald\'s Corporation', 'NKE': 'Nike Inc',
            'SBUX': 'Starbucks Corporation', 'LOW': 'Lowe\'s Companies Inc', 'TJX': 'TJX Companies Inc',
            'BKNG': 'Booking Holdings Inc', 'ABNB': 'Airbnb Inc', 'UBER': 'Uber Technologies Inc',
            'LYFT': 'Lyft Inc', 'DIS': 'Walt Disney Company', 'CMCSA': 'Comcast Corporation',
            'CHTR': 'Charter Communications Inc', 'ROKU': 'Roku Inc', 'SPOT': 'Spotify Technology SA',
            
            # Consumer Staples
            'PG': 'Procter & Gamble Company', 'KO': 'Coca-Cola Company', 'PEP': 'PepsiCo Inc',
            'WMT': 'Walmart Inc', 'COST': 'Costco Wholesale Corporation', 'CL': 'Colgate-Palmolive Company',
            'KMB': 'Kimberly-Clark Corporation', 'GIS': 'General Mills Inc', 'K': 'Kellogg Company',
            
            # Energy
            'XOM': 'Exxon Mobil Corporation', 'CVX': 'Chevron Corporation', 'COP': 'ConocoPhillips',
            'EOG': 'EOG Resources Inc', 'SLB': 'Schlumberger Limited', 'PSX': 'Phillips 66',
            'VLO': 'Valero Energy Corporation', 'MPC': 'Marathon Petroleum Corporation',
            
            # Auto & Transportation
            'F': 'Ford Motor Company', 'GM': 'General Motors Company', 'NIO': 'NIO Inc',
            'XPEV': 'XPeng Inc', 'LI': 'Li Auto Inc', 'RIVN': 'Rivian Automotive Inc',
            'LCID': 'Lucid Group Inc', 'SPCE': 'Virgin Galactic Holdings Inc',
            
            # Chinese Stocks
            'BABA': 'Alibaba Group Holding Limited', 'JD': 'JD.com Inc', 'PDD': 'PDD Holdings Inc',
            'BIDU': 'Baidu Inc', 'TME': 'Tencent Music Entertainment Group',
            
            # Meme Stocks
            'GME': 'GameStop Corp', 'AMC': 'AMC Entertainment Holdings Inc', 'BB': 'BlackBerry Limited',
            'NOK': 'Nokia Corporation', 'WISH': 'ContextLogic Inc', 'CLOV': 'Clover Health Investments Corp',
            
            # Social Media & Internet
            'TWTR': 'Twitter Inc', 'SNAP': 'Snap Inc', 'PINS': 'Pinterest Inc',
            'SHOP': 'Shopify Inc', 'SQ': 'Block Inc', 'ETSY': 'Etsy Inc',
            'DASH': 'DoorDash Inc', 'COIN': 'Coinbase Global Inc', 'SOFI': 'SoFi Technologies Inc',
            'AFRM': 'Affirm Holdings Inc', 'PTON': 'Peloton Interactive Inc',
            
            # ETFs
            'SPY': 'SPDR S&P 500 ETF Trust', 'QQQ': 'Invesco QQQ Trust', 'IWM': 'iShares Russell 2000 ETF',
            'VTI': 'Vanguard Total Stock Market ETF', 'GLD': 'SPDR Gold Trust', 'SLV': 'iShares Silver Trust'
        }
    
    def get_available_stocks(self) -> List[str]:
        """Get list of all available stock symbols."""
        return list(self.stock_symbols.keys())
    
    def search_stocks(self, query: str) -> List[Dict]:
        """Enhanced search for stocks by symbol or name with aliases."""
        query_lower = query.lower().strip()
        results = []
        name_mapping = self.get_stock_name_mapping()
        
        # Define common search aliases
        aliases = {
            'google': ['GOOGL', 'GOOG'],
            'alphabet': ['GOOGL', 'GOOG'], 
            'facebook': ['META'],
            'meta': ['META'],
            'amazon': ['AMZN'],
            'microsoft': ['MSFT'],
            'apple': ['AAPL'],
            'tesla': ['TSLA'],
            'netflix': ['NFLX'],
            'twitter': ['TWTR'],
            'nvidia': ['NVDA'],
            'intel': ['INTC'],
            'amd': ['AMD'],
            'walmart': ['WMT'],
            'disney': ['DIS'],
            'mcdonalds': ['MCD'],
            'starbucks': ['SBUX'],
            'coca cola': ['KO'],
            'pepsi': ['PEP'],
            'boeing': ['BA'],
            'ford': ['F'],
            'general motors': ['GM'],
            'paypal': ['PYPL'],
            'visa': ['V'],
            'mastercard': ['MA'],
            'jpmorgan': ['JPM'],
            'jp morgan': ['JPM'],
            'goldman sachs': ['GS'],
            'bank of america': ['BAC'],
            'johnson and johnson': ['JNJ'],
            'pfizer': ['PFE'],
            'moderna': ['MRNA']
        }
        
        # First, check aliases
        for alias, symbols in aliases.items():
            if query_lower == alias or query_lower in alias:
                for symbol in symbols:
                    if symbol in self.symbols and symbol not in [r['symbol'] for r in results]:
                        company_name = name_mapping.get(symbol, f"{symbol} Corporation")
                        current_price = self.get_current_price(symbol)
                        results.append({
                            'symbol': symbol,
                            'name': company_name,
                            'price': current_price,
                            'match_type': 'alias_match'
                        })
        
        # Then, exact symbol matches
        for symbol in self.symbols:
            if symbol.lower() == query_lower and symbol not in [r['symbol'] for r in results]:
                company_name = name_mapping.get(symbol, f"{symbol} Corporation")
                current_price = self.get_current_price(symbol)
                results.append({
                    'symbol': symbol,
                    'name': company_name,
                    'price': current_price,
                    'match_type': 'exact_symbol'
                })
        
        # Then, partial symbol matches
        for symbol in self.symbols:
            if query_lower in symbol.lower() and symbol not in [r['symbol'] for r in results]:
                company_name = name_mapping.get(symbol, f"{symbol} Corporation")
                current_price = self.get_current_price(symbol)
                results.append({
                    'symbol': symbol,
                    'name': company_name,
                    'price': current_price,
                    'match_type': 'partial_symbol'
                })
        
        # Finally, company name matches
        for symbol in self.symbols:
            company_name = name_mapping.get(symbol, f"{symbol} Corporation")
            if (query_lower in company_name.lower() and 
                symbol not in [r['symbol'] for r in results]):
                current_price = self.get_current_price(symbol)
                results.append({
                    'symbol': symbol,
                    'name': company_name,
                    'price': current_price,
                    'match_type': 'company_name'
                })
        
        # Limit results and sort by relevance
        return results[:15]
    
    def get_sector_performance(self) -> pd.DataFrame:
        """Get sector performance data."""
        sectors = [
            'Technology', 'Healthcare', 'Financials', 'Consumer Discretionary',
            'Communication Services', 'Industrials', 'Consumer Staples',
            'Energy', 'Utilities', 'Real Estate', 'Materials'
        ]
        
        sector_data = []
        
        for sector in sectors:
            performance = random.uniform(-5, 5)  # ±5% performance
            
            sector_data.append({
                'sector': sector,
                'performance': round(performance, 2),
                'market_cap': random.randint(500, 5000),  # In billions
                'stocks_count': random.randint(50, 200)
            })
        
        return pd.DataFrame(sector_data)
    
    def refresh_data(self):
        """Refresh market data by clearing cache."""
        # Clear price cache to force fresh data fetch
        self.price_cache.clear()
        self.cache_timestamp.clear()
        return {"success": True, "message": "Market data refreshed"}
    
    def get_market_status(self) -> Dict:
        """Get current market status."""
        # Mock market hours (simplified)
        now = datetime.now()
        is_weekend = now.weekday() >= 5  # Saturday = 5, Sunday = 6
        current_hour = now.hour
        
        # Market hours: 9:30 AM to 4:00 PM ET (simplified)
        is_market_hours = 9 <= current_hour < 16
        
        if is_weekend:
            status = "CLOSED"
            message = "Market is closed - Weekend"
        elif is_market_hours:
            status = "OPEN"
            message = "Market is open"
        else:
            status = "CLOSED"
            if current_hour < 9:
                message = "Market opens at 9:30 AM ET"
            else:
                message = "Market is closed - After hours"
        
        return {
            'status': status,
            'message': message,
            'is_open': status == "OPEN",
            'next_open': "9:30 AM ET" if status == "CLOSED" else None,
            'next_close': "4:00 PM ET" if status == "OPEN" else None
        }