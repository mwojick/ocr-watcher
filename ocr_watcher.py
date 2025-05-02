import subprocess
import time
import os
import tempfile
from PIL import ImageGrab


def process_image_with_tesseract(image_path):
    # Run tesseract on the image
    result = subprocess.run(
        [
            "tesseract",
            image_path,
            "stdout",
            "--psm",
            "3",
            "-l",
            "jpn",
            "-c",
            "preserve_interword_spaces=1",
        ],
        capture_output=True,
        text=True,
    )
    # Copy the result to clipboard using wl-copy
    ocr_text = result.stdout.strip()
    if ocr_text:
        subprocess.run(["wl-copy"], input=ocr_text.encode(), check=False)
        print(f"OCR Text copied to clipboard: {ocr_text}")
    else:
        print(f"Error: {result.stderr}")


def main():
    print("Monitoring clipboard for images...")
    last_image_data = None

    while True:
        try:
            # Check if there's an image in the clipboard
            img = ImageGrab.grabclipboard()

            if img is not None:
                # Compare with last image to avoid processing the same image multiple times
                current_image_data = img.tobytes()

                if current_image_data != last_image_data:
                    print("New image detected in clipboard")
                    last_image_data = current_image_data

                    # Save the image to a temporary file
                    with tempfile.NamedTemporaryFile(
                        suffix=".png", delete=False
                    ) as temp:
                        temp_filename = temp.name

                    img.save(temp_filename)
                    process_image_with_tesseract(temp_filename)

                    # Clean up
                    os.unlink(temp_filename)

            # Wait before checking again
            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
