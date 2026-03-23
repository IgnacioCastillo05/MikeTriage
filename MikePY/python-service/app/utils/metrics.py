import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PredictionMetrics:
    def __init__(self):
        self.predictions = []
        self.errors = []

    def record_prediction(self, prediction: Dict[str, Any]):
        self.predictions.append({
            'timestamp': datetime.utcnow(),
            'event_id': prediction.get('event_id'),
            'markets': prediction.get('markets'),
            'features_used': prediction.get('features_used')
        })

        if len(self.predictions) > 10000:
            self.predictions = self.predictions[-5000:]

    def record_error(self, error: Exception, context: Dict[str, Any]):
        self.errors.append({
            'timestamp': datetime.utcnow(),
            'error': str(error),
            'context': context
        })

        if len(self.errors) > 1000:
            self.errors = self.errors[-500:]

    def get_stats(self) -> Dict[str, Any]:
        return {
            'total_predictions': len(self.predictions),
            'total_errors': len(self.errors),
            'error_rate': len(self.errors) / (len(self.predictions) + 1)
        }

metrics = PredictionMetrics()