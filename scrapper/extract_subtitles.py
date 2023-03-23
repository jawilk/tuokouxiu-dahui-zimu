import re
import cv2
import pytesseract
from tqdm import tqdm


cap = cv2.VideoCapture('video.mp4')

pattern = re.compile(r'[\u4e00-\u9fff]+')
prev_text = ''
text_all = []

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
# fps = int(cap.get(cv2.CAP_PROP_FPS))
# interval = 3

for i in tqdm(range(frame_count)):
    # cap.set(cv2.CAP_PROP_POS_FRAMES, i)
    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    n, m = gray.shape
    gray = gray[int(3*n/4):, int(m/4):int(3*m/4)]
    gray[gray < 230] = 0
    gray[gray >= 230] = 255
    # gray = cv2.resize(gray, (1000, 200))

    thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(thresh, lang='chi_sim')

    chinese_count = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    chinese_percent = chinese_count / len(text)
    if chinese_percent >= 0.5:
        text_new = ''.join(pattern.findall(text))
        if prev_text == '':
            text_all.append(text_new)
            prev_text = ''.join(pattern.findall(text_new))
            continue

        match_count = sum([1 for char in prev_text if char in text_new])
        match_percent = match_count / len(prev_text)
        if match_percent < 0.7:
            text_all.append(text_new)
            prev_text = ''.join(pattern.findall(text_new))

    cv2.imshow('frame', thresh)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

print(text_all)
with open('output.txt', 'w') as file:
    file.write('\n'.join(str(line) for line in text_all))
