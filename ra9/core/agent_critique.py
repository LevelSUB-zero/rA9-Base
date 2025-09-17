"""
Agent Mini-Critique - Self-evaluation and refinement system
Implements immediate self-critique for agent outputs
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

from .schemas import AgentOutput, AgentCritique, AgentType
from .config import CRITIC_MAX_ALLOWED_ISSUES
from ..tools.tool_api import ask_gemini


class AgentCritic:
    """Base class for agent critics"""
    
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        self.critique_template = self._get_critique_template()
        self.rewrite_template = self._get_rewrite_template()
    
    def critique(self, agent_output: AgentOutput) -> AgentCritique:
        """
        Critique an agent output
        
        Args:
            agent_output: AgentOutput to critique
            
        Returns:
            AgentCritique with issues and suggestions
        """
        # Try structured JSON critic first
        issues, suggested_edits, passed_flag = self._run_structured_critic(agent_output)
        if issues is None:
            # Fallback to legacy prompt and parse
            prompt = self._build_critique_prompt(agent_output)
            critique_response = ask_gemini(prompt)
            issues, suggested_edits = self._parse_critique_response(critique_response)
            passed_flag = len(issues) == 0 or all('minor' in issue.lower() for issue in issues)
        
        # Determine if critique passed
        passed = len(issues) == 0 or all('minor' in issue.lower() for issue in issues)
        
        # Calculate confidence impact
        confidence_impact = self._calculate_confidence_impact(issues, suggested_edits)
        
        return AgentCritique(
            agent=self.agent_type,
            passed=passed,
            issues=issues,
            suggested_edits=suggested_edits,
            confidence_impact=confidence_impact,
            timestamp=datetime.now()
        )
    
    def rewrite(self, agent_output: AgentOutput, critique: AgentCritique) -> AgentOutput:
        """
        Rewrite agent output based on critique
        
        Args:
            agent_output: Original agent output
            critique: Critique with suggestions
            
        Returns:
            Rewritten AgentOutput
        """
        if critique.passed:
            return agent_output  # No rewrite needed
        
        # Build rewrite prompt
        prompt = self._build_rewrite_prompt(agent_output, critique)
        
        # Get rewritten response
        rewritten_response = ask_gemini(prompt)
        
        # Extract new reasoning trace
        new_reasoning_trace = self._extract_reasoning_trace(rewritten_response)
        
        # Calculate new confidence (usually higher after rewrite)
        new_confidence = min(1.0, agent_output.confidence + 0.1)
        
        # Create rewritten output
        rewritten_output = AgentOutput(
            agent=agent_output.agent,
            text_draft=rewritten_response,
            reasoning_trace=new_reasoning_trace,
            confidence=new_confidence,
            citations=agent_output.citations,
            memory_hits=agent_output.memory_hits,
            iteration=agent_output.iteration + 1,
            timestamp=datetime.now()
        )
        
        return rewritten_output
    
    def _get_critique_template(self) -> str:
        """Get the critique template for this agent type"""
        return f"""
You are a quality control expert for {self.agent_type.value} reasoning. Your job is to critique the following output for quality issues.

Critique the output for:
1. Contradictions or inconsistencies
2. Vague or unclear statements
3. Missing evidence or reasoning
4. Logical fallacies or errors
5. Inappropriate tone or style
6. Missing important considerations
7. Overconfidence or underconfidence

For each issue found, provide:
- Specific description of the problem
- Why it's problematic
- Suggested improvement

If no significant issues are found, respond with "No significant issues found."

Output format:
ISSUES:
- [Issue 1]: [Description] - [Suggestion]
- [Issue 2]: [Description] - [Suggestion]

SUGGESTED_EDITS:
- [Edit 1]
- [Edit 2]
"""

    def _build_structured_critic_prompt(self, agent_output: AgentOutput) -> str:
        """Prompt for LLM-based structured critic returning JSON."""
        return f"""
You are an automated critic. Input: AGENT_OUTPUT (JSON) and CONTEXT.
Return JSON strictly in this schema:
{{ "pass": true|false, "issues": ["short reason"], "suggested_edits": ["exact sentences to remove/replace or rewrite instructions"] }}
Focus on: unsupported factual claims, inconsistency between reasoning trace and conclusion, overconfident language, format compliance.

