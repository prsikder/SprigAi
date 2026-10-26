# SprigAI AI Model Directory

Place trained model artifacts here when the AI modules are implemented in later parts.

Expected subfolders:

- `crop_recommendation/` for crop `.pkl` models, encoders, and scalers.
- `fertilizer_recommendation/` for fertilizer recommendation `.pkl` artifacts.
- `disease_detection/` for PyTorch `.pth` models and class maps.
- `soil_classification/` for PyTorch `.pth` models and class maps.

This foundation does not load models yet. Feature modules should check for missing
files and show a clear "model file missing" message before running inference.

## Crop Recommendation

Preferred location:

- `ai_models/crop_recommendation/crop_encoder.pkl`
- `ai_models/crop_recommendation/district_encoder.pkl`
- `ai_models/crop_recommendation/growth_encoder.pkl`
- `ai_models/crop_recommendation/harvest_encoder.pkl`
- `ai_models/crop_recommendation/season_encoder.pkl`
- `ai_models/crop_recommendation/rf_classifier.pkl`
- `ai_models/crop_recommendation/rf_regressor.pkl`

For this local build, the service also checks the provided
`Required files/crop recommendation/` folder as a fallback.

## Fertilizer Recommendation

Preferred location:

- `ai_models/fertilizer_recommendation/catboost_fertilizer_model.pkl`
- `ai_models/fertilizer_recommendation/fertilizer_categorical_columns.pkl`
- `ai_models/fertilizer_recommendation/fertilizer_cat_features.pkl`
- `ai_models/fertilizer_recommendation/fertilizer_input_columns.pkl`

For this local build, the service also checks the provided
`Required files/Fertilizer recommendation/` folder as a fallback.

## Disease Detection

Preferred location:

- `ai_models/disease_detection/crop_disease_model.pth`
- `ai_models/disease_detection/class_names.json`
- `ai_models/disease_detection/metrics.json`

For this local build, the service also checks
`Required files/Crop Disease Detection/` as a fallback.

## Soil Classification

Preferred location:

- `ai_models/soil_classification/soil_classifier.pth`
- `ai_models/soil_classification/class_names.json`
- `ai_models/soil_classification/metrics.json`

For this local build, the service also checks
`Required files/Soil classification/` as a fallback.
