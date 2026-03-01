import urllib.request
import bz2
import os
import sys


def download_and_extract_model():
    """
    Downloads and extracts the Dlib 68-point facial landmark model.
    The model will be saved inside the 'models' folder.
    """

    # Secure HTTPS URL
    url = "https://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"

    models_dir = "models"
    compressed_file = os.path.join(models_dir, "shape_predictor_68_face_landmarks.dat.bz2")
    extracted_file = os.path.join(models_dir, "shape_predictor_68_face_landmarks.dat")

    # Create models folder if it does not exist
    os.makedirs(models_dir, exist_ok=True)

    # If model already exists, skip download
    if os.path.exists(extracted_file):
        print("✅ Model already exists. No need to download again.")
        return

    try:
        # Step 1: Download compressed model
        print("📥 Downloading Dlib face landmark model (~60MB)... Please wait.")
        urllib.request.urlretrieve(url, compressed_file)
        print("✅ Download complete.")

        # Step 2: Extract the .bz2 file
        print("📦 Extracting model...")
        with bz2.BZ2File(compressed_file, 'rb') as fr:
            with open(extracted_file, 'wb') as fw:
                fw.write(fr.read())

        # Step 3: Remove compressed file
        os.remove(compressed_file)

        print("🎉 Extraction complete!")
        print("Model is ready inside the 'models' folder.")

    except Exception as e:
        print("❌ Error occurred while downloading the model.")
        print("Error:", e)
        sys.exit(1)


if __name__ == "__main__":
    download_and_extract_model()