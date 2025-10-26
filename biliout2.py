import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import subprocess
import platform

def sanitize_filename(filename):
    """清理文件名中的特殊字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def select_folder(export_mode):
    folder_path = filedialog.askdirectory()
    if folder_path:
        output_folder = os.path.join(folder_path, '导出')
        os.makedirs(output_folder, exist_ok=True)
        if export_mode == 'video':
            for vt in ['16', '32', '64', '80']:
                process_folder(folder_path, output_folder, vt)
        else:
            process_audio_folder(folder_path, output_folder)

def process_folder(path, output_folder, video_type):
    video_type = str(video_type)
    for root, dirs, files in os.walk(path):
        if 'entry.json' in files and video_type in dirs:
            entry_json_path = os.path.join(root, 'entry.json')
            with open(entry_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                title = data.get('title', '')
                if not title:
                    print("找不到json数据文件")
                    continue
                
                # 清理文件名
                safe_title = sanitize_filename(title)
                output_filename = f"{safe_title}.mp4"
                output_filepath = os.path.join(output_folder, output_filename)
                
                audio_file = os.path.join(root, video_type, 'audio.m4s')
                video_file = os.path.join(root, video_type, 'video.m4s')
                
                try:
                    # Windows下需要shell=True
                    shell_flag = True if platform.system() == 'Windows' else False
                    subprocess.run([
                        "ffmpeg",
                        "-i", video_file,
                        "-i", audio_file,
                        "-c", "copy",
                        output_filepath
                    ], check=True, shell=shell_flag)
                    
                    if os.path.exists(output_filepath):
                        print(f"成功处理文件{output_filename}")
                    else:
                        print(f"文件创建失败: {output_filename}")
                except subprocess.CalledProcessError as e:
                    print(f"合并出错: {e}")

def process_audio_folder(path, output_folder):
    video_types = ['16', '32', '64', '80']
    for root, dirs, files in os.walk(path):
        if 'entry.json' in files:
            entry_json_path = os.path.join(root, 'entry.json')
            with open(entry_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                title = data.get('title', '')
                if not title:
                    print("找不到json数据文件")
                    continue
                
                # 清理文件名
                safe_title = sanitize_filename(title)
                output_filename = f"{safe_title}.aac"
                output_filepath = os.path.join(output_folder, output_filename)
                
                audio_file = None
                for vt in video_types:
                    audio_path = os.path.join(root, vt, 'audio.m4s')
                    if os.path.exists(audio_path):
                        audio_file = audio_path
                        break
                
                if not audio_file:
                    print(f"未找到音频文件: {root}")
                    continue
                
                try:
                    # Windows下需要shell=True
                    shell_flag = True if platform.system() == 'Windows' else False
                    subprocess.run([
                        "ffmpeg",
                        "-i", audio_file,
                        "-c:a", "copy",
                        "-f", "adts",
                        output_filepath
                    ], check=True, shell=shell_flag)
                    
                    if os.path.exists(output_filepath):
                        print(f"成功导出音频: {output_filename}")
                    else:
                        print(f"音频创建失败: {output_filename}")
                except subprocess.CalledProcessError as e:
                    print(f"音频导出错误: {e}")

def main():
    root = tk.Tk()
    root.geometry("300x180")
    root.title("b站离线缓存导出工具")
    export_type = tk.StringVar(value='video')

    lbl1 = tk.Label(root, text="当前版本可以自动扫描大多数缓存")
    lbl1.pack(pady=3)

    lbl2 = tk.Label(root, text="Ciallo～ (∠・ω< )⌒★")
    lbl2.pack(pady=3)

    radio_frame = tk.Frame(root)
    radio_frame.pack(pady=5)
    tk.Radiobutton(radio_frame, text="导出视频", variable=export_type, value='video').pack(side=tk.LEFT, padx=5)
    tk.Radiobutton(radio_frame, text="导出音频", variable=export_type, value='audio').pack(side=tk.LEFT, padx=5)

    btn = tk.Button(root, text="请选择你的英雄", 
                  command=lambda: select_folder(export_type.get()))
    btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()