import os
from openai import OpenAI
import glob

# 设置API密钥
client = OpenAI(
    api_key = "a40b7290-ad68-44f5-861a-9b33dd26e794",  # 替换为您的实际API密钥
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

# 设置主题和文件夹（用于存放md文件和输出内容）

md_folder_path = "md_output"  # 直接使用相对路径

# 设置要查找的关键词列表 - 包含这些关键词的MD文件会被选中作为参考
keywords = ["使用林地按林地保护等级面积统计表", "使用林地分森林类别面积统计表"]  # 自定义关键词列表

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
        
        # 如果没有精确匹配，尝试匹配每个关键词的部分
        if file_path not in matched_files:
            for keyword in keywords:
                for part in keyword.split():
                    if len(part) >= 2 and part.lower() in file_name.lower():
                        if file_path not in matched_files:
                            matched_files.append(file_path)
                            print(f"部分匹配 '{part}': {file_name}")
    
    # 如果仍然没有匹配，尝试模糊匹配（任意关键字的字符在文件名中）
    if not matched_files:
        for file_path in md_files:
            file_name = os.path.basename(file_path)
            for keyword in keywords:
                if any(char in file_name.lower() for char in keyword.lower() if ord(char) > 127):  # 只检查中文字符
                    if file_path not in matched_files:
                        matched_files.append(file_path)
                        print(f"字符匹配 '{keyword}': {file_name}")
    
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

project_root = os.path.dirname(os.path.dirname(__file__))
output_dir = os.path.join(project_root, 'output_reports')
os.makedirs(output_dir, exist_ok=True)

# 从文件夹读取匹配的md文件内容
md_content = read_filtered_md_files(md_folder_path, keywords)

if not md_content:
    user_input = input("未找到匹配内容，是否继续生成报告？(y/n): ").strip().lower()
    if user_input != 'y':
        print("程序退出")
        exit(1)
    else:
        md_content = "无匹配的参考文件内容"

# 生成详细提示词
prompt_content = (
    f"请根据以下要求生成报告：\n"
    f"1. 以下是参考信息：\n{md_content}\n"
    f"""2. 严格模仿以下格式：（二）使用林地分析
 项目拟长期使用林地面积34.3006hm²。
按林地保护等级：Ⅲ级保护林地面积34.0204hm²、Ⅳ级保护林地面积0.2802hm²；按森林类别：重点商品林地面积34.0204hm²、一般商品林地面积0.2802hm²；按林地类型：用材林林地面积34.054hm²、经济林林地面积0.2462hm²；使用林地地貌类型均为丘陵，林地质量等级为Ⅱ级、Ⅲ级，林地质量一般。本项目属于经营性项目，项目拟使用林地符合《建设项目使用林地审核审批管理办法》（国家林业局令第35号）第四条第一款第（五）项“战略性新兴产业项目，勘查项目，大中型矿山，符合相关旅游规划的生态旅游开发项目，可以使用Ⅱ级及以下保护林地。其他工矿、仓储建设项目和符合规划的经营性项目，可以使用Ⅲ级及以下保护林地”的规定。

生成类似的文本，禁止生成特殊符号（'*'或'#'），禁止生成解释性语言（例如：'注：XXX'）
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
    
    output_file = os.path.join(output_dir,  '4.2.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)
    
    print(f"\n\n报告已生成并保存至: {output_file}")

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}") 