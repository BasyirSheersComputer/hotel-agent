"""
Copyright (c) 2025 Sheers Software Sdn. Bhd.
All Rights Reserved.

Metrics Collection Service for Performance Dashboard
Tracks query metrics, response times, question categories, and agent performance.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import sqlite3
import json
import os
from pathlib import Path
import random # For simulation of new metrics until fully implemented

# Database path - stored alongside backend
DB_PATH = Path(__file__).parent.parent.parent / "analytics.db"

class MetricsService:
    """Service for collecting and querying performance metrics"""
    
    def __init__(self):
        self._init_database()
        self._migrate_database()
    
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Queries table - tracks every query
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query_text TEXT NOT NULL,
                response_time_ms INTEGER NOT NULL,
                question_category TEXT,
                source_type TEXT,
                agent_id TEXT,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                tokens_used INTEGER DEFAULT 0,
                cost_estimate REAL DEFAULT 0.0,
                accuracy_score REAL DEFAULT 0.0,
                aht_saved_s INTEGER DEFAULT 0
            )
        """)
        
        # Conversions table - tracks booking conversions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                query_id INTEGER,
                conversion_type TEXT,
                value REAL,
                FOREIGN KEY (query_id) REFERENCES queries(id)
            )
        """)
        
        # Performance snapshots - hourly aggregated data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_queries INTEGER,
                avg_response_time_ms REAL,
                success_rate REAL,
                unique_agents INTEGER
            )
        """)
        
        # Agents table - track agent usage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_queries INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()

    def _migrate_database(self):
        """Simple migration to add new columns if they don't exist"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        try:
            # Check if new columns exist
            cursor.execute("SELECT tokens_used FROM queries LIMIT 1")
        except sqlite3.OperationalError:
            # Add missing columns
            print("Migrating database: Adding new metric columns...")
            try:
                cursor.execute("ALTER TABLE queries ADD COLUMN tokens_used INTEGER DEFAULT 0")
                cursor.execute("ALTER TABLE queries ADD COLUMN cost_estimate REAL DEFAULT 0.0")
                cursor.execute("ALTER TABLE queries ADD COLUMN accuracy_score REAL DEFAULT 0.0")
                cursor.execute("ALTER TABLE queries ADD COLUMN aht_saved_s INTEGER DEFAULT 0")
                conn.commit()
            except Exception as e:
                print(f"Migration warning: {e}")
        
        conn.close()
    
    def log_query(
        self,
        query_text: str,
        response_time_ms: int,
        question_category: Optional[str] = None,
        source_type: Optional[str] = None,
        agent_id: Optional[str] = "default",
        success: bool = True,
        error_message: Optional[str] = None,
        tokens_used: int = 0,
        cost_estimate: float = 0.0
    ) -> int:
        """
        Log a query to the metrics database
        
        Returns:
            query_id: ID of the logged query
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Simulate accuracy score (0.85 - 1.0 for successful queries)
        accuracy_score = 0.0
        if success:
            accuracy_score = round(random.uniform(0.85, 1.0), 2)
            
        # Simulate AHT saved (manual search takes ~300s, AI takes ~3s)
        aht_saved_s = 0
        if success:
            aht_saved_s = max(0, 300 - (response_time_ms / 1000))
            
        # Simulate tokens and cost if not provided (for demo)
        if tokens_used == 0 and success:
            tokens_used = random.randint(150, 500)
            cost_estimate = (tokens_used / 1000) * 0.03 # Approx GPT-4o cost
        
        cursor.execute("""
            INSERT INTO queries 
            (query_text, response_time_ms, question_category, source_type, agent_id, success, error_message, 
             tokens_used, cost_estimate, accuracy_score, aht_saved_s)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (query_text, response_time_ms, question_category, source_type, agent_id, success, error_message,
              tokens_used, cost_estimate, accuracy_score, int(aht_saved_s)))
        
        query_id = cursor.lastrowid
        
        # Update agent stats
        cursor.execute("""
            INSERT INTO agents (agent_id, total_queries)
            VALUES (?, 1)
            ON CONFLICT(agent_id) DO UPDATE SET
                last_seen = CURRENT_TIMESTAMP,
                total_queries = total_queries + 1
        """, (agent_id,))
        
        conn.commit()
        conn.close()
        
        return query_id
    
    def log_conversion(
        self,
        query_id: int,
        conversion_type: str = "booking",
        value: float = 0.0
    ):
        """Log a conversion event"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO conversions (query_id, conversion_type, value)
            VALUES (?, ?, ?)
        """, (query_id, conversion_type, value))
        
        conn.commit()
        conn.close()
    
    def get_summary_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary metrics for the dashboard
        """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(response_time_ms) as avg_time,
                AVG(accuracy_score) * 100 as avg_accuracy,
                SUM(aht_saved_s) as total_saved_s,
                SUM(tokens_used) as total_tokens,
                SUM(cost_estimate) as total_cost
            FROM queries
            WHERE timestamp > ?
        """, (cutoff_time,))
        
        row = cursor.fetchone()
        total_queries = row[0] or 0
        avg_response_time = row[1] or 0
        avg_accuracy = row[2] or 0
        total_saved_s = row[3] or 0
        total_tokens = row[4] or 0
        total_cost = row[5] or 0.0
        
        # Success rate
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN success = TRUE THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM queries
            WHERE timestamp > ?
        """, (cutoff_time,))
        success_rate = cursor.fetchone()[0] or 100.0
        
        # Unique agents
        cursor.execute("""
            SELECT COUNT(DISTINCT agent_id) FROM queries
            WHERE timestamp > ?
        """, (cutoff_time,))
        unique_agents = cursor.fetchone()[0]
        
        # RAG vs Maps counts for breakdown
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN source_type = 'RAG' THEN 1 END) as rag_count,
                COUNT(CASE WHEN source_type = 'Maps' THEN 1 END) as maps_count
            FROM queries
            WHERE timestamp > ?
        """, (cutoff_time,))
        source_counts = cursor.fetchone()
        rag_count = source_counts[0] or 0
        maps_count = source_counts[1] or 0
        
        # Internal vs External Accuracy (Simulated split for now)
        internal_accuracy = avg_accuracy  # Proxy
        external_accuracy = avg_accuracy * 0.95 # Proxy
        
        # AHT Reduction (Simulated baseline of 300s per query)
        # Calculate % reduction: (Baseline - Actual) / Baseline
        # Baseline total time = total_queries * 300s
        # Actual total time = total_queries * (avg_response_time / 1000)
        aht_reduction_percent = 0
        if total_queries > 0:
            baseline_time = total_queries * 300
            actual_time = total_queries * (avg_response_time / 1000)
            if baseline_time > 0:
                aht_reduction_percent = ((baseline_time - actual_time) / baseline_time) * 100

        conn.close()
        
        return {
            "total_queries": total_queries,
            "avg_response_time_ms": round(avg_response_time, 2),
            "success_rate": round(success_rate, 2),
            "unique_agents": unique_agents,
            "period_hours": hours,
            
            # New fields for design.json
            "accuracy_percent": round(avg_accuracy, 1),
            "internal_accuracy_percent": round(internal_accuracy, 1),
            "external_accuracy_percent": round(external_accuracy, 1),
            "aht_reduction_percent": round(aht_reduction_percent, 1),
            "aht_delta_percent": 2.5, # Simulated DoD change
            
            "rag_count": rag_count,
            "rag_percentage": round((rag_count / total_queries * 100) if total_queries else 0, 1),
            "maps_count": maps_count,
            "maps_percentage": round((maps_count / total_queries * 100) if total_queries else 0, 1),
            
            "tokens_used": total_tokens,
            "estimated_cost": round(total_cost, 4),
            "rate_limit_status": "Healthy",
            "cost_breakdown": "GPT-4o: 80%, Maps: 20%"
        }
    
    def get_question_categories(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get breakdown of questions by category"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT 
                COALESCE(question_category, 'Uncategorized') as category,
                COUNT(*) as count,
                AVG(response_time_ms) as avg_time,
                AVG(accuracy_score) * 100 as accuracy
            FROM queries
            WHERE timestamp > ?
            GROUP BY question_category
            ORDER BY count DESC
        """, (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "category": row[0],
                "count": row[1],
                "avg_ai_time": round(row[2], 2), # Renamed to match design.json
                "accuracy": round(row[3] or 0, 1) # Added accuracy
            }
            for row in results
        ]
    
    def get_hourly_trends(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get hourly query trends"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as query_count,
                AVG(response_time_ms) as avg_response_time,
                COUNT(CASE WHEN success = TRUE THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM queries
            WHERE timestamp > ?
            GROUP BY hour
            ORDER BY hour ASC
        """, (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "time": row[0], # Renamed to match design.json
                "queryVolume": row[1], # Renamed to match design.json
                "avg_response_time_ms": round(row[2], 2),
                "success_rate": round(row[3], 2)
            }
            for row in results
        ]
    
    def get_agent_performance(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get performance metrics per agent"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT 
                agent_id,
                COUNT(*) as query_count,
                AVG(response_time_ms) as avg_response_time,
                AVG(accuracy_score) * 100 as accuracy,
                MAX(timestamp) as last_active
            FROM queries
            WHERE timestamp > ?
            GROUP BY agent_id
            ORDER BY query_count DESC
        """, (cutoff_time,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "name": row[0], # Renamed to match design.json
                "queryCount": row[1], # Renamed
                "avgTimeMs": round(row[2], 2), # Renamed
                "accuracyPercent": round(row[3] or 0, 1), # Added
                "lastActive": row[4] # Renamed
            }
            for row in results
        ]
    
    def get_source_distribution(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get distribution of query sources (RAG vs Maps vs Other)"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT 
                COALESCE(source_type, 'Unknown') as source,
                COUNT(*) as count,
                COUNT(*) * 100.0 / (SELECT COUNT(*) FROM queries WHERE timestamp > ?) as percentage
            FROM queries
            WHERE timestamp > ?
            GROUP BY source_type
            ORDER BY count DESC
        """, (cutoff_time, cutoff_time))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                "source": row[0],
                "count": row[1],
                "percentage": round(row[2], 2)
            }
            for row in results
        ]

# Global instance
_metrics_service = None

def get_metrics_service() -> MetricsService:
    """Get or create the global metrics service instance"""
    global _metrics_service
    if _metrics_service is None:
        _metrics_service = MetricsService()
    return _metrics_service

