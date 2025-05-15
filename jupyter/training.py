import argparse
import os
import glob
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor

def load_data(train_dir):
    # Load all Parquet files from the training channel
    files = glob.glob(os.path.join(train_dir, '*.parquet'))
    df_list = [pd.read_parquet(f) for f in files]
    return pd.concat(df_list, ignore_index=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    args = parser.parse_args()

    # Load and prepare data
    df = load_data(args.train)
    X = df[['wave_height_m', 'current_speed_kph']]
    y = df['sea_temp_c']

    # Train a simple RandomForest model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save the model to the SageMaker model directory
    model_dir = os.environ.get('SM_MODEL_DIR', '/opt/ml/model')
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, 'model.joblib'))
