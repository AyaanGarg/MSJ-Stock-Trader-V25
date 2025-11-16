import json
import os
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
from modules.market_data import MarketData


class TradingHistory:
    """Manages detailed trading history and investment outcomes."""
    
    def __init__(self):
        self.market_data = MarketData()
        self.trades_file = "data/trades.json"
        self.users_file = "data/users.json"
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs("data", exist_ok=True)
    
    def _load_trades(self) -> Dict:
        """Load trades from file."""
        try:
            with open(self.trades_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_users(self) -> Dict:
        """Load users from file."""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def get_user_trading_history(self, user_id: str, days: int = 30) -> pd.DataFrame:
        """Get comprehensive trading history for a user."""
        trades = self._load_trades()
        
        if user_id not in trades:
            return pd.DataFrame()
        
        user_trades = trades[user_id]
        
        # Filter trades by date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        filtered_trades = []
        for trade in user_trades:
            trade_date = datetime.fromisoformat(trade['timestamp'])
            if start_date <= trade_date <= end_date:
                # Calculate P&L for completed trades
                trade_copy = trade.copy()
                
                if trade['order_type'] == 'sell':
                    # Find corresponding buy trade for P&L calculation
                    buy_price = trade.get('avg_buy_price', trade['price'])
                    trade_copy['pnl'] = (trade['price'] - buy_price) * trade['quantity']
                    trade_copy['pnl_percentage'] = ((trade['price'] - buy_price) / buy_price) * 100
                else:
                    # For buy orders, calculate unrealized P&L
                    current_price = self.market_data.get_current_price(trade['symbol'])
                    trade_copy['pnl'] = (current_price - trade['price']) * trade['quantity']
                    trade_copy['pnl_percentage'] = ((current_price - trade['price']) / trade['price']) * 100
                    trade_copy['current_price'] = current_price
                
                # Add holding period for sells
                if trade['order_type'] == 'sell' and 'buy_date' in trade:
                    buy_date = datetime.fromisoformat(trade['buy_date'])
                    holding_period = (trade_date - buy_date).days
                    trade_copy['holding_period_days'] = holding_period
                
                filtered_trades.append(trade_copy)
        
        df = pd.DataFrame(filtered_trades)
        
        if not df.empty:
            df = df.sort_values('timestamp', ascending=False)
            
            # Add formatted columns for display
            df['trade_date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
            df['total_value'] = df['quantity'] * df['price']
            
        return df
    
    def get_investment_outcomes(self, user_id: str) -> Dict:
        """Get detailed investment outcomes and statistics."""
        trades = self._load_trades()
        
        if user_id not in trades:
            return {
                "total_trades": 0,
                "profitable_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "best_trade": None,
                "worst_trade": None,
                "average_holding_period": 0,
                "most_traded_symbol": None
            }
        
        user_trades = trades[user_id]
        
        # Calculate statistics
        total_trades = len(user_trades)
        profitable_trades = 0
        losing_trades = 0
        total_pnl = 0
        trade_pnls = []
        holding_periods = []
        symbol_counts = {}
        
        best_trade = None
        worst_trade = None
        max_profit = float('-inf')
        max_loss = float('inf')
        
        for trade in user_trades:
            if trade['order_type'] == 'sell' and 'avg_buy_price' in trade:
                # Calculate P&L for completed trades
                buy_price = trade['avg_buy_price']
                sell_price = trade['price']
                quantity = trade['quantity']
                
                pnl = (sell_price - buy_price) * quantity
                trade_pnls.append(pnl)
                total_pnl += pnl
                
                if pnl > 0:
                    profitable_trades += 1
                    if pnl > max_profit:
                        max_profit = pnl
                        best_trade = {
                            'symbol': trade['symbol'],
                            'quantity': quantity,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'pnl': pnl,
                            'pnl_percentage': ((sell_price - buy_price) / buy_price) * 100,
                            'date': trade['timestamp']
                        }
                elif pnl < 0:
                    losing_trades += 1
                    if pnl < max_loss:
                        max_loss = pnl
                        worst_trade = {
                            'symbol': trade['symbol'],
                            'quantity': quantity,
                            'buy_price': buy_price,
                            'sell_price': sell_price,
                            'pnl': pnl,
                            'pnl_percentage': ((sell_price - buy_price) / buy_price) * 100,
                            'date': trade['timestamp']
                        }
                
                # Calculate holding period
                if 'buy_date' in trade:
                    buy_date = datetime.fromisoformat(trade['buy_date'])
                    sell_date = datetime.fromisoformat(trade['timestamp'])
                    holding_period = (sell_date - buy_date).days
                    holding_periods.append(holding_period)
            
            # Count symbols
            symbol = trade['symbol']
            symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
        
        # Calculate derived statistics
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        average_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0
        most_traded_symbol = max(symbol_counts.keys(), key=lambda k: symbol_counts[k]) if symbol_counts else None
        
        return {
            "total_trades": total_trades,
            "profitable_trades": profitable_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(total_pnl, 2),
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "average_holding_period": round(average_holding_period, 1),
            "most_traded_symbol": most_traded_symbol,
            "average_profit_per_trade": round(total_pnl / total_trades, 2) if total_trades > 0 else 0
        }
    
    def get_sector_analysis(self, user_id: str) -> pd.DataFrame:
        """Get trading analysis by sector."""
        trades = self._load_trades()
        
        if user_id not in trades:
            return pd.DataFrame()
        
        # Define sector mapping for major stocks
        sector_mapping = {
            'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Technology', 'AMZN': 'Technology',
            'TSLA': 'Automotive', 'NVDA': 'Technology', 'META': 'Technology', 'NFLX': 'Technology',
            'JPM': 'Financial', 'BAC': 'Financial', 'WFC': 'Financial', 'GS': 'Financial',
            'JNJ': 'Healthcare', 'PFE': 'Healthcare', 'UNH': 'Healthcare', 'ABBV': 'Healthcare',
            'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'SLB': 'Energy',
            'WMT': 'Retail', 'HD': 'Retail', 'COST': 'Retail', 'TGT': 'Retail',
            'KO': 'Consumer Goods', 'PEP': 'Consumer Goods', 'PG': 'Consumer Goods', 'MCD': 'Consumer Goods'
        }
        
        user_trades = trades[user_id]
        sector_data = {}
        
        for trade in user_trades:
            symbol = trade['symbol']
            sector = sector_mapping.get(symbol, 'Other')
            
            if sector not in sector_data:
                sector_data[sector] = {
                    'trades': 0,
                    'total_volume': 0,
                    'total_pnl': 0,
                    'symbols': set()
                }
            
            sector_data[sector]['trades'] += 1
            sector_data[sector]['total_volume'] += trade['quantity'] * trade['price']
            sector_data[sector]['symbols'].add(symbol)
            
            # Calculate P&L for sell orders
            if trade['order_type'] == 'sell' and 'avg_buy_price' in trade:
                pnl = (trade['price'] - trade['avg_buy_price']) * trade['quantity']
                sector_data[sector]['total_pnl'] += pnl
        
        # Convert to DataFrame
        sector_analysis = []
        for sector, data in sector_data.items():
            sector_analysis.append({
                'sector': sector,
                'trades': data['trades'],
                'total_volume': round(data['total_volume'], 2),
                'total_pnl': round(data['total_pnl'], 2),
                'unique_symbols': len(data['symbols']),
                'avg_pnl_per_trade': round(data['total_pnl'] / data['trades'], 2) if data['trades'] > 0 else 0
            })
        
        df = pd.DataFrame(sector_analysis)
        if not df.empty:
            df = df.sort_values('total_pnl', ascending=False)
        
        return df
    
    def get_monthly_performance(self, user_id: str, months: int = 12) -> pd.DataFrame:
        """Get monthly trading performance."""
        trades = self._load_trades()
        
        if user_id not in trades:
            return pd.DataFrame()
        
        user_trades = trades[user_id]
        
        # Group trades by month
        monthly_data = {}
        
        for trade in user_trades:
            trade_date = datetime.fromisoformat(trade['timestamp'])
            month_key = trade_date.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'trades': 0,
                    'volume': 0,
                    'pnl': 0,
                    'profitable_trades': 0
                }
            
            monthly_data[month_key]['trades'] += 1
            monthly_data[month_key]['volume'] += trade['quantity'] * trade['price']
            
            # Calculate P&L for sell orders
            if trade['order_type'] == 'sell' and 'avg_buy_price' in trade:
                pnl = (trade['price'] - trade['avg_buy_price']) * trade['quantity']
                monthly_data[month_key]['pnl'] += pnl
                if pnl > 0:
                    monthly_data[month_key]['profitable_trades'] += 1
        
        # Convert to DataFrame
        monthly_performance = []
        for month, data in monthly_data.items():
            win_rate = (data['profitable_trades'] / data['trades'] * 100) if data['trades'] > 0 else 0
            
            monthly_performance.append({
                'month': month,
                'trades': data['trades'],
                'volume': round(data['volume'], 2),
                'pnl': round(data['pnl'], 2),
                'win_rate': round(win_rate, 2)
            })
        
        df = pd.DataFrame(monthly_performance)
        if not df.empty:
            df = df.sort_values('month', ascending=False).head(months)
        
        return df