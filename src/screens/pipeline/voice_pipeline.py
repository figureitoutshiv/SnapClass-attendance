from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np
import io
import librosa
import streamlit as st

VOICE_SAMPLE_RATE = 16000

@st.cache_resource
def load_voice_encoder():
    return VoiceEncoder()

def get_voice_embedding(audio_bytes):
    try:
        encoder = load_voice_encoder()

        audio, sr = librosa.load(
            io.BytesIO(audio_bytes), sr=VOICE_SAMPLE_RATE
        )
        wav = preprocess_wav(audio, source_sr=sr)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()

    except Exception as e:
        st.error('Voice recog error')
        return None

def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    new_embedding = np.asarray(new_embedding, dtype=np.float32).reshape(-1)
    new_norm = np.linalg.norm(new_embedding)
    if new_norm == 0:
        return None, 0.0

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding is None:
            continue

        stored_embedding = np.asarray(
            stored_embedding, dtype=np.float32
        ).reshape(-1)
        if stored_embedding.size == 0:
            continue
        if stored_embedding.shape != new_embedding.shape:
            raise ValueError("Voice embeddings must have matching dimensions.")

        stored_norm = np.linalg.norm(stored_embedding)
        if stored_norm == 0:
            continue

        similarity = float(
            np.dot(new_embedding, stored_embedding) / (new_norm * stored_norm)
        )
        if similarity > best_score:
            best_score = similarity
            best_sid = sid

    if best_score >= threshold:
        return best_sid, best_score
    return None, best_score

def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    encoder = load_voice_encoder()
    audio, sr = librosa.load(
        io.BytesIO(audio_bytes), sr=VOICE_SAMPLE_RATE
    )
    segments = librosa.effects.split(audio, top_db=30)

    identified_results = {}

    for start, end in segments:
        if end - start < sr * 0.5:
            continue
        segment_audio = audio[start:end]
        wav = preprocess_wav(segment_audio, source_sr=sr)
        embedding = encoder.embed_utterance(wav)

        sid, score = identify_speaker(embedding, candidates_dict, threshold)

        if sid is not None:
            if sid not in identified_results or score > identified_results[sid]:
                identified_results[sid] = score

    return identified_results
