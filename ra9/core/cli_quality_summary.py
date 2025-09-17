import json
from typing import Dict, Any
from ra9.test_complete_brain_architecture import test_complete_brain_workflow


def run_quality_summary(payload: Dict[str, Any] = None) -> Dict[str, Any]:
    """Run the complete workflow (test harness) and print a compact quality summary JSON."""
    result = test_complete_brain_workflow()
    summary = {
        'broadcast_count': len(result.get('gated_items', [])),
        'quarantine_count': len(result.get('quarantine', [])),
        'coherence': float(result.get('coherence_analysis', {}).get('coherence_score', 0.0)),
        'critique_pass_rate': float(result.get('system_stats', {}).get('critique', {}).get('pass_rate', 0.0)),
    }
    print(json.dumps({'quality_summary': summary}, ensure_ascii=False))
    return summary


