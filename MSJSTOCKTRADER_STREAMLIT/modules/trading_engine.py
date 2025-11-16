import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import uuid
import random
import pytz

class TradingEngine:
    """Handles trade execution and order management with market hours support."""
    
    def __init__(self):
        self.orders_file = "data/orders.json"
        self.trades_file = "data/trades.json"
        self.market_open_hour = 13  # 1:00 PM PST
        self.timezone = pytz.timezone('America/Los_Angeles')  # PST/PDT timezone
        self._ensure_data_directory()
        self._initialize_data()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        os.makedirs("data", exist_ok=True)
    
    def _initialize_data(self):
        """Initialize trading data files."""
        if not os.path.exists(self.orders_file):
            self._save_json(self.orders_file, {})
        
        if not os.path.exists(self.trades_file):
            self._save_json(self.trades_file, {})
    
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
    
    def is_market_open(self) -> bool:
        """Check if market is currently open for trading.
        Market hours: Weekdays (Mon-Fri), starting at 1:00 PM PST.
        Market is closed on weekends (Saturday and Sunday).
        """
        now_pst = datetime.now(self.timezone)
        
        # Check if it's a weekend
        if now_pst.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False
        
        # Check if it's after market open time (1:00 PM PST)
        if now_pst.hour < self.market_open_hour:
            return False
        
        return True
    
    def get_next_market_open(self) -> datetime:
        """Get the next market open time (1:00 PM PST on next weekday)."""
        now_pst = datetime.now(self.timezone)
        next_open = now_pst.replace(hour=self.market_open_hour, minute=0, second=0, microsecond=0)
        
        # If today's market time hasn't passed yet and it's a weekday
        if next_open > now_pst and now_pst.weekday() < 5:
            return next_open
        
        # Move to next day
        next_open += timedelta(days=1)
        
        # Skip weekends
        while next_open.weekday() >= 5:  # Skip Saturday (5) and Sunday (6)
            next_open += timedelta(days=1)
        
        return next_open
    
    def place_order(self, order_data: Dict) -> Dict:
        """Place a trading order."""
        from modules.portfolio_manager import PortfolioManager
        from modules.market_data import MarketData
        
        portfolio_manager = PortfolioManager()
        market_data = MarketData()
        
        # Validate order data
        required_fields = ['symbol', 'side', 'quantity', 'order_type', 'user_id']
        for field in required_fields:
            if field not in order_data:
                return {"success": False, "message": f"Missing required field: {field}"}
        
        # Check buying power for buy orders
        if order_data['side'] == 'buy':
            current_price = market_data.get_current_price(order_data['symbol'])
            order_value = float(order_data['quantity']) * current_price
            buying_power = portfolio_manager.get_buying_power(order_data['user_id'])
            
            if order_value > buying_power:
                return {"success": False, "message": "Insufficient buying power"}
        
        # Check buying power for short sell (requires collateral)
        if order_data['side'] == 'short_sell':
            current_price = market_data.get_current_price(order_data['symbol'])
            order_value = float(order_data['quantity']) * current_price
            buying_power = portfolio_manager.get_buying_power(order_data['user_id'])
            
            if order_value > buying_power:
                return {"success": False, "message": "Insufficient buying power for short sell collateral"}
        
        # Check position for sell orders
        if order_data['side'] == 'sell':
            positions = portfolio_manager.get_positions(order_data['user_id'])
            if positions.empty:
                return {"success": False, "message": "No positions to sell"}
            
            symbol_position = positions[positions['symbol'] == order_data['symbol']]
            if symbol_position.empty:
                return {"success": False, "message": f"No position in {order_data['symbol']}"}
            
            available_quantity = symbol_position.iloc[0]['quantity']
            if float(order_data['quantity']) > available_quantity:
                return {"success": False, "message": "Insufficient shares to sell"}
        
        # Check short position for short cover orders
        if order_data['side'] == 'short_cover':
            short_positions = portfolio_manager.get_short_positions(order_data['user_id'])
            if short_positions.empty:
                return {"success": False, "message": "No short positions to cover"}
            
            symbol_position = short_positions[short_positions['symbol'] == order_data['symbol']]
            if symbol_position.empty:
                return {"success": False, "message": f"No short position in {order_data['symbol']}"}
            
            available_quantity = abs(symbol_position.iloc[0]['quantity'])
            if float(order_data['quantity']) > available_quantity:
                return {"success": False, "message": "Insufficient short shares to cover"}
        
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Create order
        order = {
            'order_id': order_id,
            'user_id': order_data['user_id'],
            'symbol': order_data['symbol'],
            'side': order_data['side'],
            'quantity': order_data['quantity'],
            'order_type': order_data['order_type'],
            'price': order_data.get('price'),
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'filled_at': None,
            'filled_price': None,
            'filled_quantity': 0
        }
        
        # Save order
        orders = self._load_json(self.orders_file)
        if order_data['user_id'] not in orders:
            orders[order_data['user_id']] = []
        
        orders[order_data['user_id']].append(order)
        self._save_json(self.orders_file, orders)
        
        # Execute order immediately (for demo/educational platform)
        # Note: Real market hours are tracked but orders execute instantly for better UX
        execution_result = self._execute_order(order)
        market_status = "open" if self.is_market_open() else "closed (simulated execution)"
        
        # Update the order in the orders file (change from pending to filled)
        orders = self._load_json(self.orders_file)
        if order_data['user_id'] in orders:
            for i, stored_order in enumerate(orders[order_data['user_id']]):
                if stored_order['order_id'] == order_id:
                    orders[order_data['user_id']][i] = order
                    break
        self._save_json(self.orders_file, orders)
        
        return {
            "success": True, 
            "order_id": order_id,
            "status": "filled",
            "message": f"Order executed successfully (Market: {market_status})",
            "execution_result": execution_result
        }
    
    def _execute_order(self, order: Dict) -> Dict:
        """Execute an order (simplified simulation)."""
        from modules.portfolio_manager import PortfolioManager
        from modules.market_data import MarketData
        
        portfolio_manager = PortfolioManager()
        market_data = MarketData()
        
        # Get current market price
        current_price = market_data.get_current_price(order['symbol'])
        
        # Simulate execution price (add some slippage)
        slippage = random.uniform(-0.01, 0.01)  # ±1% slippage
        execution_price = current_price * (1 + slippage)
        
        # Update order status
        order['status'] = 'filled'
        order['filled_at'] = datetime.now().isoformat()
        order['filled_price'] = execution_price
        order['filled_quantity'] = order['quantity']
        
        # Update portfolio based on order type
        if order['side'] == 'buy':
            # Add long position and deduct cash
            portfolio_manager.update_position(
                order['user_id'], 
                order['symbol'], 
                order['quantity'], 
                execution_price
            )
            portfolio_manager.update_cash_balance(
                order['user_id'], 
                -order['quantity'] * execution_price
            )
        elif order['side'] == 'sell':
            # Reduce long position and add cash
            portfolio_manager.update_position(
                order['user_id'], 
                order['symbol'], 
                -order['quantity'], 
                execution_price
            )
            portfolio_manager.update_cash_balance(
                order['user_id'], 
                order['quantity'] * execution_price
            )
        elif order['side'] == 'short_sell':
            # Create short position (negative quantity) and add cash (borrow proceeds)
            portfolio_manager.update_position(
                order['user_id'], 
                order['symbol'], 
                -order['quantity'],  # Negative for short
                execution_price
            )
            portfolio_manager.update_cash_balance(
                order['user_id'], 
                order['quantity'] * execution_price  # Get cash from short sale
            )
        elif order['side'] == 'short_cover':
            # Cover short position (add back positive quantity) and deduct cash
            portfolio_manager.update_position(
                order['user_id'], 
                order['symbol'], 
                order['quantity'],  # Positive to cover short
                execution_price
            )
            portfolio_manager.update_cash_balance(
                order['user_id'], 
                -order['quantity'] * execution_price  # Pay to cover
            )
        
        # Record trade
        self._record_trade(order, execution_price)
        
        return {
            "executed": True,
            "execution_price": execution_price,
            "execution_time": order['filled_at']
        }
    
    def _record_trade(self, order: Dict, execution_price: float):
        """Record executed trade."""
        trade = {
            'trade_id': str(uuid.uuid4()),
            'order_id': order['order_id'],
            'user_id': order['user_id'],
            'symbol': order['symbol'],
            'side': order['side'],
            'quantity': order['quantity'],
            'price': execution_price,
            'value': order['quantity'] * execution_price,
            'executed_at': datetime.now().isoformat()
        }
        
        trades = self._load_json(self.trades_file)
        if order['user_id'] not in trades:
            trades[order['user_id']] = []
        
        trades[order['user_id']].append(trade)
        self._save_json(self.trades_file, trades)
    
    def get_pending_orders(self, user_id: str = None) -> List[Dict]:
        """Get all pending orders, optionally filtered by user_id."""
        orders = self._load_json(self.orders_file)
        
        pending_orders = []
        
        if user_id:
            # Get pending orders for specific user
            user_orders = orders.get(user_id, [])
            # Safety check: ensure user_orders is a list and each order is a dict
            if isinstance(user_orders, list):
                pending_orders = [order for order in user_orders if isinstance(order, dict) and order.get('status') == 'pending']
            else:
                pending_orders = []
        else:
            # Get all pending orders across all users
            for uid, user_orders in orders.items():
                # Safety check: ensure user_orders is a list
                if not isinstance(user_orders, list):
                    continue
                for order in user_orders:
                    # Safety check: ensure order is a dict
                    if isinstance(order, dict) and order.get('status') == 'pending':
                        order_copy = order.copy()
                        order_copy['user_id'] = uid
                        pending_orders.append(order_copy)
        
        # Add estimated execution time to each order
        next_open = self.get_next_market_open()
        for order in pending_orders:
            order['estimated_execution'] = next_open.isoformat()
            order['estimated_execution_formatted'] = next_open.strftime('%A, %B %d at %I:%M %p PST')
        
        return pending_orders
    
    def process_pending_orders(self) -> Dict:
        """Process all pending orders. Should be called when market opens (1:00 PM PST weekdays)."""
        if not self.is_market_open():
            return {
                "success": False,
                "message": "Market is closed. Cannot process orders.",
                "processed_count": 0
            }
        
        orders = self._load_json(self.orders_file)
        processed_count = 0
        failed_count = 0
        
        # Process all pending orders
        for user_id, user_orders in orders.items():
            for i, order in enumerate(user_orders):
                if order['status'] == 'pending':
                    try:
                        # Execute the order
                        execution_result = self._execute_order(order)
                        
                        # Update the order in the stored data
                        orders[user_id][i] = order
                        processed_count += 1
                    except Exception as e:
                        # Mark order as failed
                        orders[user_id][i]['status'] = 'failed'
                        orders[user_id][i]['failure_reason'] = str(e)
                        failed_count += 1
        
        # Save updated orders
        self._save_json(self.orders_file, orders)
        
        return {
            "success": True,
            "message": f"Processed {processed_count} orders successfully, {failed_count} failed",
            "processed_count": processed_count,
            "failed_count": failed_count
        }
    
    def get_user_orders(self, user_id: str, status: str = None) -> pd.DataFrame:
        """Get orders for a user."""
        orders = self._load_json(self.orders_file)
        
        user_orders = orders.get(user_id, [])
        
        if status:
            user_orders = [order for order in user_orders if order['status'] == status]
        
        if not user_orders:
            return pd.DataFrame(columns=['order_id', 'symbol', 'side', 'quantity', 'order_type', 'status', 'created_at'])
        
        return pd.DataFrame(user_orders)
    
    def get_recent_trades(self, user_id: str, limit: int = 10) -> pd.DataFrame:
        """Get recent trades for a user."""
        trades = self._load_json(self.trades_file)
        
        user_trades = trades.get(user_id, [])
        
        # Sort by execution time and limit
        user_trades = sorted(user_trades, key=lambda x: x['executed_at'], reverse=True)[:limit]
        
        if not user_trades:
            return pd.DataFrame(columns=['trade_id', 'symbol', 'side', 'quantity', 'price', 'value', 'executed_at'])
        
        return pd.DataFrame(user_trades)
    
    def get_user_trades(self, user_id: str) -> list:
        """Get all trades for a user as a list for compatibility."""
        trades_df = self.get_all_trades(user_id)
        if trades_df.empty:
            return []
        return trades_df.to_dict('records')
    
    def get_all_trades(self, user_id: str) -> pd.DataFrame:
        """Get all trading history for a user."""
        trades = self._load_json(self.trades_file)
        user_trades = trades.get(user_id, [])
        
        if not user_trades:
            return pd.DataFrame(columns=['Symbol', 'Side', 'Quantity', 'Price', 'Value', 'Date'])
        
        # Convert to DataFrame
        df_data = []
        for trade in user_trades:
            df_data.append({
                'Symbol': trade['symbol'],
                'Side': trade['side'].title(),
                'Quantity': trade['quantity'],
                'Price': f"${trade['price']:.2f}",
                'Value': f"${trade['value']:,.2f}",
                'Date': datetime.fromisoformat(trade['executed_at']).strftime('%Y-%m-%d %H:%M')
            })
        
        return pd.DataFrame(df_data)
    
    def get_today_trades(self, user_id: str) -> pd.DataFrame:
        """Get today's trades for a user."""
        trades = self._load_json(self.trades_file)
        
        user_trades = trades.get(user_id, [])
        
        # Filter for today's trades
        today = datetime.now().date()
        today_trades = []
        
        for trade in user_trades:
            trade_date = datetime.fromisoformat(trade['executed_at']).date()
            if trade_date == today:
                today_trades.append(trade)
        
        if not today_trades:
            return pd.DataFrame(columns=['trade_id', 'symbol', 'side', 'quantity', 'price', 'value', 'executed_at'])
        
        return pd.DataFrame(today_trades)
    
    def get_performance_metrics(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict:
        """Get trading performance metrics for a date range."""
        trades = self._load_json(self.trades_file)
        
        user_trades = trades.get(user_id, [])
        
        # Filter trades by date range
        filtered_trades = []
        for trade in user_trades:
            trade_date = datetime.fromisoformat(trade['executed_at']).date()
            if start_date.date() <= trade_date <= end_date.date():
                filtered_trades.append(trade)
        
        if not filtered_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_pnl': 0.0,
                'avg_trade_pnl': 0.0
            }
        
        # Calculate real metrics based on actual trades
        from modules.portfolio_manager import PortfolioManager
        from modules.market_data import MarketData
        
        portfolio_manager = PortfolioManager()
        market_data = MarketData()
        
        total_trades = len(filtered_trades)
        total_pnl = 0.0
        winning_trades = 0
        losing_trades = 0
        
        # Track buy prices for each symbol
        symbol_buy_prices = {}
        
        for trade in filtered_trades:
            symbol = trade['symbol']
            side = trade['side']
            price = trade['price']
            quantity = trade['quantity']
            
            if side == 'buy':
                # Store buy price for later P&L calculation
                if symbol not in symbol_buy_prices:
                    symbol_buy_prices[symbol] = []
                symbol_buy_prices[symbol].append({'price': price, 'quantity': quantity})
            else:  # sell
                # Calculate P&L from this sell
                if symbol in symbol_buy_prices and symbol_buy_prices[symbol]:
                    # Use average buy price
                    buy_records = symbol_buy_prices[symbol]
                    total_buy_value = sum(r['price'] * r['quantity'] for r in buy_records)
                    total_buy_quantity = sum(r['quantity'] for r in buy_records)
                    avg_buy_price = total_buy_value / total_buy_quantity if total_buy_quantity > 0 else price
                    
                    trade_pnl = (price - avg_buy_price) * quantity
                    total_pnl += trade_pnl
                    
                    if trade_pnl > 0:
                        winning_trades += 1
                    else:
                        losing_trades += 1
        
        # Calculate unrealized P&L for remaining positions
        for symbol, buy_records in symbol_buy_prices.items():
            try:
                current_price = market_data.get_current_price(symbol)
                for record in buy_records:
                    unrealized_pnl = (current_price - record['price']) * record['quantity']
                    total_pnl += unrealized_pnl
            except:
                # Skip if can't get current price
                pass
        
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        avg_trade_pnl = total_pnl / total_trades if total_trades > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_trade_pnl': avg_trade_pnl
        }
    
    def get_trade_history(self, user_id: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get trade history with P&L for charting."""
        trades = self._load_json(self.trades_file)
        
        user_trades = trades.get(user_id, [])
        
        # Filter trades by date range
        filtered_trades = []
        for trade in user_trades:
            trade_date = datetime.fromisoformat(trade['executed_at']).date()
            if start_date.date() <= trade_date <= end_date.date():
                filtered_trades.append(trade)
        
        if not filtered_trades:
            return pd.DataFrame(columns=['date', 'pnl', 'cumulative_pnl'])
        
        # Create DataFrame and add mock P&L
        df = pd.DataFrame(filtered_trades)
        df['date'] = pd.to_datetime(df['executed_at']).dt.date
        
        # Mock P&L per trade
        df['pnl'] = [random.uniform(-500, 1000) for _ in range(len(df))]
        df['cumulative_pnl'] = df['pnl'].cumsum()
        
        return df[['date', 'pnl', 'cumulative_pnl']]
    
    def cancel_order(self, user_id: str, order_id: str) -> Dict:
        """Cancel a pending order."""
        orders = self._load_json(self.orders_file)
        
        user_orders = orders.get(user_id, [])
        
        # Find and cancel order
        for i, order in enumerate(user_orders):
            if order['order_id'] == order_id:
                if order['status'] == 'pending':
                    orders[user_id][i]['status'] = 'cancelled'
                    orders[user_id][i]['cancelled_at'] = datetime.now().isoformat()
                    self._save_json(self.orders_file, orders)
                    return {"success": True, "message": "Order cancelled successfully"}
                else:
                    return {"success": False, "message": f"Cannot cancel order with status: {order['status']}"}
        
        return {"success": False, "message": "Order not found"}
    
    def get_daily_trade_count(self) -> int:
        """Get total trades across all users today (admin function)."""
        trades = self._load_json(self.trades_file)
        
        today = datetime.now().date()
        total_trades = 0
        
        for user_trades in trades.values():
            for trade in user_trades:
                trade_date = datetime.fromisoformat(trade['executed_at']).date()
                if trade_date == today:
                    total_trades += 1
        
        return total_trades
    
    def get_daily_volume(self) -> float:
        """Get total trading volume today (admin function)."""
        trades = self._load_json(self.trades_file)
        
        today = datetime.now().date()
        total_volume = 0.0
        
        for user_trades in trades.values():
            for trade in user_trades:
                trade_date = datetime.fromisoformat(trade['executed_at']).date()
                if trade_date == today:
                    total_volume += trade['value']
        
        return total_volume