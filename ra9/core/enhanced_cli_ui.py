#!/usr/bin/env python3
"""
Enhanced CLI UI for RA9 with real-time workflow visualization
Shows typewriter animations, agent status, iterations, performance metrics
"""

import sys
import time
import json
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'

class TypewriterAnimation:
    """Typewriter effect for text output"""
    
    def __init__(self, delay: float = 0.03, color: str = Colors.WHITE):
        self.delay = delay
        self.color = color
        self.active = False
    
    def type_text(self, text: str, prefix: str = "", suffix: str = ""):
        """Type text with animation"""
        if not self.active:
            return text
        
        sys.stdout.write(f"{prefix}{self.color}")
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(self.delay)
        sys.stdout.write(f"{suffix}{Colors.RESET}")
        sys.stdout.flush()
        return text

class ProgressBar:
    """Animated progress bar"""
    
    def __init__(self, width: int = 40):
        self.width = width
        self.current = 0
        self.total = 100
    
    def update(self, current: int, total: int = None):
        """Update progress bar"""
        if total:
            self.total = total
        self.current = current
        
        percent = (current / self.total) * 100
        filled = int((current / self.total) * self.width)
        bar = '█' * filled + '░' * (self.width - filled)
        
        sys.stdout.write(f"\r{Colors.CYAN}[{bar}] {percent:.1f}%{Colors.RESET}")
        sys.stdout.flush()
    
    def complete(self):
        """Mark as complete"""
        self.update(self.total)
        print()

