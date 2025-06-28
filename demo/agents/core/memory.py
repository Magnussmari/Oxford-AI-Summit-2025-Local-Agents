"""
Long-term memory system for agent learning and improvement
"""

import sqlite3
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
import hashlib
from pathlib import Path
from loguru import logger
import numpy as np


@dataclass
class MemoryEntry:
    """Single memory entry"""
    id: str = ""
    agent_name: str = ""
    query: str = ""
    response: str = ""
    prompt: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    execution_time: float = 0.0
    tokens_used: int = 0
    embedding: Optional[List[float]] = None
    
    def __post_init__(self):
        if not self.id:
            # Generate unique ID based on content
            content = f"{self.agent_name}:{self.query}:{self.timestamp.isoformat()}"
            self.id = hashlib.md5(content.encode()).hexdigest()


class AgentMemorySystem:
    """Long-term memory storage and retrieval for agents"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "agent_memory.db")
            
        self.db_path = db_path
        self._init_db()
        self._init_cache()
        
    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    prompt TEXT,
                    metadata TEXT,
                    timestamp REAL NOT NULL,
                    success INTEGER NOT NULL,
                    execution_time REAL,
                    tokens_used INTEGER,
                    embedding TEXT,
                    created_at REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_agent_name ON memories(agent_name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_success ON memories(success)')
            
            # Create performance metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    agent_name TEXT PRIMARY KEY,
                    total_queries INTEGER DEFAULT 0,
                    successful_queries INTEGER DEFAULT 0,
                    total_time REAL DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    last_updated REAL DEFAULT (strftime('%s', 'now'))
                )
            ''')
            
            conn.commit()
            
    def _init_cache(self):
        """Initialize in-memory cache"""
        self.cache = {
            "recent_queries": {},  # Agent -> List of recent queries
            "embeddings": {},      # Query hash -> embedding
            "metrics": {}          # Agent -> metrics
        }
        
    def store_interaction(self, entry: MemoryEntry) -> bool:
        """Store a successful interaction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Store memory
                conn.execute('''
                    INSERT OR REPLACE INTO memories 
                    (id, agent_name, query, response, prompt, metadata, 
                     timestamp, success, execution_time, tokens_used, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    entry.id,
                    entry.agent_name,
                    entry.query,
                    entry.response,
                    entry.prompt,
                    json.dumps(entry.metadata),
                    entry.timestamp.timestamp(),
                    int(entry.success),
                    entry.execution_time,
                    entry.tokens_used,
                    json.dumps(entry.embedding) if entry.embedding else None
                ))
                
                # Update metrics
                conn.execute('''
                    INSERT OR REPLACE INTO agent_metrics 
                    (agent_name, total_queries, successful_queries, total_time, total_tokens)
                    VALUES (
                        ?,
                        COALESCE((SELECT total_queries FROM agent_metrics WHERE agent_name = ?), 0) + 1,
                        COALESCE((SELECT successful_queries FROM agent_metrics WHERE agent_name = ?), 0) + ?,
                        COALESCE((SELECT total_time FROM agent_metrics WHERE agent_name = ?), 0) + ?,
                        COALESCE((SELECT total_tokens FROM agent_metrics WHERE agent_name = ?), 0) + ?
                    )
                ''', (
                    entry.agent_name,
                    entry.agent_name,
                    entry.agent_name, int(entry.success),
                    entry.agent_name, entry.execution_time,
                    entry.agent_name, entry.tokens_used
                ))
                
                conn.commit()
                
                # Update cache
                if entry.agent_name not in self.cache["recent_queries"]:
                    self.cache["recent_queries"][entry.agent_name] = []
                self.cache["recent_queries"][entry.agent_name].append(entry.query)
                
                # Keep only last 100 queries per agent in cache
                if len(self.cache["recent_queries"][entry.agent_name]) > 100:
                    self.cache["recent_queries"][entry.agent_name] = \
                        self.cache["recent_queries"][entry.agent_name][-100:]
                        
                logger.info(f"Stored memory for {entry.agent_name}: {entry.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            return False
            
    def retrieve_similar(self, query: str, agent_name: str = None, 
                        limit: int = 5, min_similarity: float = 0.7) -> List[MemoryEntry]:
        """Retrieve similar past interactions"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Simple keyword-based similarity for now
                # In production, use proper embeddings
                keywords = set(query.lower().split())
                
                base_query = '''
                    SELECT * FROM memories 
                    WHERE success = 1
                '''
                
                params = []
                if agent_name:
                    base_query += ' AND agent_name = ?'
                    params.append(agent_name)
                    
                base_query += ' ORDER BY timestamp DESC LIMIT 100'
                
                cursor = conn.execute(base_query, params)
                
                # Score and filter results
                scored_results = []
                for row in cursor:
                    memory_query = row[2].lower()  # query column
                    memory_keywords = set(memory_query.split())
                    
                    # Calculate Jaccard similarity
                    intersection = len(keywords & memory_keywords)
                    union = len(keywords | memory_keywords)
                    similarity = intersection / union if union > 0 else 0
                    
                    if similarity >= min_similarity:
                        entry = self._row_to_memory_entry(row)
                        scored_results.append((similarity, entry))
                        
                # Sort by similarity and return top results
                scored_results.sort(key=lambda x: x[0], reverse=True)
                return [entry for _, entry in scored_results[:limit]]
                
        except Exception as e:
            logger.error(f"Failed to retrieve similar memories: {e}")
            return []
            
    def get_agent_performance_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Get performance metrics for an agent"""
        try:
            # Check cache first
            if agent_name in self.cache["metrics"]:
                cache_entry = self.cache["metrics"][agent_name]
                if cache_entry["timestamp"] > datetime.now().timestamp() - 300:  # 5 min cache
                    return cache_entry["metrics"]
                    
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT * FROM agent_metrics WHERE agent_name = ?
                ''', (agent_name,))
                
                row = cursor.fetchone()
                if row:
                    metrics = {
                        "total_queries": row[1],
                        "successful_queries": row[2],
                        "success_rate": row[2] / row[1] if row[1] > 0 else 0,
                        "average_time": row[3] / row[1] if row[1] > 0 else 0,
                        "total_tokens": row[4],
                        "average_tokens": row[4] / row[1] if row[1] > 0 else 0
                    }
                else:
                    metrics = {
                        "total_queries": 0,
                        "successful_queries": 0,
                        "success_rate": 1.0,
                        "average_time": 0,
                        "total_tokens": 0,
                        "average_tokens": 0
                    }
                    
                # Get recent performance trends
                cursor = conn.execute('''
                    SELECT success, execution_time, tokens_used, timestamp
                    FROM memories 
                    WHERE agent_name = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 10
                ''', (agent_name,))
                
                recent = cursor.fetchall()
                if recent:
                    recent_success_rate = sum(r[0] for r in recent) / len(recent)
                    recent_avg_time = sum(r[1] for r in recent) / len(recent)
                    
                    metrics["recent_success_rate"] = recent_success_rate
                    metrics["recent_avg_time"] = recent_avg_time
                    metrics["trend"] = "improving" if recent_success_rate > metrics["success_rate"] else "stable"
                    
                # Cache the metrics
                self.cache["metrics"][agent_name] = {
                    "timestamp": datetime.now().timestamp(),
                    "metrics": metrics
                }
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get agent metrics: {e}")
            return {
                "total_queries": 0,
                "success_rate": 1.0,
                "average_time": 0,
                "error": str(e)
            }
            
    def get_successful_patterns(self, agent_name: str, min_occurrences: int = 3) -> List[Dict]:
        """Identify successful patterns for an agent"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Get successful queries
                cursor = conn.execute('''
                    SELECT query, prompt, COUNT(*) as count, AVG(execution_time) as avg_time
                    FROM memories
                    WHERE agent_name = ? AND success = 1
                    GROUP BY query
                    HAVING count >= ?
                    ORDER BY count DESC
                    LIMIT 20
                ''', (agent_name, min_occurrences))
                
                patterns = []
                for row in cursor:
                    patterns.append({
                        "query_pattern": row[0],
                        "prompt_used": row[1],
                        "occurrences": row[2],
                        "avg_execution_time": row[3]
                    })
                    
                return patterns
                
        except Exception as e:
            logger.error(f"Failed to get successful patterns: {e}")
            return []
            
    def cleanup_old_memories(self, days: int = 30):
        """Remove old memories to manage database size"""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).timestamp()
            
            with sqlite3.connect(self.db_path) as conn:
                # Keep recent memories and all successful ones from last 7 days
                conn.execute('''
                    DELETE FROM memories 
                    WHERE timestamp < ? 
                    AND (success = 0 OR timestamp < ?)
                ''', (cutoff, (datetime.now() - timedelta(days=7)).timestamp()))
                
                deleted = conn.total_changes
                conn.commit()
                
                logger.info(f"Cleaned up {deleted} old memories")
                return deleted
                
        except Exception as e:
            logger.error(f"Failed to cleanup memories: {e}")
            return 0
            
    def export_memories(self, agent_name: str = None, format: str = "json") -> str:
        """Export memories for backup or analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = 'SELECT * FROM memories'
                params = []
                
                if agent_name:
                    query += ' WHERE agent_name = ?'
                    params.append(agent_name)
                    
                cursor = conn.execute(query, params)
                
                memories = []
                for row in cursor:
                    entry = self._row_to_memory_entry(row)
                    memories.append(asdict(entry))
                    
                if format == "json":
                    return json.dumps(memories, indent=2, default=str)
                else:
                    # Could add CSV or other formats
                    return json.dumps(memories, indent=2, default=str)
                    
        except Exception as e:
            logger.error(f"Failed to export memories: {e}")
            return "{}"
            
    def _row_to_memory_entry(self, row: Tuple) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        return MemoryEntry(
            id=row[0],
            agent_name=row[1],
            query=row[2],
            response=row[3],
            prompt=row[4] or "",
            metadata=json.loads(row[5]) if row[5] else {},
            timestamp=datetime.fromtimestamp(row[6]),
            success=bool(row[7]),
            execution_time=row[8] or 0.0,
            tokens_used=row[9] or 0,
            embedding=json.loads(row[10]) if row[10] else None
        )
        
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple Jaccard similarity for now
        # In production, use proper embeddings
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0