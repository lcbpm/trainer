# watermark_remover 执行流程说明

## 1. 读取视频文件
- 程序会遍历输入目录，找到所有有效的视频文件（如 `.mp4`）。
- 对每个视频文件，依次进行处理。

---

## 2. 选择水印区域（弹窗手动框选）
- 读取视频的第一帧或有效帧。
- 弹出窗口（OpenCV 的 `selectROI`），让用户用鼠标框选水印所在区域（ROI）。
- 框选后按空格或回车，程序记录下 ROI 区域坐标。

---

## 3. 生成水印掩码（mask）
- 在选定的 ROI 区域内，自动分析多帧，检测水印的具体位置，生成二值掩码（mask）。
- 掩码表示哪些像素属于水印，需要被去除。

---

## 4. 预览去水印效果（可选）
- 程序会用 Lama 模型对一帧图片进行去水印处理。
- 弹窗显示去水印后的效果，用户可以选择继续或取消。
- 这一步**不会生成完整新视频**，只是预览。

---

## 5. 批量处理视频帧
- 对视频的每一帧，使用 Lama 模型和掩码进行去水印处理。
- Lama 会智能填补水印区域，使画面尽量自然。

---

## 6. 合成新视频
- 所有处理后的帧重新合成为新的视频文件（通常为 `.mp4`）。
- 输出到指定目录。

---

## 7. 输出处理信息
- 程序会输出每个视频的分辨率、时长、帧率、总帧数等信息。
- 处理完成后提示成功。

---

## 主要流程代码片段（伪代码）

```python
for video in videos:
    video_clip = VideoFileClip(video)
    # 1. 选择水印区域
    roi = watermark_detector.select_roi(video_clip)
    # 2. 生成掩码
    watermark_mask = watermark_detector.generate_mask(video_clip)
    # 3. 预览效果
    if preview_enabled:
        if not watermark_detector.preview_effect(video_clip, watermark_mask, lama_model, lama_config):
            print("Processing cancelled by user")
            break
    # 4. 批量处理帧并合成新视频
    process_video(video_clip, output_path, watermark_mask, lama_model, lama_config)
```

---

## 总结
- **手动选区** → **自动生成掩码** → **可选预览** → **批量去水印** → **合成新视频**
- Lama 模型保证去水印区域自然无痕。

如需详细代码解读或某一步的原理说明，欢迎继续提问！ 