# 基于 YOLOv8 与 DeepSORT 的多目标跟踪复现

本仓库对应同名课程论文。实验在 UA-DETRAC 的 MVI_20011 视频上比较 YOLOv8n、YOLOv8s 和不同检测置信度阈值。课程代码补充了空检测帧的跟踪器更新，并保存逐帧检测、跟踪和计时记录。检测器与 DeepSORT 外观特征网络均使用预训练权重。

## 1. 安装环境

原实验使用 Windows、Python 3.10.21、PyTorch 2.0.1、CUDA 11.8 和 RTX 3060 Laptop GPU。以下命令在仓库根目录的 PowerShell 中执行。

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install torch==2.0.1 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cu118
python -m pip install -r requirements.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

PyTorch 安装命令参照[官方历史版本说明](https://pytorch.org/get-started/previous-versions/#v201)。

## 2. 准备权重和视频

从[仓库 Releases](../../releases) 获取 `reproduction-weights.zip`，解压到仓库根目录，使三个权重落在下表的位置。

| 文件 | 仓库内放置位置 | 来源 |
| --- | --- | --- |
| yolov8n.pt | `ultralytics/yolo/v8/detect/yolov8n.pt` | Ultralytics YOLOv8n |
| yolov8s.pt | `ultralytics/yolo/v8/detect/yolov8s.pt` | Ultralytics YOLOv8s |
| ckpt.t7 | `ultralytics/yolo/v8/detect/deep_sort_pytorch/deep_sort/deep/checkpoint/ckpt.t7` | DeepSORT 外观特征权重 |
| MVI_20011.mp4 | `ultralytics/yolo/v8/detect/MVI_20011.mp4` | UA-DETRAC MVI_20011 图像序列转换得到 |

### 生成测试视频

在仓库根目录执行以下命令。脚本从 [Hugging Face 镜像](https://huggingface.co/datasets/kalyan1729/sentineledgedataset) 的固定版本获取 `MVI_20011` 序列的 664 张图像，并按编号顺序生成 960 × 540、25 FPS 的 MP4。视频会保存到上表位置。

```powershell
python -m pip install huggingface_hub==0.36.0
python prepare_mvi_20011.py
```

如果已经有该序列的图像，可直接指定包含 `img00001.jpg` 到 `img00664.jpg` 的目录，无需安装下载依赖。

```powershell
python prepare_mvi_20011.py --frames-dir "D:\path\to\MVI_20011"
```

脚本会保留已有的 `MVI_20011.mp4`。图像来自 Wen 等人的 [UA-DETRAC 数据集](https://sites.google.com/view/daweidu/projects/ua-detrac)。重新编码得到的视频与论文原始 MP4 的编码可能不同，检测输出可能略有差异。

## 3. 运行实验

```powershell
# 运行基准实验
powershell -NoProfile -ExecutionPolicy Bypass -File .\ultralytics\yolo\v8\detect\run_all_experiments.ps1 -BaselineOnly

# 运行论文的四组实验
powershell -NoProfile -ExecutionPolicy Bypass -File .\ultralytics\yolo\v8\detect\run_all_experiments.ps1
```

| 实验名 | 检测权重 | 置信度阈值 |
| --- | --- | --- |
| baseline_yolov8n_conf05 | yolov8n.pt | 0.5 |
| model_yolov8s_conf05 | yolov8s.pt | 0.5 |
| conf03 | yolov8n.pt | 0.3 |
| conf07 | yolov8n.pt | 0.7 |

基准组同时作为阈值 0.5 的对照。四组均使用 `imgsz=640`、`iou=0.7` 和同一份 `deep_sort.yaml`。脚本从仓库载入本地 Ultralytics 代码，复跑输出写到 `ultralytics/yolo/v8/detect/runs/reproduction/`。重复运行时程序会为已存在的结果目录追加编号。

## 4. 查看结果

论文对应的原始记录位于 `ultralytics/yolo/v8/detect/runs/detect/` 下的四个实验目录。`frame_stats.csv` 记录各帧的检测框数量、确认轨迹数量和检测模块耗时。`tracks.csv` 记录确认轨迹的帧号、ID、类别与边界框。`experiment_config.json` 记录实验参数和原运行环境。复跑时还会生成带跟踪标记的视频，检测模块计时会随运行环境变化。

## 上游项目

- [Muhammad Moin Faisal 的 YOLOv8-DeepSORT-Object-Tracking](https://github.com/MuhammadMoinFaisal/YOLOv8-DeepSORT-Object-Tracking)
- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics)，本项目内置版本为 8.0.3，源码标注 GPL-3.0。
- [ZQPei 的 deep_sort_pytorch](https://github.com/ZQPei/deep_sort_pytorch)，该组件保留原 MIT 许可及作者说明。
