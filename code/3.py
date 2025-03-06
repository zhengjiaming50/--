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
keywords = ["按林地保护等级面积统计表"]  # 自定义关键词列表

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
    f"""2. 严格模仿以下格式，生成类似的文本，禁止生成特殊符号（'*'或'#'），禁止生成解释性语言（例如：'注：XXX'）：三、其他有关情况说明
（一）项目使用林地权属情况说明
经调查，项目拟长期使用林地面积34.3006hm²，均为集体林地。项目建设使用林地权属清楚，不存在纠纷问题。
（二）违法使用林地情况说明
在调查过程中未发现用地单位有先使用林地后办手续或擅自改变林地用途现象，也未见有非法采伐林木的行为，用地单位按国家林地管理的法律法规要求正在办理使用林地手续。
（三）特定建设项目情况说明
项目不属于特定建设项目，属于经营性项目，拟使用林地保护等级为Ⅲ级、Ⅳ级，符合《建设项目使用林地审核审批管理办法》（国家林业局令第35号）第四条第一款第（五）项“战略性新兴产业项目，勘查项目，大中型矿山，符合相关旅游规划的生态旅游开发项目，可以使用Ⅱ级及以下保护林地。其他工矿、仓储建设项目和符合规划的经营性项目，可以使用Ⅲ级及以下保护林地”的规定。
（四）其它情况说明
（1）项目使用林地性质
项目拟使用林地均为永久性使用，不涉及临时占用林地。
（2）项目重叠情况说明
项目与南宁新江经无圩至崇左扶绥一级路（扶绥那列至华阳路口段）改建市政道路工程项目（桂林审政字〔2018〕665号）重叠林地面积0.0170hm²，该部分林地已由上述项目申报并获批，因此不列入本项目使用林地范围统计。
（2）项目现状地类、树种与数据库地类、树种不一致
项目建设使用林地是以扶绥县2018年度森林督查暨森林资源管理一张图成果为基础数据进行外业调查，使用林地地块主要属性因子原则上直接依据“一张图”确定，使其与林地“一张图”属性保持一致。根据外业调查发现项目建设使用林地部分小班属性因子与林地“一张图”属性不一致，现将林地“一张图”与现状调查不一致的主要小班和地块进行分析说明，
（五）可行性报告时效性说明
项目使用林地现场实地调查时间是2020年4月9日，于2020年4月份完成报告编制。因此，所执行的有关规定和标准均为2020年4月以前颁布的法规和标准。本报告时效期12个月，若超过时效上报，林地现状发生变化，或者因国家使用林地相关的法律法规发生变化，应以国家最新的法律法规为准，对本报告进行补充完善或重新编写后才能作为上报材料。

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
    output_file = os.path.join(output_dir, '3.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")