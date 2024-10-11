import threading
import time
import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab, Image, ImageTk
import pytesseract
import os


def show_mouse_position():
    import time

    print("3秒后开始显示鼠标坐标，按Ctrl+C停止")
    time.sleep(3)
    try:
        while True:
            x, y = pyautogui.position()
            position_str = f"X: {x}, Y: {y}"
            print(position_str, end="\r")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n结束")


class TaskManager:
    def __init__(self):
        self.number_region = (170, 250, 510, 370)
        self.draw_region = (176, 522, 472, 813)
        self.x_l_mo = 45
        self.x_r_mo = 40
        pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/bin/tesseract"
        os.makedirs("temp", exist_ok=True)
        self.log_text = None
        self.image_labels = None

    def set_ui_elements(self, log_text, image_labels):
        self.log_text = log_text
        self.image_labels = image_labels

    def set_number_region(self, x1, y1, x3, y3):
        self.number_region = (min(x1, x3), min(y1, y3), max(x1, x3), max(y1, y3))

    def set_draw_region(self, x1, y1, x3, y3):
        self.draw_region = (min(x1, x3), min(y1, y3), max(x1, x3), max(y1, y3))

    def start_task(self, total_questions, answer_interval, prepare_time):
        threading.Thread(
            target=self._task_thread,
            args=(total_questions, answer_interval, prepare_time),
        ).start()

    def _task_thread(self, total_questions, answer_interval, prepare_time):
        self.log(f"准备开始，等待 {prepare_time} 秒...")
        time.sleep(prepare_time)

        custom_oem_psm_config = r"--oem 3 --psm 6"

        for i in range(total_questions):
            self.log(f"开始第 {i + 1} 题...")
            screenshot = ImageGrab.grab(bbox=self.number_region)

            if screenshot.width == 0 or screenshot.height == 0:
                self.log(f"第 {i + 1} 题：区域截图失败，宽度或高度为 0")
                continue

            self.update_image(self.image_labels[0], screenshot)

            img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            height, width = img.shape[:2]
            mid_x = width // 2

            left_img = img[:, : mid_x - self.x_l_mo]
            right_img = img[:, mid_x + self.x_r_mo :]

            left_img_path = f"temp/{i + 1}_l.png"
            right_img_path = f"temp/{i + 1}_r.png"
            cv2.imwrite(left_img_path, left_img)
            cv2.imwrite(right_img_path, right_img)

            self.update_image(
                self.image_labels[1],
                Image.fromarray(cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)),
            )
            self.update_image(
                self.image_labels[2],
                Image.fromarray(cv2.cvtColor(right_img, cv2.COLOR_BGR2RGB)),
            )

            nums = self.recognize_numbers(
                left_img_path, right_img_path, custom_oem_psm_config
            )

            if None not in nums and len(nums) == 2:
                if nums[0] > nums[1]:
                    symbol = ">"
                    self.draw_symbol(">")
                elif nums[0] < nums[1]:
                    symbol = "<"
                    self.draw_symbol("<")
                else:
                    symbol = "="
                    self.draw_symbol("=")

                self.log(f"第 {i + 1} 题结果：{nums[0]} {symbol} {nums[1]}")
            else:
                self.log(f"第 {i + 1} 题：无法识别足够的数字")

            time.sleep(answer_interval)

    def process_image(self, screenshot):
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        height, width = img.shape[:2]
        mid_x = width // 2
        left_img = img[:, : mid_x - self.x_l_mo]
        right_img = img[:, mid_x + self.x_r_mo :]
        return left_img, right_img

    def recognize_numbers(self, left_img_path, right_img_path, config):
        nums = []
        for img_path in [left_img_path, right_img_path]:
            result = pytesseract.image_to_string(
                Image.open(img_path), config=config
            ).strip()
            result = "".join(filter(str.isdigit, result))
            if result:
                try:
                    num = int(result)
                    nums.append(num)
                except ValueError:
                    self.log(f"无法识别有效数字，OCR 输出：'{result}'")
                    nums.append(None)
            else:
                self.log(f"未找到有效的数字")
                nums.append(None)
        return nums

    def draw_symbol(self, symbol):
        if symbol == ">":
            pyautogui.moveTo(self.draw_region[0] + 60, self.draw_region[1] + 60)
            pyautogui.dragRel(10, 10, duration=0.05)
            pyautogui.dragRel(-10, 1, duration=0.05)
        elif symbol == "<":
            pyautogui.moveTo(self.draw_region[0] + 60, self.draw_region[1] + 60)
            pyautogui.dragRel(-10, 1, duration=0.05)
            pyautogui.dragRel(10, 10, duration=0.05)
        elif symbol == "=":
            pyautogui.moveTo(self.draw_region[0] + 40, self.draw_region[1] + 70)
            pyautogui.dragRel(40, 0, duration=0.1)
            pyautogui.moveRel(0, 20)
            pyautogui.dragRel(40, 0, duration=0.1)

    def log(self, message):
        if self.log_text:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        else:
            print(message)

    def update_image(self, label, image):
        if label:
            photo = ImageTk.PhotoImage(image)
            label.config(image=photo)
            label.image = photo
