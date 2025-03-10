import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from tqdm import tqdm
import threading

# 配置路径
base_dir = os.path.dirname(os.path.abspath(__file__))
output_image_folder = os.path.join(base_dir, 'code', 'output_images')
output_text_folder = os.path.join(base_dir, 'code', 'output_texts')
os.makedirs(output_image_folder, exist_ok=True)
os.makedirs(output_text_folder, exist_ok=True)

def pdf_to_images_and_extract_text(pdf_path):
    pdf_document = fitz.open(pdf_path)
    for page_number in range(len(pdf_document)):
        page = pdf_document.load_page(page_number)
        # 设置分辨率，增加清晰度
        zoom_x = 2.0  # 水平缩放因子
        zoom_y = 2.0  # 垂直缩放因子
        mat = fitz.Matrix(zoom_x, zoom_y)  # 创建缩放矩阵
        pix = page.get_pixmap(matrix=mat, dpi=300)  # 使用更高的 DPI
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # 保存图片
        image_filename = f"{os.path.basename(pdf_path)}_page_{page_number + 1}.png"
        image_path = os.path.join(output_image_folder, image_filename)
        img.save(image_path)

        # 处理图片以提取文本
        process_image(image_path)

def process_image(image_path):
    # 使用PIL打开图片
    img = Image.open(image_path)
    
    # 使用Tesseract进行OCR识别
    result_text = pytesseract.image_to_string(img, lang='chi_sim')  # 使用简体中文识别
    
    # 生成输出文件名
    output_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}.txt"
    output_path = os.path.join(output_text_folder, output_filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_text)

def find_and_process_files(folder_path):
    files_to_process = []
    # 支持的图片格式
    image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_lower = file.lower()
            file_path = os.path.join(root, file)
            if file_lower.endswith('.pdf'):
                files_to_process.append(('pdf', file_path))
            elif any(file_lower.endswith(ext) for ext in image_extensions):
                files_to_process.append(('image', file_path))

    for file_type, file_path in tqdm(files_to_process, desc="Processing files"):
        if file_type == 'pdf':
            pdf_to_images_and_extract_text(file_path)
        else:
            # 对于图片文件，直接进行OCR处理
            # 生成在output_text_folder中的输出文件名
            output_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.txt"
            output_path = os.path.join(output_text_folder, output_filename)
            # 如果输出文件不存在，则处理图片
            if not os.path.exists(output_path):
                process_image(file_path)

if __name__ == "__main__":
    folder_path = os.path.join(os.path.dirname(__file__), "pdf")
    find_and_process_files(folder_path)