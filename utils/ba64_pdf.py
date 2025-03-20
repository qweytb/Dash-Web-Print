from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import base64
from io import BytesIO


def base64_to_pdf_base64(base64_data):
    # 解码输入的 Base64 图片数据
    image_data = base64.b64decode(base64_data)
    img = Image.open(BytesIO(image_data))

    # 如果图像是 RGBA 格式，转换为 RGB 并确保白色背景
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))  # 白色背景
        background.paste(img, (0, 0), img)  # 将 RGBA 图像粘贴到白色背景上
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    img_width, img_height = img.size

    # A4 的标准尺寸
    pdf_width, pdf_height = A4  # pdf_width = 595, pdf_height = 842

    # 在内存中创建 PDF
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)  # 直接使用 A4 尺寸

    # 计算图片缩放比例，保持宽高比例
    scale = min(pdf_width / img_width, pdf_height / img_height)
    new_width = img_width * scale
    new_height = img_height * scale

    # 绘制白色背景
    c.setFillColorRGB(1, 1, 1)  # 白色
    c.rect(0, 0, pdf_width, pdf_height, fill=1, stroke=0)  # 覆盖整个页面

    # 将图像数据加载到 ImageReader
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="JPEG", quality=95)  # 保存为高质量 JPEG
    img_byte_arr.seek(0)  # 将指针重置到开头
    img_reader = ImageReader(img_byte_arr)

    # 将图片绘制到 PDF 页面，居中显示
    x = (pdf_width - new_width) / 2  # 水平居中
    y = (pdf_height - new_height) / 2  # 垂直居中
    c.drawImage(img_reader, x, y, width=new_width, height=new_height)

    # 保存 PDF 到内存缓冲区
    c.save()

    # 将 PDF 数据转换为 Base64
    pdf_buffer.seek(0)  # 重置缓冲区指针到开头
    pdf_base64 = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    pdf_buffer.close()  # 关闭缓冲区

    return pdf_base64
