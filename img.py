from PIL import Image, ImageDraw

# 创建一个透明图像
image = Image.new('RGBA', (240, 55), (0, 0, 0, 0))

# 创建一个绘图对象
draw = ImageDraw.Draw(image)

# 绘制边框
border_width = 2
border_color = (255, 0, 0)  # 白色
draw.rectangle([(0, 0), (240 - 1, 55 - 1)], outline=border_color, width=border_width)

# 显示图像
image.show()