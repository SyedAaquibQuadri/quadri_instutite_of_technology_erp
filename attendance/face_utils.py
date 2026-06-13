import json
import numpy as np
import face_recognition
import cv2
from accounts.models import StudentProfile


def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        return None
    return encodings[0]


def encode_face_from_multiple(image_paths):
    all_encodings = []
    for path in image_paths:
        enc = encode_face(path)
        if enc is not None:
            all_encodings.append(enc)
    if len(all_encodings) == 0:
        return None
    return np.mean(all_encodings, axis=0)


def save_encoding(student_id, encoding):
    try:
        profile = StudentProfile.objects.get(user_id=student_id)
        profile.face_encoding = json.dumps(encoding.tolist())
        profile.save(update_fields=['face_encoding'])
        return True
    except StudentProfile.DoesNotExist:
        return False


def load_all_encodings():
    profiles = StudentProfile.objects.exclude(
        face_encoding__isnull=True
    ).exclude(
        face_encoding=''
    ).select_related('user')

    result = {}
    for profile in profiles:
        try:
            enc = np.array(json.loads(profile.face_encoding), dtype=np.float64)
            result[profile.user.pk] = {
                'encoding': enc,
                'name': profile.user.get_full_name() or profile.user.username,
                'roll_no': profile.roll_no,
            }
        except (json.JSONDecodeError, ValueError):
            continue
    return result


def recognize_faces(frame, all_encodings, tolerance=0.5):
    if not all_encodings:
        return [], []

    if len(frame.shape) == 3 and frame.shape[2] == 3:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    else:
        rgb_frame = frame

    face_locations = face_recognition.face_locations(rgb_frame, model='hog')
    frame_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    known_ids = list(all_encodings.keys())
    known_encs = [all_encodings[sid]['encoding'] for sid in known_ids]

    matched_students = []
    faces_payload = []

    for face_enc, face_loc in zip(frame_encodings, face_locations):
        top, right, bottom, left = face_loc
        box = [int(left), int(top), int(right - left), int(bottom - top)]
        matched = False
        matched_name = 'Unknown'
        matched_id = None

        if known_encs:
            results = face_recognition.compare_faces(known_encs, face_enc, tolerance=tolerance)
            distances = face_recognition.face_distance(known_encs, face_enc)
            best_idx = int(np.argmin(distances))
            if results[best_idx]:
                matched_id = known_ids[best_idx]
                matched_name = all_encodings[matched_id]['name']
                matched = True
                if not any(m['student_id'] == matched_id for m in matched_students):
                    matched_students.append({
                        'student_id': matched_id,
                        'name': matched_name,
                        'roll_no': all_encodings[matched_id]['roll_no'],
                    })

        faces_payload.append({
            'box': box,
            'matched': matched,
            'name': matched_name,
        })

    return matched_students, faces_payload