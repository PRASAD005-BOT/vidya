# Face-API.js Models Directory

This directory is intended to store the face-api.js model files for facial detection and emotion recognition.

## Models Required
- face detection model
- face landmark model
- face recognition model
- face expression model

If these models are not found locally, the application will automatically fall back to using CDN-hosted models.

## How to Add Models

The required model files can be downloaded from the face-api.js repository:
https://github.com/justadudewhohacks/face-api.js/tree/master/weights

The following files are needed:
- tiny_face_detector_model-weights_manifest.json
- tiny_face_detector_model-shard1
- face_landmark_68_model-weights_manifest.json
- face_landmark_68_model-shard1
- face_recognition_model-weights_manifest.json
- face_recognition_model-shard1
- face_recognition_model-shard2
- face_expression_model-weights_manifest.json
- face_expression_model-shard1

## Fallback Behavior

If local models are not found, the application will use the models hosted on the face-api.js CDN. 