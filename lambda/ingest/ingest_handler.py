import json
import boto3
import uuid
from datetime import datetime
import random
import os

# Cliente S3
s3 = boto3.client('s3', region_name='eu-west-3')
BUCKET_NAME = os.environ.get('BUCKET_NAME', '')

def generate_buoy_data():
    """
    Genera un diccionario con una sola lectura de boya.
    """
    return {
        "buoy_id": f"buoy-{uuid.uuid4().hex[:6]}",
        "timestamp": datetime.utcnow().isoformat(),
        "location": {
            "lat": round(random.uniform(48.0, 60.0), 5),
            "lon": round(random.uniform(-10.0, 5.0), 5)
        },
        "sea_temp_c": round(random.uniform(10.0, 18.0), 2),
        "wave_height_m": round(random.uniform(0.5, 3.0), 2),
        "current_speed_kph": round(random.uniform(1.0, 5.0), 2)
    }

def ingest_data_handler(event, context):
    """
    Lambda que genera N lecturas y las sube como JSONs independientes a S3.
    """
    try:
        if not BUCKET_NAME:
            raise ValueError("BUCKET_NAME no definido en variables de entorno")
        
        num_readings = 20   # <-- Número de filas a generar por invocación
        uploaded = []

        for i in range(num_readings):
            data = generate_buoy_data()
            # Nombre único basándose en ID, timestamp y un índice
            filename = f"raw/{data['buoy_id']}_{data['timestamp']}_{i:02d}.json"
            
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=filename,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            uploaded.append(filename)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'{num_readings} lecturas subidas',
                'files': uploaded
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
