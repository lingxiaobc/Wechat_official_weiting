---
name: minimalist-ip-cover-generator
description: 为公众号文章生成 21:9 超宽中文封面，沿用暖象牙色与低饱和珊瑚红、青绿的极简二维视觉，并准确复用项目中的猫咪 IP。标题必须完整且无遮挡；猫咪可以随标题改变动作和姿势，但角色身份特征不可改变；每次生成后必须执行比例、文字、遮挡和角色一致性视觉检测。不用于普通信息图或不含该 IP 的通用封面。
---

# 极简猫咪 IP 公众号封面

为公众号文章生成一张 21:9 超宽横版封面。封面应在手机缩略图中仍能看清标题，并让猫咪 IP 与文章主题产生动作上的关联，但不能以重新设计角色为代价。

生成位图时使用 `imagegen` 技能及其默认内置生成工具。技能触发后，明确告诉用户将使用猫咪原图作为身份锚点，并在生成后执行视觉检测。

## 必需输入与默认行为

- 必需：文章标题原文。
- 可选：副标题、猫咪动作、猫咪所在左右位置、额外主题符号和输出目录。
- 用户没有指定动作时，根据标题选择一个简单、可读、与主题直接相关的动作，不增加新角色或复杂故事。
- 用户没有指定输出目录时，将最终采用版本保存到项目的 `image/covers/`。
- 只有用户明确要求时，才把封面插入文章或替换已有图片。

## 先检查角色与风格基准

每次生成前必须使用 `view_image` 查看：

1. `references/ip-character-master.jpg`：角色身份的最高优先级锚点。
2. `../../../image/covers/understanding-rag-vs-capability-cover.png`：21:9 构图、标题层级和整体画风基准；文件存在时才查看。

如需进一步校准配色，可选择查看 `../../../image/infographics/01-understanding-vs-capability.png`。不要为了参考风格而加载无关图片。

向图像生成工具传入参考图时，必须明确标注：

- Image 1：角色身份参考，决定猫咪长相和服饰。
- Image 2：封面风格参考，只决定配色、留白、字体层级和二维平面语言，不复制原有标题、图标或布局内容。

角色原图与以往生成图不一致时，以 `references/ip-character-master.jpg` 为准。

## 不可变化的角色特征

下列特征属于身份约束，每张封面都必须保留并可辨认：

- 白色虎斑猫，粗黑手绘轮廓。
- 大头、短小圆润身体和四肢的原始比例。
- 大号长方形黑框眼镜与灰色椭圆瞳孔。
- 额头、双颊和尾巴上的黑色虎斑条纹。
- 小鼻子、短竖线和下分叉构成的克制嘴部造型。
- 灰色人字纹西装外套与白色内搭。
- 胸前原子符号吊坠。
- 原子球顶端的法杖。
- 弯曲、带条纹的尾巴。
- 黑、白、灰为角色主体色，不把猫咪整体改成封面强调色。

不允许更换眼镜、服装、吊坠、法杖或物种；不增加帽子、耳机、领带、背包等新配饰；不改变脸型、耳朵比例或头身比例。

## 可以变化的动作与姿势

猫咪可以根据标题进行动作适配，例如：

- 用法杖指向标题、流程或目标。
- 阅读教程、思考、观察、检查结果或操作抽象界面。
- 站立、轻微侧身、前倾、迈步或举起另一只爪子示意。
- 通过轻微眉眼和嘴部变化表现困惑、专注、恍然大悟或确认。

动作变化必须满足：完整脸部和眼镜可见；西装、吊坠、法杖和条纹尾巴仍然清楚；不因姿势变化遮挡关键身份特征。默认展示完整身体，不裁掉耳朵、法杖顶端、脚或尾巴。

## 画幅与排版

- 画幅：21:9 横版，宽高比为 7:3。接受生成工具原生尺寸带来的极小像素误差，但实测比例与 21:9 的偏差不得超过 0.5%。
- 标题：使用用户提供的原文，只出现一次；不自行添加副标题、作者名或英文口号。
- 字体：粗体、干净的中文无衬线字体，深海军蓝灰；必要的英文缩写保持原始大小写。
- 长标题优先分成两行，断行必须服从语义，不拆开专有名词或英文缩写。
- 默认采用双区构图：标题占画面约 62%–70%，猫咪占约 22%–28%，中间保留约 6%–10% 的安全间距。
- 长标题默认文字在左、猫咪在右；短标题或用户指定时可以反转，但仍需符合中文阅读顺序。
- 标题不得位于猫咪、法杖、尾巴或装饰图形的后方；角色与文字不能接触、穿插或重叠。
- 四周保留安全边距，避免公众号裁剪标题或角色。

