import cv2

# Load the Cascade Classifier
body_cascade = cv2.CascadeClassifier("haarcascade_fullbody.xml")


def de(color_img):
    # Convert to grayscale
    gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)

    # Detect the body
    body = body_cascade.detectMultiScale(gray_img, 1.2, 1)

    # display rectrangle

    for (x, y, w, h) in body:
        cv2.rectangle(color_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # display image
    cv2.imshow('img', color_img)
    # v_writer.write(color_img)
    cv2.waitKey(1)
    # cv2.destroyAllWindows()

