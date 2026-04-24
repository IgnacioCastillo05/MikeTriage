
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.synthea_generator import synthea_generator
from app.ml.triage_trainer import triage_trainer
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Generando datos sinteticos para entrenamiento")
    
    cases = synthea_generator.generate_patients(1000)
    
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data", "synthetic_training_data.json"
    )
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Datos guardados en {output_path}")
    
    X, y = triage_trainer.prepare_training_data(cases)
    logger.info(f"Preparados {X.shape[0]} casos con {X.shape[1]} features")
    
    result = triage_trainer.train(X, y)
    logger.info(f"Entrenamiento completado: {result}")

if __name__ == "__main__":
    main()