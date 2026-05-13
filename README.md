# 萤火虫迷宫 Firefly Maze

这是一个使用 Python + Pygame 编写的中文图形界面迷宫游戏。玩家需要收集萤火虫、躲避或射击怪物，并在出口开启后逃出迷宫。

## 安装依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 运行游戏

```powershell
.\.venv\Scripts\python.exe src\main.py
```

## 中文字体

游戏会在 Pygame 初始化后尝试加载系统中文字体，优先匹配：

- 微软雅黑 `Microsoft YaHei`
- 黑体 `SimHei`
- 宋体 `SimSun`
- 新宋体 `NSimSun`
- 楷体 `KaiTi`
- 仿宋 `FangSong`

不会复制或提交系统字体文件。如果中文显示为方块，请在 Windows 中安装微软雅黑、黑体或宋体，或者在 `src/assets_loader.py` 的字体匹配列表中加入你系统已有的中文字体名称。

## 主菜单

菜单为中文界面，使用键盘操作：

- ↑ / ↓：选择
- Enter：确认
- Esc：返回

主菜单包含：

- 开始游戏
- 选择关卡
- 难度选择
- 设置
- 退出游戏

主菜单背景使用 `assets/menu_background.png`。如果文件不存在，游戏会生成一张夜色迷宫风格的占位背景；已有正式背景不会被覆盖。

## 难度

难度包含：

- 简单
- 普通
- 困难

不同难度会影响怪物数量、萤火虫数量、怪物追逐概率、怪物移动间隔、击杀得分、子弹冷却和最大子弹数。难度选择会保存到本地存档。

## 关卡

当前包含 5 个递进关卡：

- 第 1 关：教学入口
- 第 2 关：分岔灯廊
- 第 3 关：回声回廊
- 第 4 关：暗光曲径
- 第 5 关：萤火深巢

选择关卡界面会显示：

- 已通关
- 当前关卡
- 未解锁

未解锁关卡不能进入，确认时会提示“请先通过前面的关卡”。

## 游戏操作

- 移动：W/A/S/D 或方向键
- 射击：Space
- 静音/恢复音乐：M
- 游戏中暂停：Esc 或 Q
- 结束界面重新开始本关：R
- 结束界面返回主界面：Esc 或 Q

暂停菜单包含：

- 继续游戏
- 重新开始本关
- 返回主界面
- 退出游戏

暂停时怪物和子弹不会更新。

## 得分规则

- 收集萤火虫：+10
- 击杀怪物：
  - 简单：+5
  - 普通：+10
  - 困难：+15
- 移动不扣分。
- 分数最低为 0。

## 存档

本地存档文件：

```text
save_data.json
```

该文件已加入 `.gitignore`，不会提交到 Git。如果文件不存在，游戏会自动创建默认存档。

每个难度单独保存：

- `unlocked_levels`
- `completed_levels`
- `highest_unlocked_level`
- `last_level`

“开始游戏”会从当前难度下上一次失败、退出或返回主界面时所在的关卡继续。

## 音乐

背景音乐路径：

```text
assets/bgm.mp3
```

如果文件存在，游戏启动后会以音量 0.4 循环播放。如果文件不存在或 mixer 初始化失败，游戏只在控制台打印中文提示并继续运行。

## 素材

图片资源放在 `assets/`：

- `player.png`
- `monster.png`
- `firefly.png`
- `wall.png`
- `floor.png`
- `exit_closed.png`
- `exit_open.png`
- `menu_background.png`
- `bgm.mp3`

缺失的图片会生成简单占位图，不覆盖已有正式素材。tile 尺寸为 48x48，替换素材会自动缩放到该尺寸。

## 项目结构

```text
firefly-maze/
  README.md
  requirements.txt
  save_data.json        # 本地存档，已忽略
  src/
    main.py
    game.py
    render.py
    assets_loader.py
    audio.py
    difficulty.py
    levels.py
    save_data.py
    menu.py
    texts.py
    map_data.py
  assets/
  tests/
  tools/
```
