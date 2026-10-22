"""
Smart Agriculture System - ML Model Training Script
Run this once to generate crop_model.pkl and fertilizer_model.pkl
Usage: python models/train_models.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# 1. CROP RECOMMENDATION MODEL
# ─────────────────────────────────────────────
def train_crop_model():
    print("Training Crop Recommendation Model...")

    # Synthetic training data: [N, P, K, temperature, humidity, ph, rainfall, season_enc, soil_enc]
    # Crops: Rice, Wheat, Maize, Cotton, Sugarcane, Soybean, Tomato, Onion, Groundnut, Mango
    np.random.seed(42)
    n_samples = 2000

    data = []
    labels = []

    crop_profiles = {
        "Rice":      dict(N=(80,120), P=(40,60),  K=(40,60),  temp=(22,34), hum=(70,90), ph=(5.5,7.0), rain=(150,300), season=[0],    soil=[0,1]),
        "Wheat":     dict(N=(80,120), P=(40,60),  K=(40,60),  temp=(10,25), hum=(40,70), ph=(6.0,7.5), rain=(50,150),  season=[1],    soil=[1,2]),
        "Maize":     dict(N=(80,120), P=(40,60),  K=(40,60),  temp=(18,32), hum=(50,75), ph=(5.8,7.0), rain=(60,120),  season=[0,1],  soil=[1,2]),
        "Cotton":    dict(N=(80,120), P=(40,60),  K=(40,60),  temp=(21,35), hum=(50,70), ph=(6.0,7.5), rain=(60,100),  season=[0],    soil=[3,1]),
        "Sugarcane": dict(N=(100,150),P=(50,80),  K=(80,120), temp=(20,35), hum=(60,80), ph=(6.0,7.5), rain=(100,200), season=[3],    soil=[1,0]),
        "Soybean":   dict(N=(20,40),  P=(60,80),  K=(40,60),  temp=(20,30), hum=(60,80), ph=(6.0,7.0), rain=(60,100),  season=[0],    soil=[1,3]),
        "Tomato":    dict(N=(80,120), P=(60,80),  K=(80,100), temp=(15,30), hum=(50,70), ph=(6.0,7.0), rain=(40,80),   season=[1,0],  soil=[2,1]),
        "Onion":     dict(N=(60,100), P=(40,60),  K=(60,80),  temp=(13,25), hum=(50,70), ph=(6.0,7.5), rain=(30,60),   season=[1],    soil=[2,1]),
        "Groundnut": dict(N=(20,40),  P=(40,60),  K=(40,60),  temp=(25,35), hum=(50,70), ph=(5.5,7.0), rain=(50,100),  season=[0],    soil=[2,1]),
        "Mango":     dict(N=(40,80),  P=(20,40),  K=(40,80),  temp=(24,35), hum=(50,70), ph=(5.5,7.5), rain=(75,250),  season=[3],    soil=[1,2]),
    }

    # season encoding: 0=Kharif, 1=Rabi, 2=Zaid, 3=Annual
    # soil encoding: 0=Clayey, 1=Loamy, 2=Sandy Loam, 3=Black

    per_crop = n_samples // len(crop_profiles)

    for crop, p in crop_profiles.items():
        for _ in range(per_crop):
            N    = np.random.uniform(*p["N"])
            P    = np.random.uniform(*p["P"])
            K    = np.random.uniform(*p["K"])
            temp = np.random.uniform(*p["temp"])
            hum  = np.random.uniform(*p["hum"])
            ph   = np.random.uniform(*p["ph"])
            rain = np.random.uniform(*p["rain"])
            season = np.random.choice(p["season"])
            soil   = np.random.choice(p["soil"])
            data.append([N, P, K, temp, hum, ph, rain, season, soil])
            labels.append(crop)

    df = pd.DataFrame(data, columns=["N","P","K","temperature","humidity","ph","rainfall","season","soil_type"])
    df["crop"] = labels

    X = df.drop("crop", axis=1).values
    y = df["crop"].values

    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(X, y_enc, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"  Crop Model Accuracy: {acc*100:.1f}%")

    joblib.dump(model, os.path.join(BASE_DIR, "crop_model.pkl"))
    joblib.dump(le,    os.path.join(BASE_DIR, "crop_label_encoder.pkl"))
    print("  Saved: crop_model.pkl, crop_label_encoder.pkl")


# ─────────────────────────────────────────────
# 2. FERTILIZER RECOMMENDATION MODEL
# ─────────────────────────────────────────────
def train_fertilizer_model():
    print("Training Fertilizer Recommendation Model...")

    np.random.seed(42)
    n_samples = 3000

    # Features: [soil_N, soil_P, soil_K, ph, crop_type_enc, moisture]
    # Labels: fertilizer id 0-9

    # crop type encoding: 0=Rice,1=Wheat,2=Maize,3=Cotton,4=Sugarcane,5=Soybean,6=Tomato,7=Onion,8=Groundnut,9=Mango

    fertilizer_rules = {
        # (crop_range, condition) -> fertilizer_id
        0: dict(N=(0,40),   P=(0,30),  K=(0,30),  crops=[0,1,2,3],   fert=0),   # Low N -> Urea
        1: dict(N=(0,40),   P=(0,30),  K=(0,30),  crops=[5,8],       fert=5),   # Legumes low P -> SSP
        2: dict(N=(40,80),  P=(0,30),  K=(0,30),  crops=[0,1,2,3],   fert=1),   # Medium N, low P -> DAP
        3: dict(N=(40,80),  P=(30,60), K=(0,30),  crops=[4,6,7],     fert=2),   # Low K -> MOP
        4: dict(N=(40,80),  P=(30,60), K=(30,60), crops=[3,5],       fert=3),   # Balanced -> NPK 10-26-26
        5: dict(N=(40,80),  P=(30,60), K=(30,60), crops=[0,1,2],     fert=4),   # Rice/Wheat -> NPK 12-32-16
        6: dict(N=(80,150), P=(30,60), K=(60,120),crops=[4,6,7],     fert=9),   # High demand -> K-Nitrate
        7: dict(N=(0,60),   P=(0,30),  K=(0,30),  crops=[0,1,2,3,6], fert=6),   # Organic need -> Vermicompost
        8: dict(N=(0,60),   P=(0,30),  K=(0,30),  crops=[6,3,0],     fert=7),   # Pest risk -> Neem Cake
        9: dict(N=(40,80),  P=(20,50), K=(20,50), crops=[0,1,2,6,7], fert=8),   # Zinc deficiency -> ZnSO4
    }

    data = []
    labels = []
    per_rule = n_samples // 10

    for rule_id, r in fertilizer_rules.items():
        for _ in range(per_rule):
            N    = np.random.uniform(r["N"][0], r["N"][1])
            P    = np.random.uniform(r["P"][0], r["P"][1])
            K    = np.random.uniform(r["K"][0], r["K"][1])
            ph   = np.random.uniform(5.5, 7.5)
            crop = np.random.choice(r["crops"])
            moist= np.random.uniform(20, 80)
            data.append([N, P, K, ph, crop, moist])
            labels.append(r["fert"])

    X = np.array(data)
    y = np.array(labels)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"  Fertilizer Model Accuracy: {acc*100:.1f}%")

    joblib.dump(model, os.path.join(BASE_DIR, "fertilizer_model.pkl"))
    print("  Saved: fertilizer_model.pkl")


# ─────────────────────────────────────────────
# 3. DISEASE CNN MODEL (MobileNetV2)
# ─────────────────────────────────────────────
def train_disease_model():
    print("Training Disease Detection CNN Model (MobileNetV2)...")
    try:
        import tensorflow as tf
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
        from tensorflow.keras.models import Model

        NUM_CLASSES = 28
        IMG_SIZE    = 224

        base = MobileNetV2(weights="imagenet", include_top=False,
                           input_shape=(IMG_SIZE, IMG_SIZE, 3))
        base.trainable = False

        x = base.output
        x = GlobalAveragePooling2D()(x)
        x = Dropout(0.3)(x)
        x = Dense(256, activation="relu")(x)
        x = Dropout(0.2)(x)
        out = Dense(NUM_CLASSES, activation="softmax")(x)

        disease_model = Model(inputs=base.input, outputs=out)
        disease_model.compile(optimizer="adam",
                               loss="categorical_crossentropy",
                               metrics=["accuracy"])

        # Save the untrained architecture (weights will be random).
        # In production: train on PlantVillage dataset.
        disease_model.save(os.path.join(BASE_DIR, "disease_model.h5"))
        print("  Saved: disease_model.h5 (architecture ready — train with PlantVillage dataset for real accuracy)")

    except ImportError:
        print("  TensorFlow not installed. Creating a placeholder disease_model.h5 flag file.")
        flag = os.path.join(BASE_DIR, "disease_model_missing.txt")
        with open(flag, "w") as f:
            f.write("Install tensorflow and re-run train_models.py to generate disease_model.h5")


if __name__ == "__main__":
    print("=" * 55)
    print("  Smart Agriculture — Model Training")
    print("=" * 55)
    train_crop_model()
    train_fertilizer_model()
    train_disease_model()
    print("\nAll models trained and saved in /models/")
