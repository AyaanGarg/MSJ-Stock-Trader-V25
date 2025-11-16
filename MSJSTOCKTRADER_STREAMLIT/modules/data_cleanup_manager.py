import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
import csv
from io import StringIO

class DataCleanupManager:
    """Manages automatic data cleanup after 6 months while preserving user accounts."""
    
    def __init__(self):
        self.trades_file = "data/trades.json"
        self.positions_file = "data/positions.json"
        self.portfolios_file = "data/portfolios.json"
        self.archive_dir = "data/archives"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create necessary directories."""
        os.makedirs("data", exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
    
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
    
    def get_data_older_than(self, months: int = 6) -> Dict:
        """Identify data older than specified months."""
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        trades = self._load_json(self.trades_file)
        old_trades = {}
        
        for user_id, user_trades in trades.items():
            old_user_trades = []
            for trade in user_trades:
                trade_date = datetime.fromisoformat(trade['executed_at'])
                if trade_date < cutoff_date:
                    old_user_trades.append(trade)
            
            if old_user_trades:
                old_trades[user_id] = old_user_trades
        
        return {
            "cutoff_date": cutoff_date.isoformat(),
            "trades_to_delete": old_trades,
            "total_trades": sum(len(t) for t in old_trades.values()),
            "affected_users": len(old_trades)
        }
    
    def archive_old_data(self, season_id: str) -> Dict:
        """Archive old data before deletion."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_file = os.path.join(self.archive_dir, f"season_{season_id}_{timestamp}.json")
        
        old_data = self.get_data_older_than(6)
        
        archive_data = {
            "season_id": season_id,
            "archived_at": datetime.now().isoformat(),
            "cutoff_date": old_data["cutoff_date"],
            "trades": old_data["trades_to_delete"],
            "total_trades": old_data["total_trades"],
            "affected_users": old_data["affected_users"]
        }
        
        self._save_json(archive_file, archive_data)
        
        return {
            "success": True,
            "archive_file": archive_file,
            "stats": {
                "total_trades": old_data["total_trades"],
                "affected_users": old_data["affected_users"]
            }
        }
    
    def delete_old_trades(self, months: int = 6) -> Dict:
        """Delete trades older than specified months."""
        cutoff_date = datetime.now() - timedelta(days=months * 30)
        
        trades = self._load_json(self.trades_file)
        deleted_count = 0
        
        for user_id in trades:
            original_count = len(trades[user_id])
            trades[user_id] = [
                trade for trade in trades[user_id]
                if datetime.fromisoformat(trade['executed_at']) >= cutoff_date
            ]
            deleted_count += original_count - len(trades[user_id])
        
        self._save_json(self.trades_file, trades)
        
        return {
            "success": True,
            "deleted_trades": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    def export_user_data(self, user_id: str, format: str = "csv") -> Dict:
        """Export all user trading data for download."""
        trades = self._load_json(self.trades_file)
        portfolios = self._load_json(self.portfolios_file)
        positions = self._load_json(self.positions_file)
        
        user_trades = trades.get(user_id, [])
        user_portfolio = portfolios.get(user_id, {})
        user_positions = positions.get(user_id, {})
        
        if format == "csv":
            return self._export_as_csv(user_id, user_trades, user_portfolio, user_positions)
        else:
            return self._export_as_json(user_id, user_trades, user_portfolio, user_positions)
    
    def _export_as_csv(self, user_id: str, trades: List, portfolio: Dict, positions: Dict) -> Dict:
        """Export data as CSV format."""
        # Create CSV for trades
        output = StringIO()
        
        fieldnames = ['trade_id', 'symbol', 'side', 'quantity', 'price', 'value', 'order_type', 'executed_at']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        if trades:
            for trade in trades:
                writer.writerow({
                    'trade_id': trade.get('trade_id', ''),
                    'symbol': trade.get('symbol', ''),
                    'side': trade.get('side', ''),
                    'quantity': trade.get('quantity', 0),
                    'price': trade.get('price', 0),
                    'value': trade.get('value', 0),
                    'order_type': trade.get('order_type', ''),
                    'executed_at': trade.get('executed_at', '')
                })
        else:
            # If no trades, add a row with metadata
            writer.writerow({
                'trade_id': 'NO_TRADES',
                'symbol': f'User: {user_id}',
                'side': f'Export Date: {datetime.now().strftime("%Y-%m-%d")}',
                'quantity': f'Cash: ${portfolio.get("cash_balance", 0):,.2f}',
                'price': 0,
                'value': 0,
                'order_type': f'Positions: {len(positions)}',
                'executed_at': ''
            })
        
        csv_data = output.getvalue()
        output.close()
        
        return {
            "success": True,
            "format": "csv",
            "data": csv_data,
            "filename": f"trades_{user_id}_{datetime.now().strftime('%Y%m%d')}.csv",
            "total_trades": len(trades),
            "summary": {
                "user_id": user_id,
                "export_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "cash_balance": portfolio.get('cash_balance', 0),
                "total_trades": len(trades),
                "active_positions": len(positions)
            }
        }
    
    def _export_as_json(self, user_id: str, trades: List, portfolio: Dict, positions: Dict) -> Dict:
        """Export data as JSON format."""
        export_data = {
            "user_id": user_id,
            "export_date": datetime.now().isoformat(),
            "portfolio": portfolio,
            "positions": positions,
            "trades": trades,
            "summary": {
                "cash_balance": portfolio.get('cash_balance', 0),
                "total_trades": len(trades),
                "active_positions": len(positions)
            }
        }
        
        return {
            "success": True,
            "format": "json",
            "data": json.dumps(export_data, indent=2),
            "filename": f"trading_data_{user_id}_{datetime.now().strftime('%Y%m%d')}.json",
            "total_trades": len(trades)
        }
    
    def liquidate_all_positions(self, user_id: str) -> Dict:
        """Liquidate all user positions (convert to cash)."""
        from modules.market_data import MarketData
        
        positions = self._load_json(self.positions_file)
        portfolios = self._load_json(self.portfolios_file)
        
        user_positions = positions.get(user_id, {})
        
        if not user_positions:
            return {
                "success": True,
                "message": "No positions to liquidate",
                "total_value": 0
            }
        
        market_data = MarketData()
        total_value = 0
        
        # Calculate total value of all positions
        for symbol, position in user_positions.items():
            try:
                current_price = market_data.get_current_price(symbol)
                quantity = position.get('quantity', 0)
                position_value = current_price * quantity
                total_value += position_value
            except:
                # If can't get price, use avg_cost
                total_value += position.get('avg_cost', 0) * position.get('quantity', 0)
        
        # Clear positions
        positions[user_id] = {}
        
        # Add value to cash balance
        if user_id in portfolios:
            portfolios[user_id]['cash_balance'] = portfolios[user_id].get('cash_balance', 0) + total_value
            portfolios[user_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_json(self.positions_file, positions)
        self._save_json(self.portfolios_file, portfolios)
        
        return {
            "success": True,
            "message": f"All positions liquidated. ${total_value:,.2f} added to cash balance.",
            "total_value": total_value,
            "positions_liquidated": len(user_positions)
        }
    
    def reset_user_to_starting_cash(self, user_id: str, starting_cash: float = 100000.0) -> Dict:
        """Reset user's cash balance to starting amount and clear positions."""
        portfolios = self._load_json(self.portfolios_file)
        positions = self._load_json(self.positions_file)
        
        # Clear positions
        positions[user_id] = {}
        
        # Reset cash balance
        if user_id in portfolios:
            portfolios[user_id]['cash_balance'] = starting_cash
            portfolios[user_id]['last_updated'] = datetime.now().isoformat()
        else:
            portfolios[user_id] = {
                'cash_balance': starting_cash,
                'created_at': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat()
            }
        
        self._save_json(self.positions_file, positions)
        self._save_json(self.portfolios_file, portfolios)
        
        return {
            "success": True,
            "message": f"Portfolio reset to ${starting_cash:,.2f}",
            "cash_balance": starting_cash
        }
    
    def reset_all_users(self, exclude_demo: bool = True) -> Dict:
        """Reset all users to starting cash (for competition reset)."""
        from modules.auth_manager import AuthManager
        
        auth_manager = AuthManager()
        all_users = auth_manager._load_users()
        
        reset_count = 0
        skipped = []
        
        for username, user_data in all_users.items():
            user_id = user_data.get('user_id')
            
            # Skip demo user if requested
            if exclude_demo and username == 'demo':
                skipped.append(username)
                continue
            
            # Liquidate and reset
            self.liquidate_all_positions(user_id)
            self.reset_user_to_starting_cash(user_id)
            reset_count += 1
        
        return {
            "success": True,
            "message": f"Reset {reset_count} user portfolios",
            "reset_count": reset_count,
            "skipped": skipped
        }
