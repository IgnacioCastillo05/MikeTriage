
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.data.triage_dataset_loader import triage_dataset_loader
from app.data.synthea_generator import synthea_generator
from app.ml.triage_trainer import triage_trainer
from app.ml.symptom_encoder import symptom_encoder
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Iniciando pipeline completo de entrenamiento")
    
    logger.info("Cargando dataset FEDMLL...")
    fedmll_cases = triage_dataset_loader.load_fedmll_triage()
    logger.info(f"Cargados {len(fedmll_cases)} casos de FEDMLL")
    
    logger.info("Generando datos sinteticos...")
    synthea_cases = synthea_generator.generate_patients(1000)
    logger.info(f"Generados {len(synthea_cases)} casos sinteticos")
    
    all_cases = fedmll_cases + synthea_cases
    logger.info(f"Total casos: {len(all_cases)}")
    
    all_symptoms = []
    for case in all_cases:
        symptoms = case.get("sintomas", [])
        if isinstance(symptoms, list):
            all_symptoms.extend(symptoms)
        elif isinstance(symptoms, str):
            all_symptoms.append(symptoms)
    
    logger.info("Entrenando vectorizador de sintomas...")
    symptom_encoder.fit(all_symptoms)
    
    models_path = triage_trainer.models_path
    os.makedirs(models_path, exist_ok=True)
    symptom_encoder.save(os.path.join(models_path, "symptom_vectorizer.pkl"))
    
    logger.info("Preparando datos para entrenamiento...")
    X, y = triage_trainer.prepare_training_data(all_cases)
    
    logger.info("Entrenando modelo Random Forest...")
    result = triage_trainer.train(X, y)
    
    logger.info(f"Entrenamiento completado: {result}")
    
    report_path = os.path.join(models_path, "training_report.json")
    with open(report_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Reporte guardado en {report_path}")

if __name__ == "__main__":
    main()