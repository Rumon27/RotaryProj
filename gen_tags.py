import cv2
import os

OUTPUT_DIR = "tags"
DICTIONARY = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
TAG_SIZE_PX = 200
QUIET_ZONE_PX = 40     
NUM_TAGS = 3

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for tag_id in range(NUM_TAGS):
        tag_img = cv2.aruco.generateImageMarker(DICTIONARY, tag_id, TAG_SIZE_PX)

        padded = cv2.copyMakeBorder(
            tag_img,
            QUIET_ZONE_PX, QUIET_ZONE_PX, QUIET_ZONE_PX, QUIET_ZONE_PX,
            cv2.BORDER_CONSTANT, value=255
        )

        out_path = os.path.join(OUTPUT_DIR, f"tag_{tag_id}.png")
        cv2.imwrite(out_path, padded)
        print(f"saved {out_path}")

if __name__ == "__main__":
    main()