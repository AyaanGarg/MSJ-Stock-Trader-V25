import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import uuid
import random

class PortfolioManager:
    """Manages user portfolios, positions, and watchlists."""
    
    def __init__(self):
        self.portfolios_file = "data/portfolios.json"
        self.positions_file = "data/positions.json"
        self.watchlists_file = "data/watchlists.json"
        self._ensure_data_directory()
        self._initialize_data()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs("data", exist_ok=True)
    
    def _initialize_data(self):
        """Initialize portfolio data files."""
        # Initialize portfolios
        if not os.path.exists(self.portfolios_file):
            default_portfolios = {}
            self._save_json(self.portfolios_file, default_portfolios)
        
        # Initialize positions
        if not os.path.exists(self.positions_file):
            default_positions = {}
            self._save_json(self.positions_file, default_positions)
        
        # Initialize watchlists
        if not os.path.exists(self.watchlists_file):
            default_watchlists = {}
            self._save_json(self.watchlists_file, default_watchlists)
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON data from file."""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filename: str, data: Dict):
        """Save JSON data to file."""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_portfolio(self, user_id: str, initial_cash: float = 100000.0) -> Dict:
        """Create a new portfolio for a user."""
        portfolios = self._load_json(self.portfolios_file)
        positions = self._load_json(self.positions_file)
        watchlists = self._load_json(self.watchlists_file)
        
        # Check if portfolio already exists
        if user_id in portfolios:
            return {
                "success": True,
                "message": "Portfolio already exists",
                "portfolio_id": user_id
            }
        
        # Create new portfolio
        portfolios[user_id] = {
            'cash_balance': initial_cash,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        # Initialize empty positions
        positions[user_id] = {}
        
        # Initialize empty watchlist
        watchlists[user_id] = []
        
        # Save all data
        self._save_json(self.portfolios_file, portfolios)
        self._save_json(self.positions_file, positions)
        self._save_json(self.watchlists_file, watchlists)
        
        return {
            "success": True,
            "message": f"Portfolio created with ${initial_cash:,.2f} starting cash",
            "portfolio_id": user_id
        }
    
    def get_portfolio_value(self, user_id: str) -> float:
        """Get total portfolio value for user."""
        # Get cash balance
        cash_balance = self.get_cash_balance(user_id)
        
        # Get positions value
        positions = self.get_positions(user_id)
        positions_value = 0.0
        
        if not positions.empty:
            for _, position in positions.iterrows():
                # Mock current price (in real app, would fetch from market data)
                current_price = random.uniform(50, 200)
                positions_value += position['quantity'] * current_price
        
        return cash_balance + positions_value
    
    def calculate_portfolio_value(self, user_id: str) -> float:
        """Calculate portfolio value - alias for get_portfolio_value for compatibility."""
        return self.get_portfolio_value(user_id)
    
    def get_portfolio_summary(self, user_id: str) -> Dict:
        """Get comprehensive portfolio summary for user."""
        try:
            cash_balance = self.get_cash_balance(user_id)
            positions = self.get_positions(user_id)
            positions_value = 0.0
            
            if not positions.empty:
                for _, position in positions.iterrows():
                    # Mock current price (in real app, would fetch from market data)  
                    current_price = random.uniform(50, 200)
                    positions_value += position['quantity'] * current_price
            
            total_value = cash_balance + positions_value
            
            return {
                "success": True,
                "portfolio": {
                    "cash_balance": cash_balance,
                    "positions_value": positions_value,
                    "total_value": total_value,
                    "positions": positions.to_dict('records') if not positions.empty else []
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting portfolio summary: {str(e)}"
            }
    
    def get_cash_balance(self, user_id: str) -> float:
        """Get cash balance for user."""
        portfolios = self._load_json(self.portfolios_file)
        
        if user_id not in portfolios:
            # Initialize with default cash balance
            portfolios[user_id] = {
                'cash_balance': 100000.0,  # Starting with $100k demo money
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
            self._save_json(self.portfolios_file, portfolios)
            return 100000.0
        
        return portfolios[user_id].get('cash_balance', 0.0)
    
    def update_cash_balance(self, user_id: str, amount: float):
        """Update cash balance for user."""
        portfolios = self._load_json(self.portfolios_file)
        
        if user_id not in portfolios:
            portfolios[user_id] = {
                'cash_balance': 100000.0,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        portfolios[user_id]['cash_balance'] += amount
        portfolios[user_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_json(self.portfolios_file, portfolios)
    
    def get_positions(self, user_id: str) -> pd.DataFrame:
        """Get current long positions for user (quantity > 0)."""
        positions = self._load_json(self.positions_file)
        
        user_positions = positions.get(user_id, {})
        
        if not user_positions:
            return pd.DataFrame(columns=['symbol', 'quantity', 'avg_cost', 'market_value', 'unrealized_pnl'])
        
        # Convert to DataFrame - only long positions
        positions_list = []
        for symbol, position_data in user_positions.items():
            quantity = position_data['quantity']
            # Only include long positions (positive quantity)
            if quantity > 0:
                positions_list.append({
                    'symbol': symbol,
                    'quantity': position_data['quantity'],
                    'avg_cost': position_data['avg_cost'],
                    'last_updated': position_data['last_updated']
                })
        
        return pd.DataFrame(positions_list)
    
    def get_short_positions(self, user_id: str) -> pd.DataFrame:
        """Get current short positions for user (quantity < 0)."""
        positions = self._load_json(self.positions_file)
        
        user_positions = positions.get(user_id, {})
        
        if not user_positions:
            return pd.DataFrame(columns=['symbol', 'quantity', 'avg_cost', 'market_value', 'unrealized_pnl'])
        
        # Convert to DataFrame - only short positions
        positions_list = []
        for symbol, position_data in user_positions.items():
            quantity = position_data['quantity']
            # Only include short positions (negative quantity)
            if quantity < 0:
                positions_list.append({
                    'symbol': symbol,
                    'quantity': position_data['quantity'],
                    'avg_cost': position_data['avg_cost'],
                    'last_updated': position_data['last_updated']
                })
        
        return pd.DataFrame(positions_list)
    
    def update_position(self, user_id: str, symbol: str, quantity: int, price: float):
        """Update or create position for user."""
        positions = self._load_json(self.positions_file)
        
        if user_id not in positions:
            positions[user_id] = {}
        
        if symbol in positions[user_id]:
            # Update existing position
            current_pos = positions[user_id][symbol]
            current_quantity = current_pos['quantity']
            current_avg_cost = current_pos['avg_cost']
            
            # Calculate new average cost
            total_value = (current_quantity * current_avg_cost) + (quantity * price)
            new_quantity = current_quantity + quantity
            
            if new_quantity != 0:
                new_avg_cost = total_value / new_quantity
                positions[user_id][symbol] = {
                    'quantity': new_quantity,
                    'avg_cost': new_avg_cost,
                    'last_updated': datetime.now().isoformat()
                }
            else:
                # Position closed
                del positions[user_id][symbol]
        else:
            # New position
            positions[user_id][symbol] = {
                'quantity': quantity,
                'avg_cost': price,
                'last_updated': datetime.now().isoformat()
            }
        
        self._save_json(self.positions_file, positions)
    
    def get_buying_power(self, user_id: str) -> float:
        """Get available buying power (simplified calculation)."""
        cash_balance = self.get_cash_balance(user_id)
        # In a real app, this would consider margin, borrowed amounts, etc.
        return cash_balance
    
    def get_daily_pnl(self, user_id: str) -> float:
        """Get daily profit and loss based on actual portfolio performance."""
        from modules.market_data import MarketData
        from modules.trading_engine import TradingEngine
        
        market_data = MarketData()
        trading_engine = TradingEngine()
        
        # Get today's trades
        today_trades = trading_engine.get_today_trades(user_id)
        
        if today_trades.empty:
            return 0.0
        
        # Calculate P&L from today's trades
        total_pnl = 0.0
        
        for _, trade in today_trades.iterrows():
            if trade['side'] == 'buy':
                # For buys, calculate unrealized P&L based on current price
                try:
                    current_price = market_data.get_current_price(trade['symbol'])
                    buy_value = trade['quantity'] * trade['price']
                    current_value = trade['quantity'] * current_price
                    total_pnl += (current_value - buy_value)
                except:
                    # If can't get current price, assume no change
                    pass
            else:  # sell
                # For sells, we realize the P&L
                # Get average cost from positions before this sale
                positions = self.get_positions(user_id)
                if not positions.empty:
                    symbol_pos = positions[positions['symbol'] == trade['symbol']]
                    if not symbol_pos.empty:
                        avg_cost = symbol_pos.iloc[0]['avg_cost']
                        sell_price = trade['price']
                        total_pnl += (sell_price - avg_cost) * trade['quantity']
        
        return total_pnl
    
    def get_portfolio_history(self, user_id: str, days: int = 30) -> pd.DataFrame:
        """Get portfolio value history based on actual trades."""
        import json
        
        # Load trades to check if user has any trading history
        try:
            with open('data/trades.json', 'r') as f:
                all_trades = json.load(f)
            user_trades = all_trades.get(user_id, [])
        except:
            user_trades = []
        
        end_date = datetime.now()
        dates = [end_date - timedelta(days=i) for i in range(days)]
        dates.reverse()
        
        # If no trades, show flat line at starting value
        if not user_trades:
            starting_value = 100000.0
            return pd.DataFrame({
                'date': dates,
                'value': [starting_value] * len(dates)
            })
        
        # If trades exist, calculate actual values based on current portfolio
        current_value = self.get_portfolio_value(user_id)
        
        # Create realistic history showing gradual changes
        # Start from 100k and show progression to current value
        starting_value = 100000.0
        value_change = current_value - starting_value
        
        values = []
        for i in range(len(dates)):
            # Gradual progression from start to current
            progress = i / max(1, len(dates) - 1)
            value = starting_value + (value_change * progress)
            values.append(value)
        
        return pd.DataFrame({
            'date': dates,
            'value': values
        })
    
    def get_watchlist(self, user_id: str) -> pd.DataFrame:
        """Get user's watchlist."""
        watchlists = self._load_json(self.watchlists_file)
        
        user_watchlist = watchlists.get(user_id, [])
        
        if not user_watchlist:
            return pd.DataFrame(columns=['symbol', 'added_date'])
        
        return pd.DataFrame(user_watchlist)
    
    def add_to_watchlist(self, user_id: str, symbol: str) -> Dict:
        """Add symbol to user's watchlist."""
        watchlists = self._load_json(self.watchlists_file)
        
        if user_id not in watchlists:
            watchlists[user_id] = []
        
        # Check if symbol already in watchlist
        for item in watchlists[user_id]:
            if item['symbol'] == symbol:
                return {"success": False, "message": "Symbol already in watchlist"}
        
        # Add to watchlist
        watchlists[user_id].append({
            'symbol': symbol,
            'added_date': datetime.now().isoformat()
        })
        
        self._save_json(self.watchlists_file, watchlists)
        
        return {"success": True, "message": f"Added {symbol} to watchlist"}
    
    def remove_from_watchlist(self, user_id: str, symbol: str) -> Dict:
        """Remove symbol from user's watchlist."""
        watchlists = self._load_json(self.watchlists_file)
        
        if user_id not in watchlists:
            return {"success": False, "message": "Watchlist not found"}
        
        # Find and remove symbol
        watchlists[user_id] = [item for item in watchlists[user_id] if item['symbol'] != symbol]
        
        self._save_json(self.watchlists_file, watchlists)
        
        return {"success": True, "message": f"Removed {symbol} from watchlist"}
    
    def get_performance_summary(self, user_id: str) -> Dict:
        """Get portfolio performance summary."""
        current_value = self.get_portfolio_value(user_id)
        cash_balance = self.get_cash_balance(user_id)
        
        # Mock calculations - in real app would track historical data
        starting_value = 100000.0  # Default starting value
        total_return = current_value - starting_value
        total_return_pct = (total_return / starting_value) * 100
        
        return {
            'current_value': current_value,
            'cash_balance': cash_balance,
            'invested_value': current_value - cash_balance,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'daily_pnl': self.get_daily_pnl(user_id)
        }