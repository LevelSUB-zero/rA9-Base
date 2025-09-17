"""
Central configuration for quality thresholds and behavior toggles.
"""

# Critic diagnostic mode: allow up to N issues to still count as pass (None disables)
CRITIC_MAX_ALLOWED_ISSUES = None  # e.g., set to 2 for quick loosened check

# Coherence requirement for finalization
COHERENCE_THRESHOLD = 0.85