AGENT_OUTPUT:
{{
  "agent": "{agent_output.agent.value}",
  "textDraft": {json.dumps(agent_output.text_draft)},
  "reasoningTrace": {json.dumps(agent_output.reasoning_trace)},
  "confidence": {agent_output.confidence:.2f}
}}
"""

    def _run_structured_critic(self, agent_output: AgentOutput) -> Tuple[Optional[List[str]], Optional[List[str]], Optional[bool]]:
        """Execute structured critic; return (issues, suggested_edits, pass). None issues -> fallback."""
        try:
            prompt = self._build_structured_critic_prompt(agent_output)
            response = ask_gemini(prompt)
            data = json.loads(response)
            if not isinstance(data, dict):
                return None, None, None
            issues = data.get('issues', []) or []
            suggested = data.get('suggested_edits', []) or []
            passed_flag = bool(data.get('pass', False))
            return issues, suggested, passed_flag
        except Exception:
            return None, None, None
    
    def _get_rewrite_template(self) -> str:
        """Get the rewrite template for this agent type"""
        return f"""
You are a {self.agent_type.value} reasoning expert. Rewrite the following output to address the critique issues while maintaining the core message and improving quality.

Focus on:
- Addressing all identified issues
- Maintaining the original intent
- Improving clarity and precision
- Strengthening evidence and reasoning
- Ensuring appropriate tone and style

Provide a complete, improved version of the response.
"""
    
    def _build_critique_prompt(self, agent_output: AgentOutput) -> str:
        """Build the critique prompt"""
        return f"""
{self.critique_template}

AGENT OUTPUT TO CRITIQUE:
Agent: {agent_output.agent.value}
Confidence: {agent_output.confidence:.2f}
Response: {agent_output.text_draft}

Reasoning Trace:
{chr(10).join(f"- {step}" for step in agent_output.reasoning_trace)}

Citations: {len(agent_output.citations)}
Memory Hits: {len(agent_output.memory_hits)}

Please provide your critique:
"""
    
    def _build_rewrite_prompt(self, agent_output: AgentOutput, critique: AgentCritique) -> str:
        """Build the rewrite prompt"""
        return f"""
{self.rewrite_template}

ORIGINAL OUTPUT:
{agent_output.text_draft}

CRITIQUE ISSUES:
{chr(10).join(f"- {issue}" for issue in critique.issues)}

SUGGESTED EDITS:
{chr(10).join(f"- {edit}" for edit in critique.suggested_edits)}