## 视觉语言

- 暖象牙白或浅米白背景，带轻微哑光纸张质感。
- 低饱和珊瑚红、灰粉、青绿和海军蓝灰作为强调色。
- 二维扁平编辑插画、清晰轮廓、克制留白和明确视觉层级。
- 可以使用少量与标题相关的书本、灯泡、箭头、目标、路径或检查符号，但不得包含额外文字，且必须弱于标题和猫咪。
- 只借鉴纪念碑谷式的克制色彩和极简图形语言，不借鉴空间气质或空间结构。
- 禁止等距建筑、楼梯、平台、透视场景、不可能几何、视觉错觉、3D、复杂风景、霓虹色、玻璃拟态和装饰堆叠。

## 生成提示词骨架

将用户标题和动作设计填入以下骨架。`Text` 与角色身份约束必须逐字写清：

```text
Use case: ads-marketing
Asset type: WeChat Official Account article cover, ultra-wide header image

Input images:
- Image 1: authoritative IP character and identity anchor.
- Image 2: style and composition reference only; do not copy its text or content.

Primary request: Create one polished 21:9 ultra-wide landscape cover for an article about [主题].

Text (verbatim, render exactly once):
“[完整标题]”

Character identity invariants:
the same white tabby cat; black hand-drawn outlines; rectangular glasses; gray oval pupils; original facial proportions and stripes; gray herringbone blazer; white shirt; atom pendant; atom-topped wand; curved striped tail; original large-head short-body proportions. Do not redesign or recolor the character.

Character action:
[与标题相关的简单动作，以及法杖、吊坠、尾巴保持可见的要求]

Composition/framing:
exact 21:9 ultra-wide landscape; title zone [左/右]; complete cat zone [右/左]; 6%–10% clear gap; no overlap; no cropping; strong mobile thumbnail readability.

Style/medium:
minimalist flat 2D editorial cover; warm ivory paper-like background; muted coral, dusty rose, desaturated teal and soft navy-gray; clean hierarchy and generous negative space.

Constraints:
exact title, no invented text, cat identity matches Image 1, all character signatures visible, title and cat never overlap, no watermark, no extra characters, no isometric architecture, no impossible geometry, no 3D perspective, no visual clutter.
```

如果标题包含不常见英文缩写，应在提示词中额外说明字母和大小写，但输出仍保持标题原文，不添加连字符或拼读标记。

## 生成后的强制视觉检测

生成结果不能未经检查直接交付。先把候选图保存或复制到项目目录，再使用 `view_image` 查看原始清晰度版本，并完成以下检查：

### 1. 画幅检测

- 读取实际宽高并计算宽高比。
- 与 21:9 的偏差不超过 0.5%。
- 检查四周是否留有安全边距，猫咪是否完整。

### 2. 标题检测

- 逐字比对标题，确认没有错字、漏字、重复、乱码或模型自创文字。
- 检查中英文标点和英文缩写大小写。
- 标题只出现一次，所有字符清晰可见。
- 标题没有被猫咪、法杖、尾巴、图标或画面边缘遮挡。

### 3. IP 一致性检测

逐项核对：白色虎斑、粗黑轮廓、长方形眼镜、灰色瞳孔、额头与脸颊条纹、原始嘴部、灰色人字纹西装、白色内搭、原子吊坠、原子法杖、条纹弯尾、原始头身比例。

任何一项关键特征缺失、替换或明显变形，都判定为不合格。动作自然但角色不像原图，同样不合格。

### 4. 构图与缩略图检测

- 视线先落在标题，再自然移动到猫咪和辅助符号。
- 标题与猫咪各自处于独立区域，没有视觉竞争。
- 在缩小预览中，标题仍能快速识别，猫咪仍能被认作同一 IP。
- 装饰元素没有抢夺注意力或制造假箭头、假文字。

### 5. 风格检测

- 确认为暖色浅背景、低饱和珊瑚红与青绿、深蓝灰标题、二维扁平画风。
- 确认没有建筑、楼梯、等距空间、错视几何、3D 或花哨光效。
- 猫咪保持黑白灰身份色，且与背景自然融合。

## 失败处理与交付

- 标题错误、发生遮挡、角色失真或比例超差时，不得采用该版本。
- 迭代时只针对一个主要失败点修改提示词，并重复全部身份约束。
- 每张封面默认最多生成两次；仍不合格时，向用户说明失败点并询问是否继续。
- 不覆盖已有封面，除非用户明确要求；使用稳定英文文件名，并在冲突时增加 `-v2`、`-v3`。
- 最终回复必须报告：成品路径、实际尺寸与比例、视觉检测结果、最终提示词概要，以及使用内置 ImageGen 还是 CLI。
