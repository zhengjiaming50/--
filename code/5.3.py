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

# 修改关键词列表为精确匹配内容
keywords = ["项目使用林地森林植被恢复费"]  # 核心特征词

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
    
    # 简化匹配逻辑 - 仅保留精确匹配
    for file_path in md_files:
        file_name = os.path.basename(file_path)
        # 严格匹配判断（包含完整关键词）
        for keyword in keywords:
            if keyword in file_name:  # 保持原样大小写匹配
                matched_files.append(file_path)
                print(f"精确匹配 '{keyword}': {file_name}")
                break  # 匹配到即跳出循环

    # 完全禁用部分匹配和模糊匹配
    # 如果没有匹配文件时的处理
    if not matched_files:
        print("\n未找到精确匹配文件，可选文件列表:")
        for idx, fp in enumerate(md_files, 1):
            print(f"{idx}. {os.path.basename(fp)}")
        
        # 添加手动选择功能
        try:
            choice = int(input("请输入要使用的文件编号（0表示退出）: "))
            if 1 <= choice <= len(md_files):
                matched_files.append(md_files[choice-1])
            else:
                exit()
        except:
            print("输入无效，程序退出")
            exit()
    
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
    f"""2. 模仿以下格式,禁止生成特殊符号（'**'或'#'），禁止生成解释性语言（例如：'注：XXX'）：（四）测算结果
项目属经营性项目，拟使用林地面积xx.xxxxhm²，森林植被恢复费xx.xxxx万元，即：
[分类名称]部分（[总面积]㎡）  
商品林地按地类分：  
▸ 乔木林地：[X]㎡×10元/㎡=[金额计算]元=_[万元转换]_  
...（其他地类同理）  
森林植被恢复费小计：[万元值]万元  
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
    
    output_file = os.path.join(output_dir,  '5.3.txt')
    
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