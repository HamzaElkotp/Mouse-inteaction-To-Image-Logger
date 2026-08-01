import time, os, threading
from pynput import mouse
from PIL import Image, ImageDraw
from win32api import GetSystemMetrics

INTERVAL:int = 30
SCREEN_WIDTH:int = GetSystemMetrics(0)
SCREEN_HEIGHT:int = GetSystemMetrics(1)
OUTPUT_DIR:str = "Output/HI_mouse_dataset"
LINE_WIDTH:int = 4
POINT_RADIUS:int = 6

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

isRecording:bool = False
startTime:int = 0
path = []
clicks = []
lock = threading.Lock()

def startRecording()->None:
    global isRecording, startTime
    if not isRecording:
        isRecording = True
        startTime = time.time()
        print(f"Interaction detected at {startTime}! Started 10-second recording...")

def stop_recording()->None:
    global isRecording, startTime
    with lock:
        isRecording = False
        startTime = 0

def onMove(x,y)->None:
    with lock:
        startRecording()
        path.append((x,y))

def onClick(x,y, button, pressed):
    if(pressed):
        with lock:
            startRecording()
            clicks.append((x,y, button))

def generateImg(currentPath, currentClicks, timestamp)->None:
    img = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), "black")
    draw = ImageDraw.Draw(img)

    if len(currentPath) > 1:
        draw.line(currentPath, fill=(200, 220, 255), width=LINE_WIDTH)
    for x, y, button in currentClicks:
        color = "green" if button == mouse.Button.left else "red"
        draw.ellipse(
            [x - POINT_RADIUS, y - POINT_RADIUS, x + POINT_RADIUS, y + POINT_RADIUS],
            fill=color
        )

    imgPath = os.path.join(OUTPUT_DIR, f"mouse_track_{timestamp}.jpg")
    img.save(imgPath)
    print(f"Saved: {imgPath}\nWaiting for next interaction...")

if __name__ == "__main__":
    print("Mouse tracker running.")
    
    listener = mouse.Listener(on_move=onMove, on_click=onClick)
    listener.start()
    
    try:
        while True:
            time.sleep(0.1)
            with lock:
                if isRecording and (time.time() - startTime) >= INTERVAL:
                    currentPath = list(path)
                    currentClicks = list(clicks)

                    path.clear()
                    clicks.clear()
                    isRecording=False

                    threading.Thread(
                        target=generateImg,
                        args=(currentPath, currentClicks, int(time.time()))
                    ).start()

    except KeyboardInterrupt:
        listener.stop()