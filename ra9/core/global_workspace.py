"""
Global Workspace - Thalamo-cortical loops & L5p broadcast analogue
Implements pub/sub system for content routing and broadcasting
"""

from typing import List, Dict, Any, Optional, Callable, Set
from datetime import datetime, timedelta
import threading
import json
from collections import defaultdict, deque

from .schemas import BroadcastItem, AgentType, ActiveRepresentation


class GlobalWorkspace:
    """
    Global Workspace - pub/sub system for content broadcasting
    Analogous to thalamo-cortical loops and L5p broadcasting in the brain
    """
    
    def __init__(self, max_items: int = 1000, item_ttl: int = 3600):
        self.max_items = max_items
        self.item_ttl = item_ttl  # Time to live in seconds
        self.broadcast_items: Dict[str, BroadcastItem] = {}
        self.subscribers: Dict[str, Set[Callable]] = defaultdict(set)
        self.subscription_topics: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.RLock()
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = datetime.now()
    
    def broadcast(self, item: BroadcastItem) -> bool:
        """
        Broadcast an item to the global workspace
        
        Args:
            item: BroadcastItem to broadcast
            
        Returns:
            bool: True if successfully broadcast
        """
        with self.lock:
            # Store the item
            self.broadcast_items[item.id] = item
            
            # Notify subscribers
            self._notify_subscribers(item)
            
            # Cleanup if needed
            self._cleanup_if_needed()
            
            return True
    
    def subscribe(self, subscriber_id: str, callback: Callable[[BroadcastItem], None], 
                  topics: Optional[List[str]] = None) -> bool:
        """
        Subscribe to broadcast items
        
        Args:
            subscriber_id: Unique identifier for subscriber
            callback: Function to call when items are broadcast
            topics: Optional list of topics to filter on
            
        Returns:
            bool: True if successfully subscribed
        """
        with self.lock:
            self.subscribers[subscriber_id].add(callback)
            
            if topics:
                for topic in topics:
                    self.subscription_topics[topic].add(subscriber_id)
            
            return True
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from broadcasts
        
        Args:
            subscriber_id: Subscriber to remove
            
        Returns:
            bool: True if successfully unsubscribed
        """
        with self.lock:
            if subscriber_id in self.subscribers:
                del self.subscribers[subscriber_id]
            
            # Remove from topic subscriptions
            for topic_subscribers in self.subscription_topics.values():
                topic_subscribers.discard(subscriber_id)
            
            return True
    
    def get_item(self, item_id: str) -> Optional[BroadcastItem]:
        """Get a specific broadcast item by ID"""
        with self.lock:
            return self.broadcast_items.get(item_id)
    
    def get_items_by_agent(self, agent: AgentType) -> List[BroadcastItem]:
        """Get all items contributed by a specific agent"""
        with self.lock:
            return [item for item in self.broadcast_items.values() 
                   if agent in item.contributors]
    
    def get_items_by_confidence(self, min_confidence: float) -> List[BroadcastItem]:
        """Get all items above a confidence threshold"""
        with self.lock:
            return [item for item in self.broadcast_items.values() 
                   if item.confidence >= min_confidence]
    
    def get_recent_items(self, minutes: int = 10) -> List[BroadcastItem]:
        """Get items from the last N minutes"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        with self.lock:
            return [item for item in self.broadcast_items.values() 
                   if item.timestamp >= cutoff_time]
    
    def search_items(self, query: str, max_results: int = 10) -> List[BroadcastItem]:
        """
        Search items by text content
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of matching BroadcastItems
        """
        query_lower = query.lower()
        matches = []
        
        with self.lock:
            for item in self.broadcast_items.values():
                if query_lower in item.text.lower():
                    matches.append(item)
            
            # Sort by confidence and timestamp
            matches.sort(key=lambda x: (x.confidence, x.timestamp), reverse=True)
            
            return matches[:max_results]
    
    def _notify_subscribers(self, item: BroadcastItem) -> None:
        """Notify all relevant subscribers about a new item"""
        # Get all subscribers
        all_subscribers = set()
        for subscribers in self.subscribers.values():
            all_subscribers.update(subscribers)
        
        # Filter by topics if applicable
        topic_subscribers = set()
        for topic, subscribers in self.subscription_topics.items():
            if topic in item.text.lower() or topic in [agent.value for agent in item.contributors]:
                topic_subscribers.update(subscribers)
        
        # Combine all subscribers
        target_subscribers = all_subscribers.union(topic_subscribers)
        
        # Notify subscribers
        for callback in target_subscribers:
            try:
                callback(item)
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def _cleanup_if_needed(self) -> None:
        """Clean up old items if needed"""
        now = datetime.now()
        if (now - self.last_cleanup).seconds < self.cleanup_interval:
            return
        
        self.last_cleanup = now
        cutoff_time = now - timedelta(seconds=self.item_ttl)
        
        # Remove old items
        old_items = [item_id for item_id, item in self.broadcast_items.items() 
                    if item.timestamp < cutoff_time]
        
        for item_id in old_items:
            del self.broadcast_items[item_id]
        
        # Remove excess items if over limit
        if len(self.broadcast_items) > self.max_items:
            # Sort by timestamp and remove oldest
            sorted_items = sorted(self.broadcast_items.items(), 
                                key=lambda x: x[1].timestamp)
            
            excess_count = len(self.broadcast_items) - self.max_items
            for i in range(excess_count):
                item_id, _ = sorted_items[i]
                del self.broadcast_items[item_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get workspace statistics"""
        with self.lock:
            return {
                'total_items': len(self.broadcast_items),
                'total_subscribers': len(self.subscribers),
                'topics': list(self.subscription_topics.keys()),
                'oldest_item': min(item.timestamp for item in self.broadcast_items.values()) 
                              if self.broadcast_items else None,
                'newest_item': max(item.timestamp for item in self.broadcast_items.values()) 
                              if self.broadcast_items else None
            }


class WorkingMemory:
    """
    Executive & Working Memory - maintains active representations
    Analogous to prefrontal cortex working memory in the brain
    """
    
    def __init__(self, max_slots: int = 7):
        self.max_slots = max_slots  # Miller's rule: 7±2 items
        self.active_slots: List[ActiveRepresentation] = []
        self.lock = threading.RLock()
        self.decay_rate = 0.1  # Decay per minute
        self.last_decay = datetime.now()
    
    def add_representation(self, content: str, source_agents: List[AgentType], 
                          priority: float = 0.5, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a new active representation
        
        Args:
            content: Content to store
            source_agents: Agents that contributed
            priority: Priority level (0.0 to 1.0)
            metadata: Additional metadata
            
        Returns:
            bool: True if successfully added
        """
        with self.lock:
            # Apply decay to existing items
            self._apply_decay()
            
            # Create new representation
            representation = ActiveRepresentation(
                content=content,
                source_agents=source_agents,
                priority=priority,
                metadata=metadata or {}
            )
            
            # Add to slots
            self.active_slots.append(representation)
            
            # Maintain max slots limit
            if len(self.active_slots) > self.max_slots:
                # Remove lowest priority item
                self.active_slots.sort(key=lambda x: (x.priority, x.decay), reverse=True)
                self.active_slots = self.active_slots[:self.max_slots]
            
            return True
    
    def get_representations(self, min_priority: float = 0.0) -> List[ActiveRepresentation]:
        """Get active representations above priority threshold"""
        with self.lock:
            self._apply_decay()
            return [rep for rep in self.active_slots if rep.priority >= min_priority]
    
    def get_by_agent(self, agent: AgentType) -> List[ActiveRepresentation]:
        """Get representations contributed by specific agent"""
        with self.lock:
            self._apply_decay()
            return [rep for rep in self.active_slots if agent in rep.source_agents]
    
    def update_priority(self, content: str, new_priority: float) -> bool:
        """Update priority of a representation"""
        with self.lock:
            for rep in self.active_slots:
                if rep.content == content:
                    rep.priority = new_priority
                    return True
            return False
    
    def remove_representation(self, content: str) -> bool:
        """Remove a representation by content"""
        with self.lock:
            for i, rep in enumerate(self.active_slots):
                if rep.content == content:
                    del self.active_slots[i]
                    return True
            return False
    
    def clear(self) -> None:
        """Clear all representations"""
        with self.lock:
            self.active_slots.clear()
    
    def _apply_decay(self) -> None:
        """Apply decay to all representations"""
        now = datetime.now()
        time_since_last_decay = (now - self.last_decay).total_seconds() / 60.0  # minutes
        
        if time_since_last_decay > 0:
            for rep in self.active_slots:
                rep.decay *= (1.0 - self.decay_rate * time_since_last_decay)
                rep.decay = max(0.0, rep.decay)  # Don't go below 0
            
            # Remove fully decayed items
            self.active_slots = [rep for rep in self.active_slots if rep.decay > 0.01]
            
            self.last_decay = now
    
    def get_stats(self) -> Dict[str, Any]:
        """Get working memory statistics"""
        with self.lock:
            self._apply_decay()
            return {
                'active_slots': len(self.active_slots),
                'max_slots': self.max_slots,
                'avg_priority': sum(rep.priority for rep in self.active_slots) / max(1, len(self.active_slots)),
                'avg_decay': sum(rep.decay for rep in self.active_slots) / max(1, len(self.active_slots)),
                'agents_represented': len(set(agent for rep in self.active_slots for agent in rep.source_agents))
            }


class GlobalWorkspaceManager:
    """Manager for Global Workspace and Working Memory coordination"""
    
    def __init__(self, max_broadcast_items: int = 1000, max_working_memory_slots: int = 7):
        self.global_workspace = GlobalWorkspace(max_broadcast_items)
        self.working_memory = WorkingMemory(max_working_memory_slots)
        self.coordination_lock = threading.RLock()
    
    def broadcast_and_store(self, item: BroadcastItem, store_in_wm: bool = True) -> bool:
        """
        Broadcast item and optionally store in working memory
        
        Args:
            item: Item to broadcast
            store_in_wm: Whether to also store in working memory
            
        Returns:
            bool: True if successful
        """
        with self.coordination_lock:
            # Broadcast to global workspace
            success = self.global_workspace.broadcast(item)
            
            if success and store_in_wm:
                # Store in working memory
                self.working_memory.add_representation(
                    content=item.text,
                    source_agents=item.contributors,
                    priority=item.confidence,
                    metadata={'broadcast_id': item.id, 'speculative': item.speculative}
                )
            
            return success
    
    def get_coordinated_view(self) -> Dict[str, Any]:
        """Get coordinated view of both systems"""
        with self.coordination_lock:
            return {
                'global_workspace': self.global_workspace.get_stats(),
                'working_memory': self.working_memory.get_stats(),
                'coordination_status': 'active'
            }
