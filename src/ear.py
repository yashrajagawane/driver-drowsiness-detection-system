from scipy.spatial import distance as dist


def eye_aspect_ratio(eye):
    """
    Calculate the Eye Aspect Ratio (EAR).

    Parameters:
        eye: A list or numpy array containing 6 (x, y) coordinates
              of the eye landmarks.

    Returns:
        ear: Eye Aspect Ratio value (float)
    """

    # Vertical distances
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Horizontal distance
    C = dist.euclidean(eye[0], eye[3])

    # Prevent division by zero
    if C == 0:
        return 0.0

    # EAR formula
    ear = (A + B) / (2.0 * C)

    return ear