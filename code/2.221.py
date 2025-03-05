import os
from openai import OpenAI

# 设置API密钥
client = OpenAI(
    api_key = "a40b7290-ad68-44f5-861a-9b33dd26e794",  # 替换为您的实际API密钥
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

# 设置主题和文件夹

folder_path = os.path.join(os.path.dirname(__file__), "output_texts")

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

# 生成详细提示词
prompt_content = (
    f"请根据以下要求生成报告：\n"
    f"1. 以下是参考信息：\n{folder_content}\n"
    f"""2. 严格模仿以下格式：（二）拟使用林地情况说明
项目拟使用林地面积34.3006hm2，拟使用林地均用于长乐小镇（包含康养文化教育等、公共服务配套、配电、供水、燃气设施和道路等）建设。
（三）专项调查结果
1.涉及使用重点生态区域等的林地情况
项目没有涉及自然保护区、森林公园、湿地公园、风景名胜区、世界自然遗产地、重要水源保护地、沿海基干林带等重点生态区域等范围内的林地。
2.涉及使用城市规划区范围内的林地情况
根据《崇左市城市总体规划（2017～2035年）》，项目拟使用林地范围不属于城市规划区范围内。
3.重点保护野生植物
按照相关技术规程和认定标准，对项目区进行全面调查，项目区内没有古树名木分布，也没有国家或广西重点保护野生植物。
4.重点保护野生动物
对项目区进行全面调查，调查结果未发现项目区及周边范围内有国家或广西重点保护野生动物。
生成类似的文本，禁止生成特殊符号（'**'或'#'），禁止生成解释性语言（例如：‘注：XXX’）
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
    output_file = os.path.join(output_dir, '2.22.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")