# 添加时间限制
import datetime
import glob

# 设置时间限制
limit_date = datetime.datetime(2025, 3, 8)
current_date = datetime.datetime.now()

if current_date > limit_date:
    raise Exception("该脚本在2025年2月25日之后无法使用。")

import os
from openai import OpenAI

# 设置API密钥
client = OpenAI(
    api_key = "a40b7290-ad68-44f5-861a-9b33dd26e794",  # 替换为您的实际API密钥
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

# 设置主题和文件夹

folder_path = os.path.join(os.path.dirname(__file__), "output_texts")
md_folder_path = "md_output"  # 添加MD文件夹路径
os.makedirs(folder_path, exist_ok=True)  # 新增目录创建

# 设置要查找的关键词列表 - 包含这些关键词的MD文件会被选中作为参考
keywords = ["林地按使用林地类型面积蓄积统计表","使用林地因子调查表"]  # 自定义关键词列表

# 读取匹配关键词的所有md文件并合并内容
def read_filtered_md_files(folder_path, keywords):
    all_text = ""
    matched_files = []
    
    # 检查目录是否存在
    if not os.path.exists(folder_path):
        print(f"错误: 目录 '{folder_path}' 不存在!")
        print(f"当前工作目录: {os.getcwd()}")
        print(f"尝试创建目录...")
        try:
            os.makedirs(folder_path)
            print(f"成功创建目录: {folder_path}")
        except Exception as e:
            print(f"创建目录失败: {str(e)}")
        return all_text
    
    # 获取所有md文件
    md_files = glob.glob(os.path.join(folder_path, "*.md"))
    
    # 静默过滤大文件（200KB限制）
    MAX_SIZE_KB = 200
    md_files = [f for f in md_files if os.path.getsize(f) <= MAX_SIZE_KB * 1024]
    
    if not md_files:
        print(f"警告: 在 '{folder_path}' 目录中未找到任何MD文件!")
        return all_text
    
    print(f"目录中共有 {len(md_files)} 个MD文件")
    
    # 列出所有文件供参考
    print("所有可用的MD文件:")
    for file_path in md_files:
        print(f" - {os.path.basename(file_path)}")
    
    # 改进版关键词匹配 - 处理部分、单词和模糊匹配
    for file_path in md_files:
        file_name = os.path.basename(file_path)
        
        # 精确匹配（包含完整关键词）
        for keyword in keywords:
            if keyword.lower() in file_name.lower():
                if file_path not in matched_files:
                    matched_files.append(file_path)
                    print(f"完全匹配 '{keyword}': {file_name}")
        
        
    # 如果仍然没有匹配，使用第一个MD文件
    if not matched_files and md_files:
        first_file = md_files[0]
        matched_files.append(first_file)
        print(f"\n未找到匹配文件，将使用第一个MD文件: {os.path.basename(first_file)}")
    
    # 读取匹配的文件
    for file_path in matched_files:
        file_name = os.path.basename(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                all_text += f"\n--- 文件：{file_name} ---\n"
                all_text += file.read() + "\n"
        except Exception as e:
            print(f"读取文件时出错: {file_path}, 错误: {str(e)}")
    
    print(f"找到 {len(matched_files)} 个匹配的文件:")
    for file_path in matched_files:
        print(f" - {os.path.basename(file_path)}")
        
    return all_text.strip()

# 读取文件夹中的所有txt文件并合并内容
def read_all_txt_files(folder_path):
    all_text = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):  # 只读取txt文件
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    all_text += file.read() + "\n"  # 保留换行符
            except Exception as e:
                print(f"读取文件时出错: {file_path}, 错误: {str(e)}")
    return all_text.strip()

# 从文件夹读取内容
folder_content = read_all_txt_files(folder_path)

# 从文件夹读取匹配的md文件内容
md_content = read_filtered_md_files(md_folder_path, keywords)

# 合并所有内容
combined_content = folder_content
if md_content:
    combined_content += "\n\n=== MD文件内容 ===\n" + md_content

# 检查是否找到任何内容
if not combined_content.strip():
    user_input = input("未找到任何参考内容，是否继续生成报告？(y/n): ").strip().lower()
    if user_input != 'y':
        print("程序退出")
        exit(1)
    else:
        combined_content = "无匹配的参考文件内容"

# 生成详细提示词
prompt_content = (
    f"请根据以下要求生成报告：\n"
    f"1. 以下是参考信息：\n{combined_content}\n"
    f"""2. 严格模仿以下格式，生成类似的文本，禁止生成特殊符号（'*'或'#'），禁止生成解释性语言（例如：'注：XXX'）：（三）项目拟使用林地概况
1.拟使用林地的空间位置、面积
根据崇左市扶绥县2018年度森林督查暨森林资源管理一张图成果及外业调查，项目拟使用林地位于崇左市扶绥县龙头乡腾广村6林班94、114、116、118、129、133、134、230、237、246、247、249、250、251、252、253、254、255、257、292小班，涉及1个村1个林班20个小班22个地块。拟使用林地面积34.3006hm2。项目建设使用林地的具体空间位置、面积详见附表A。
2.拟使用林地及林木权属
项目拟长期使用林地面积34.3006hm2，均为集体林地，属扶绥县龙头乡腾广村集体所有；林木面积32.0303hm2，林木权属均为个人。
林地、林木权属清楚、无争议。
3.拟使用林地主要建设内容使用林地情况
项目拟使用林地面积34.3006hm²，拟使用林地均用于长乐小镇（包含康养文化教育等、公共服务配套、配电、供水、燃气设施和道路等）建设。
4.拟使用林地期限
永久性使用。
5.拟使用林地需要采伐林木情况
项目建设使用林地面积34.3006hm²，涉及林木面积32.0303hm2，蓄积量3405m3，树种为巨尾桉、龙眼。拟使用林地需采伐巨尾桉蓄积量3405m3、龙眼55株。

"""
)

# 使用读取的内容进行AI处理
try:
    stream = client.chat.completions.create(
        model = "deepseek-r1-250120",
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt_content},
        ],
        stream=True
    )

    # 修改输出目录到代码根目录下
    # 假设代码根目录为当前文件所在目录的上一级目录
    project_root = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(project_root, 'output_reports')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, '1.3.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")