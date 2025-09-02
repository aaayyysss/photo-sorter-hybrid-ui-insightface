import os
import numpy as np
import cv2
from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0)

def build_reference_embeddings(ref_dir, emit):
    db = {}
    for person in os.listdir(ref_dir):
        person_path = os.path.join(ref_dir, person)
        if not os.path.isdir(person_path):
            continue
        embeddings = []
        for fname in os.listdir(person_path):
            fpath = os.path.join(person_path, fname)
            img = cv2.imread(fpath)
            if img is None:
                continue
            faces = face_app.get(img)
            if faces:
                embeddings.append(faces[0].embedding)
        if embeddings:
            db[person] = np.mean(embeddings, axis=0)
            emit('log', f"✅ Loaded {len(embeddings)} images for identity: {person}")
        else:
            emit('log', f"⚠️ No face found for identity: {person}")
    return db

def sort_photos_with_embeddings(ref_db, inbox_dir, output_dir, threshold, emit):
    for subfolder, _, files in os.walk(inbox_dir):
        for fname in files:
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            fpath = os.path.join(subfolder, fname)
            img = cv2.imread(fpath)
            if img is None:
                continue
            faces = face_app.get(img)
            if not faces:
                emit('log', f"❌ No face found in: {fpath}")
                continue
            emb = faces[0].embedding.reshape(1, -1)
            best_score, best_match = 0, None
            for person, ref_emb in ref_db.items():
                score = cosine_similarity(emb, ref_emb.reshape(1, -1))[0][0]
                if score > best_score:
                    best_score = score
                    best_match = person
            if best_score >= threshold:
                out_dir = os.path.join(output_dir, best_match)
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, os.path.basename(fpath))
                cv2.imwrite(out_path, img)
                emit('log', f"✅ {os.path.basename(fpath)} matched {best_match} ({best_score:.2f})")
            else:
                emit('log', f"⚠️ No match for {os.path.basename(fpath)} (max: {best_score:.2f})")