Please provide the improved version:
"""
    
    def _parse_critique_response(self, response: str) -> Tuple[List[str], List[str]]:
        """Parse critique response to extract issues and edits"""
        issues = []
        suggested_edits = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.upper().startswith('ISSUES:'):
                current_section = 'issues'
                continue
            elif line.upper().startswith('SUGGESTED_EDITS:'):
                current_section = 'edits'
                continue
            elif line.startswith('- '):
                content = line[2:].strip()
                if current_section == 'issues' and content:
                    issues.append(content)
                elif current_section == 'edits' and content:
                    suggested_edits.append(content)
        
        # If no structured response, look for general issues
        if not issues and not suggested_edits:
            if 'no significant issues' not in response.lower():
                # Try to extract issues from unstructured response
                sentences = response.split('.')
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in ['issue', 'problem', 'concern', 'error']):
                        issues.append(sentence.strip())
        
        return issues, suggested_edits
    
    def _extract_reasoning_trace(self, response: str) -> List[str]:
        """Extract reasoning trace from response"""
        lines = response.split('\n')
        reasoning_steps = []
        
        for line in lines:
            line = line.strip()
            if (line.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                line.startswith(('-', '*', '•')) or
                'step' in line.lower() or
                'reasoning' in line.lower()):
                reasoning_steps.append(line)
        
        # If no explicit steps found, split by sentences
        if not reasoning_steps:
            sentences = response.split('.')
            reasoning_steps = [s.strip() + '.' for s in sentences if s.strip()][:5]
        
        return reasoning_steps[:5]
    
    def _calculate_confidence_impact(self, issues: List[str], suggested_edits: List[str]) -> float:
        """Calculate the impact on confidence from critique"""
        if not issues:
            return 0.0  # No impact
        
        # Count severity of issues
        high_severity_keywords = ['error', 'contradiction', 'inconsistent', 'wrong', 'incorrect']
        medium_severity_keywords = ['unclear', 'vague', 'missing', 'incomplete']
        low_severity_keywords = ['minor', 'suggestion', 'improvement']
        
        high_severity_count = sum(1 for issue in issues 
                                if any(keyword in issue.lower() for keyword in high_severity_keywords))
        medium_severity_count = sum(1 for issue in issues 
                                  if any(keyword in issue.lower() for keyword in medium_severity_keywords))
        low_severity_count = sum(1 for issue in issues 
                               if any(keyword in issue.lower() for keyword in low_severity_keywords))
        
        # Calculate impact (negative for issues, positive for edits)
        impact = -(high_severity_count * 0.3 + medium_severity_count * 0.15 + low_severity_count * 0.05)
        impact += len(suggested_edits) * 0.05  # Positive impact from having suggestions
        
        return max(-0.5, min(0.5, impact))  # Clamp between -0.5 and 0.5


class SpecializedCritic(AgentCritic):
    """Specialized critic for specific agent types"""
    
    def __init__(self, agent_type: AgentType):
        super().__init__(agent_type)
        self.specialized_criteria = self._get_specialized_criteria()
    
    def _get_specialized_criteria(self) -> Dict[str, Any]:
        """Get specialized criteria for this agent type"""
        criteria = {
            AgentType.LOGICAL: {
                'focus': ['logical consistency', 'evidence quality', 'reasoning validity'],
                'keywords': ['logical', 'evidence', 'proof', 'reasoning', 'valid', 'sound']
            },
            AgentType.EMOTIONAL: {
                'focus': ['empathy', 'emotional intelligence', 'human impact'],
                'keywords': ['emotion', 'feel', 'empathy', 'human', 'personal']
            },
            AgentType.CREATIVE: {
                'focus': ['originality', 'innovation', 'imagination'],
                'keywords': ['creative', 'novel', 'original', 'innovative', 'imaginative']
            },
            AgentType.STRATEGIC: {
                'focus': ['long-term thinking', 'resource optimization', 'risk assessment'],
                'keywords': ['strategy', 'plan', 'long-term', 'resource', 'risk']
            },
            AgentType.VERIFIER: {
                'focus': ['factual accuracy', 'source verification', 'evidence quality'],
                'keywords': ['fact', 'verify', 'source', 'evidence', 'accurate']
            },
            AgentType.ARBITER: {
                'focus': ['fairness', 'balance', 'conflict resolution'],
                'keywords': ['fair', 'balanced', 'neutral', 'resolve', 'compromise']
            }
        }
        
        return criteria.get(self.agent_type, {
            'focus': ['general quality', 'clarity', 'accuracy'],
            'keywords': ['quality', 'clear', 'accurate']
        })
    
    def critique(self, agent_output: AgentOutput) -> AgentCritique:
        """Enhanced critique with specialized criteria"""
        # Get base critique
        base_critique = super().critique(agent_output)
        
        # Add specialized analysis
        specialized_issues = self._analyze_specialized_criteria(agent_output)
        
        # Combine issues
        all_issues = base_critique.issues + specialized_issues
        
        # Recalculate confidence impact
        confidence_impact = self._calculate_confidence_impact(all_issues, base_critique.suggested_edits)
        
        return AgentCritique(
            agent=self.agent_type,
            passed=len(all_issues) == 0,
            issues=all_issues,
            suggested_edits=base_critique.suggested_edits,
            confidence_impact=confidence_impact,
            timestamp=datetime.now()
        )
    
    def _analyze_specialized_criteria(self, agent_output: AgentOutput) -> List[str]:
        """Analyze output against specialized criteria"""
        issues = []
        criteria = self.specialized_criteria
        text = agent_output.text_draft.lower()
        
        # Check for focus areas
        for focus in criteria['focus']:
            if focus not in text and not any(keyword in text for keyword in criteria['keywords']):
                issues.append(f"Missing {focus} considerations")
        
        # Check for appropriate keywords
        keyword_count = sum(1 for keyword in criteria['keywords'] if keyword in text)
        if keyword_count < 2:  # Should have at least 2 relevant keywords
            issues.append(f"Insufficient {self.agent_type.value} perspective (only {keyword_count} relevant terms)")
        
        return issues


class AgentCritiqueManager:
    """Manages agent critique and rewrite process"""
    
    def __init__(self):
        self.critics = {}
        self.critique_history = []
        self.max_allowed_issues: Optional[int] = CRITIC_MAX_ALLOWED_ISSUES  # If set, overrides pass criterion

    def set_max_allowed_issues(self, value: Optional[int]) -> None:
        """Dynamically set diagnostic strictness threshold."""
        self.max_allowed_issues = value
    
    def critique_agent_output(self, agent_output: AgentOutput) -> Tuple[AgentCritique, AgentOutput]:
        """
        Critique and potentially rewrite an agent output
        
        Args:
            agent_output: AgentOutput to critique
            
        Returns:
            Tuple of (critique, final_output)
        """
        # Get or create critic for this agent type
        if agent_output.agent not in self.critics:
            self.critics[agent_output.agent] = SpecializedCritic(agent_output.agent)
        
        critic = self.critics[agent_output.agent]
        
        # Perform critique
        critique = critic.critique(agent_output)
        # Apply loosened strictness if configured (diagnostic mode)
        if self.max_allowed_issues is not None:
            if len(critique.issues) <= self.max_allowed_issues:
                critique.passed = True
        
        # Record critique
        self._record_critique(agent_output, critique)
        
        # Rewrite if needed (single attempt), then re-critique; escalate if still failing
        if not critique.passed:
            final_output = critic.rewrite(agent_output, critique)
            second_critique = critic.critique(final_output)
            if self.max_allowed_issues is not None and len(second_critique.issues) <= self.max_allowed_issues:
                second_critique.passed = True
            if not second_critique.passed:
                # Mark escalation
                second_critique.escalate = True
            critique = second_critique
        else:
            final_output = agent_output
        
        return critique, final_output
    
    def critique_multiple_outputs(self, agent_outputs: List[AgentOutput]) -> List[Tuple[AgentCritique, AgentOutput]]:
        """
        Critique multiple agent outputs
        
        Args:
            agent_outputs: List of AgentOutputs to critique
            
        Returns:
            List of (critique, final_output) tuples
        """
        results = []
        
        for agent_output in agent_outputs:
            critique, final_output = self.critique_agent_output(agent_output)
            results.append((critique, final_output))
        
        return results
    
    def _record_critique(self, agent_output: AgentOutput, critique: AgentCritique) -> None:
        """Record critique for analysis"""
        record = {
            'timestamp': datetime.now(),
            'agent_type': agent_output.agent.value,
            'original_confidence': agent_output.confidence,
            'critique_passed': critique.passed,
            'issues_count': len(critique.issues),
            'suggested_edits_count': len(critique.suggested_edits),
            'confidence_impact': critique.confidence_impact
        }
        
        self.critique_history.append(record)
        
        # Keep only recent history (last 1000 critiques)
        if len(self.critique_history) > 1000:
            self.critique_history = self.critique_history[-1000:]
    
    def get_critique_stats(self) -> Dict[str, Any]:
        """Get critique statistics"""
        if not self.critique_history:
            return {'total_critiques': 0, 'pass_rate': 0.0, 'avg_issues': 0.0}
        
        total_critiques = len(self.critique_history)
        passed_count = sum(1 for record in self.critique_history if record['critique_passed'])
        avg_issues = sum(record['issues_count'] for record in self.critique_history) / total_critiques
        
        return {
            'total_critiques': total_critiques,
            'pass_rate': passed_count / total_critiques,
            'avg_issues': avg_issues,
            'recent_pass_rate': self._calculate_recent_pass_rate()
        }
    
    def _calculate_recent_pass_rate(self, window: int = 100) -> float:
        """Calculate recent pass rate"""
        recent_critiques = self.critique_history[-window:]
        if not recent_critiques:
            return 0.0
        
        passed_count = sum(1 for record in recent_critiques if record['critique_passed'])
        return passed_count / len(recent_critiques)


def create_critique_manager() -> AgentCritiqueManager:
    """Create a new critique manager"""
    return AgentCritiqueManager()