class AgentStatus:
    """Track individual agent status"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.status = "idle"  # idle, working, complete, error
        self.start_time = None
        self.end_time = None
        self.output = ""
        self.confidence = 0.0
    
    def start(self):
        """Mark agent as working"""
        self.status = "working"
        self.start_time = time.time()
    
    def complete(self, output: str, confidence: float = 0.0):
        """Mark agent as complete"""
        self.status = "complete"
        self.end_time = time.time()
        self.output = output
        self.confidence = confidence
    
    def error(self, error_msg: str):
        """Mark agent as error"""
        self.status = "error"
        self.end_time = time.time()
        self.output = error_msg

class EnhancedCLI:
    """Enhanced CLI with full workflow visualization"""
    
    def __init__(self):
        self.typewriter = TypewriterAnimation()
        self.progress = ProgressBar()
        self.agents: Dict[str, AgentStatus] = {}
        self.current_iteration = 0
        self.total_iterations = 1
        self.workflow_stage = "initializing"
        self.performance_metrics = {
            "start_time": None,
            "classification_time": 0,
            "agent_time": 0,
            "total_time": 0,
            "tokens_generated": 0,
            "api_calls": 0
        }
        self.meta_report = {}
        self.memory_entries = []
        
        # Enable typewriter animation by default
        self.typewriter.active = True
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_header(self):
        """Show RA9 header"""
        header = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🧠 RA9 - Enhanced Cognitive Engine v2.0                                     ║
║  Advanced Multi-Agent Reasoning with Real-time Visualization                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
        print(header)
    
    def show_workflow_stage(self, stage: str, details: str = ""):
        """Show current workflow stage"""
        self.workflow_stage = stage
        stage_colors = {
            "initializing": Colors.YELLOW,
            "classifying": Colors.BLUE,
            "memory_fetch": Colors.MAGENTA,
            "parallel_agents": Colors.GREEN,
            "self_critique": Colors.CYAN,
            "meta_coherence": Colors.YELLOW,
            "reflection_loop": Colors.MAGENTA,
            "final_output": Colors.GREEN,
            "autonomy": Colors.BLUE
        }
        
        color = stage_colors.get(stage, Colors.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\n{Colors.DIM}[{timestamp}]{Colors.RESET} {color}🔄 {stage.upper().replace('_', ' ')}{Colors.RESET}")
        if details:
            self.typewriter.type_text(f"   {details}", Colors.DIM)
            print()
    
    def show_classification_result(self, structured_query):
        """Show query classification results"""
        print(f"\n{Colors.BLUE}📊 QUERY CLASSIFICATION{Colors.RESET}")
        print(f"{Colors.WHITE}┌─ Intent: {Colors.GREEN}{structured_query.intent}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Primary Type: {Colors.YELLOW}{structured_query.query_type}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Confidence: {Colors.CYAN}{structured_query.confidence:.2f}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Reasoning Depth: {Colors.MAGENTA}{structured_query.reasoning_depth}{Colors.RESET}")
        
        if structured_query.labels:
            labels_str = ", ".join(structured_query.labels)
            print(f"{Colors.WHITE}└─ Secondary Labels: {Colors.DIM}{labels_str}{Colors.RESET}")
        
        if structured_query.label_confidences:
            print(f"{Colors.WHITE}   Label Confidences:{Colors.RESET}")
            for label, conf in structured_query.label_confidences.items():
                bar = "█" * int(conf * 10) + "░" * (10 - int(conf * 10))
                print(f"{Colors.WHITE}     {label}: {Colors.CYAN}[{bar}] {conf:.2f}{Colors.RESET}")
    
    def show_memory_status(self, memory_type: str, count: int, details: str = ""):
        """Show memory layer status"""
        memory_icons = {
            "episodic": "🧠",
            "semantic": "📚", 
            "reflective": "🪞"
        }
        
        icon = memory_icons.get(memory_type, "💾")
        print(f"\n{Colors.MAGENTA}{icon} MEMORY: {memory_type.upper()}{Colors.RESET}")
        print(f"{Colors.WHITE}   Entries: {Colors.CYAN}{count}{Colors.RESET}")
        if details:
            self.typewriter.type_text(f"   {details}", Colors.DIM)
            print()
    
    def register_agent(self, name: str, role: str):
        """Register a new agent"""
        self.agents[name] = AgentStatus(name, role)
    
    def show_agent_status(self):
        """Show all agent statuses"""
        if not self.agents:
            return
            
        print(f"\n{Colors.GREEN}🤖 AGENT STATUS{Colors.RESET}")
        
        for agent in self.agents.values():
            status_colors = {
                "idle": Colors.DIM,
                "working": Colors.YELLOW,
                "complete": Colors.GREEN,
                "error": Colors.RED
            }
            
            status_icons = {
                "idle": "⏸️",
                "working": "⚡",
                "complete": "✅",
                "error": "❌"
            }
            
            color = status_colors.get(agent.status, Colors.WHITE)
            icon = status_icons.get(agent.status, "❓")
            
            print(f"{Colors.WHITE}┌─ {icon} {agent.name} ({agent.role}){Colors.RESET}")
            print(f"{Colors.WHITE}│   Status: {color}{agent.status.upper()}{Colors.RESET}")
            
            if agent.status == "working" and agent.start_time:
                elapsed = time.time() - agent.start_time
                print(f"{Colors.WHITE}│   Elapsed: {Colors.CYAN}{elapsed:.1f}s{Colors.RESET}")
            
            if agent.status == "complete":
                print(f"{Colors.WHITE}│   Confidence: {Colors.CYAN}{agent.confidence:.2f}{Colors.RESET}")
                if agent.output:
                    preview = agent.output[:100] + "..." if len(agent.output) > 100 else agent.output
                    print(f"{Colors.WHITE}│   Output: {Colors.DIM}{preview}{Colors.RESET}")
            
            print(f"{Colors.WHITE}└─{Colors.RESET}")
    
    def update_agent_status(self, name: str, status: str, output: str = "", confidence: float = 0.0):
        """Update agent status"""
        if name in self.agents:
            if status == "working":
                self.agents[name].start()
            elif status == "complete":
                self.agents[name].complete(output, confidence)
            elif status == "error":
                self.agents[name].error(output)
    
    def show_iteration_progress(self, current: int, total: int, details: str = ""):
        """Show iteration progress"""
        self.current_iteration = current
        self.total_iterations = total
        
        print(f"\n{Colors.CYAN}🔄 ITERATION {current}/{total}{Colors.RESET}")
        if details:
            self.typewriter.type_text(details, Colors.DIM)
            print()
        
        # Show progress bar
        self.progress.update(current, total)
    
    def show_performance_metrics(self):
        """Show performance metrics"""
        if not self.performance_metrics["start_time"]:
            return
            
        total_time = time.time() - self.performance_metrics["start_time"]
        
        print(f"\n{Colors.YELLOW}📈 PERFORMANCE METRICS{Colors.RESET}")
        print(f"{Colors.WHITE}┌─ Total Time: {Colors.CYAN}{total_time:.2f}s{Colors.RESET}")
        print(f"{Colors.WHITE}├─ API Calls: {Colors.CYAN}{self.performance_metrics['api_calls']}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Tokens Generated: {Colors.CYAN}{self.performance_metrics['tokens_generated']}{Colors.RESET}")
        print(f"{Colors.WHITE}└─ Avg Response Time: {Colors.CYAN}{total_time/max(1, self.performance_metrics['api_calls']):.2f}s{Colors.RESET}")
    
    def show_meta_report(self, meta_report: Dict[str, Any]):
        """Show meta-self report"""
        self.meta_report = meta_report
        
        print(f"\n{Colors.MAGENTA}🪞 META-SELF REPORT{Colors.RESET}")
        print(f"{Colors.WHITE}┌─ Activated Agents: {Colors.CYAN}{', '.join(meta_report.get('activated_agents', []))}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Reasoning Rounds: {Colors.CYAN}{meta_report.get('rounds', 0)}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Primary Intent: {Colors.YELLOW}{meta_report.get('primary_intent', 'unknown')}{Colors.RESET}")
        print(f"{Colors.WHITE}├─ Coherence: {Colors.GREEN if meta_report.get('coherence_ok') else Colors.RED}{'✓' if meta_report.get('coherence_ok') else '✗'}{Colors.RESET}")
        print(f"{Colors.WHITE}└─ Confidence: {Colors.CYAN}{meta_report.get('confidence_estimate', 0.0):.2f}{Colors.RESET}")
    
    def show_final_output(self, output: str, reflection: str = ""):
        """Show final output with typewriter effect"""
        print(f"\n{Colors.GREEN}🎯 FINAL OUTPUT{Colors.RESET}")
        print(f"{Colors.WHITE}┌─{Colors.RESET}")
        
        # Type the output with animation
        self.typewriter.type_text(output, f"{Colors.WHITE}│ {Colors.GREEN}")
        print(f"\n{Colors.WHITE}└─{Colors.RESET}")
        
        if reflection:
            print(f"\n{Colors.CYAN}🪞 REFLECTION{Colors.RESET}")
            self.typewriter.type_text(reflection, Colors.DIM)
            print()
    
    def show_memory_write(self, memory_type: str, content: str):
        """Show memory write operation"""
        memory_icons = {
            "episodic": "🧠",
            "semantic": "📚",
            "reflective": "🪞"
        }
        
        icon = memory_icons.get(memory_type, "💾")
        print(f"\n{Colors.BLUE}{icon} WRITING TO {memory_type.upper()} MEMORY{Colors.RESET}")
        
        preview = content[:200] + "..." if len(content) > 200 else content
        self.typewriter.type_text(preview, Colors.DIM)
        print()
    
    def start_session(self):
        """Start a new session"""
        self.clear_screen()
        self.show_header()
        self.performance_metrics["start_time"] = time.time()
        self.workflow_stage = "initializing"
    
    def end_session(self):
        """End the session"""
        print(f"\n{Colors.GREEN}✅ SESSION COMPLETE{Colors.RESET}")
        self.show_performance_metrics()
        print(f"\n{Colors.DIM}Thank you for using RA9 Enhanced CLI{Colors.RESET}\n")

    # --- Realtime Events ---
    def emit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Emit a realtime event line (used by council pipeline)."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        try:
            payload = json.dumps(data, ensure_ascii=False)
        except Exception:
            payload = str(data)
        print(f"{Colors.DIM}[{timestamp}]{Colors.RESET} {Colors.CYAN}{event}{Colors.RESET} {payload}")

# Global CLI instance
cli = EnhancedCLI()

def get_cli() -> EnhancedCLI:
    """Get the global CLI instance"""
    return cli