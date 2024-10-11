import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from core import show_mouse_position


def create_ui(task_manager):
    root = tk.Tk()
    root.title("自动比大小脚本")
    root.geometry("750x650")

    # 加载默认图像
    default_image = Image.open("bg.png")
    default_image_340x120 = ImageTk.PhotoImage(default_image.crop((0, 0, 340, 120)))
    default_image_120x120 = ImageTk.PhotoImage(default_image.crop((0, 0, 120, 120)))

    # 创建框架
    frame_top = tk.Frame(root)
    frame_middle = tk.Frame(root)
    frame_params = tk.Frame(root)
    frame_buttons = tk.Frame(root)
    frame_log = tk.Frame(root)
    frame_images = tk.Frame(root)

    # 放置框架
    frame_top.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    frame_middle.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
    frame_params.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
    frame_buttons.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
    frame_log.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
    frame_images.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)

    # 创建并放置控件
    number_region_entries = create_number_region_widgets(frame_top, task_manager)
    draw_region_entries = create_draw_region_widgets(frame_middle, task_manager)
    param_entries = create_parameter_widgets(frame_params)
    create_button_widgets(
        frame_buttons,
        task_manager,
        number_region_entries,
        draw_region_entries,
        param_entries,
    )
    log_text = create_log_widget(frame_log)
    image_labels = create_image_widgets(
        frame_images, default_image_340x120, default_image_120x120
    )

    task_manager.set_ui_elements(log_text, image_labels)

    root.mainloop()


def create_number_region_widgets(frame, task_manager):
    tk.Label(
        frame, text="数字区域坐标: x1, y1, x3, y3", font=("Helvetica", 12, "bold")
    ).grid(row=0, column=0, columnspan=4)
    entries = []
    for i, val in enumerate(task_manager.number_region):
        entry = tk.Entry(frame, width=5)
        entry.insert(0, str(val))
        entry.grid(row=1, column=i)
        entries.append(entry)
    return entries


def create_draw_region_widgets(frame, task_manager):
    tk.Label(
        frame, text="绘图区域坐标: x1, y1, x3, y3", font=("Helvetica", 12, "bold")
    ).grid(row=0, column=0, columnspan=4)
    entries = []
    for i, val in enumerate(task_manager.draw_region):
        entry = tk.Entry(frame, width=5)
        entry.insert(0, str(val))
        entry.grid(row=1, column=i)
        entries.append(entry)
    return entries


def create_parameter_widgets(frame):
    tk.Label(frame, text="作答题数:", font=("Helvetica", 12, "bold")).grid(
        row=0, column=0
    )
    question_count_entry = tk.Entry(frame)
    question_count_entry.grid(row=0, column=1)

    tk.Label(frame, text="作答间隔(秒):", font=("Helvetica", 12, "bold")).grid(
        row=1, column=0
    )
    answer_interval_entry = tk.Entry(frame)
    answer_interval_entry.grid(row=1, column=1)

    tk.Label(frame, text="开始前准备时间(秒):", font=("Helvetica", 12, "bold")).grid(
        row=2, column=0
    )
    prepare_time_entry = tk.Entry(frame)
    prepare_time_entry.grid(row=2, column=1)

    return question_count_entry, answer_interval_entry, prepare_time_entry


def create_button_widgets(
    frame, task_manager, number_region_entries, draw_region_entries, param_entries
):
    def set_number_region():
        try:
            coords = [int(entry.get()) for entry in number_region_entries]
            task_manager.set_number_region(*coords)
            messagebox.showinfo("提示", f"数字区域已设置: {tuple(coords)}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的坐标值！")

    def set_draw_region():
        try:
            coords = [int(entry.get()) for entry in draw_region_entries]
            task_manager.set_draw_region(*coords)
            messagebox.showinfo("提示", f"绘图区域已设置: {tuple(coords)}")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的坐标值！")

    def start_task():
        try:
            total_questions = int(param_entries[0].get())
            answer_interval = float(param_entries[1].get())
            prepare_time = int(param_entries[2].get())
            task_manager.start_task(total_questions, answer_interval, prepare_time)
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字设置！")

    tk.Button(
        frame,
        text="设置数字区域",
        command=set_number_region,
        font=("Helvetica", 10, "bold"),
    ).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(
        frame,
        text="设置绘图区域",
        command=set_draw_region,
        bg="#388E3C",
        font=("Helvetica", 10, "bold"),
    ).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(
        frame,
        text="获取鼠标坐标",
        command=show_mouse_position,
        fg="black",
        font=("Helvetica", 14, "bold"),
        bg="#008CBA",
    ).grid(row=1, column=0, padx=5, pady=5)
    tk.Button(
        frame,
        text="开始",
        command=start_task,
        fg="black",
        font=("Helvetica", 14, "bold"),
        bg="#4CAF50",
    ).grid(row=1, column=1, padx=5, pady=5)


def create_log_widget(frame):
    log_text = tk.Text(
        frame, height=10, font=("Helvetica", 12), bg="#ffffff", fg="#000000"
    )
    log_text.pack(fill=tk.BOTH, expand=True)
    return log_text


def create_image_widgets(frame, default_image_340x120, default_image_120x120):
    tk.Label(frame, text="原始截图", font=("Helvetica", 12, "bold")).grid(
        row=0, column=0
    )
    screenshot_label = tk.Label(frame, image=default_image_340x120)
    screenshot_label.grid(row=1, column=0)
    screenshot_label.image = default_image_340x120

    tk.Label(frame, text="处理后的左半部分图像", font=("Helvetica", 12, "bold")).grid(
        row=2, column=0
    )
    left_processed_label = tk.Label(frame, image=default_image_120x120)
    left_processed_label.grid(row=3, column=0)
    left_processed_label.image = default_image_120x120

    tk.Label(frame, text="处理后的右半部分图像", font=("Helvetica", 12, "bold")).grid(
        row=4, column=0
    )
    right_processed_label = tk.Label(frame, image=default_image_120x120)
    right_processed_label.grid(row=5, column=0)
    right_processed_label.image = default_image_120x120

    return screenshot_label, left_processed_label, right_processed_label
