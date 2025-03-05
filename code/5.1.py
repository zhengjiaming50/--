import os
from openai import OpenAI


# 设置API密钥
client = OpenAI(
    api_key = "a40b7290-ad68-44f5-861a-9b33dd26e794",  # 替换为您的实际API密钥
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

# 设置主题和文件夹

folder_path = os.path.join(os.path.dirname(__file__), "output_texts")
os.makedirs(folder_path, exist_ok=True)  # 新增目录创建

print(os.path.abspath(folder_path))
# 增加路径验证
print(f"正在访问目录：{os.path.abspath(folder_path)}")
if not os.listdir(folder_path):
    print("错误：目录为空，请放入txt文件")
    exit(1)

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

# 生成详细提示词时将文件内容嵌入进去
prompt_content = (
    f"请根据以下要求生成报告：\n"
    f"1. 以下是参考信息：\n{folder_content}\n"
    f"""2. 严格模仿以下格式，生成类似的文本，禁止生成特殊符号（'**'或'#'），禁止生成解释性语言（例如：‘注：XXX’）：五、森林植被恢复费测算
（一）测算目的
根据《中华人民共和国森林法》及其实施条例、《中华人民共和国土地管理法》等有关法律法规和文件规定，项目建设使用林地，项目业主必须依法交纳有关补偿费，目的是为了加强对林地的管理，运用法律、经济等手段控制林地的减少，保持生态环境，促进林业的可持续发展。
（二）测算依据
（1）《财政部国家林业局关于调整森林植被恢复费征收标准引导节约集约利用林地的通知》（财税〔2015〕122号)；
（2）《关于调整我区森林植被恢复费征收标准引导节约集约利用林地的通知》（桂财税〔2016〕42号)。
（三）测算标准
根据《财政部国家林业局关于调整森林植被恢复费征收标准引导节约集约利用林地的通知》（财税〔2015〕122号)和《关于调整我区森林植被恢复费征收标准引导节约集约利用林地的通知》（桂财税〔2016〕42号)。
（1）郁闭度0.2以上的乔木林（含采伐迹地、火烧迹地)、竹林地、苗圃地，每平方米10元；灌木林地、疏林地、未成林造林地，每平方米6元；宜林地，每平方米3元。
（2）国家和省级公益林地，按（1）款规定征收标准2倍征收。
（3）城市规划区的林地，按（1）、（2）款规定征收标准2倍征收。
（4）城市规划区外的林地，按占用征收林地建设项目性质实行不同征收标准，属于公共基础设施、公共事业和国防建设项目的，按照（1）、（2）款规定征收标准征收；属于经营性建设项目的，按照（1）、（2）款规定征收标准2倍征收。
（5）根据《崇左市城市总体规划（2017～2035年）》，项目拟使用林地范围不属于城市规划区范围内。
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

    # 创建输出文件夹
    # 修改输出目录到代码根目录下
    # 假设代码根目录为当前文件所在目录的上一级目录
    project_root = os.path.dirname(os.path.dirname(__file__))
    output_dir = os.path.join(project_root, 'output_reports')
    os.makedirs(output_dir, exist_ok=True)
    
    # 设置输出文件路径
    output_file = os.path.join(output_dir, '5.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)  # 保留控制台输出
                f.write(content)  # 写入文件

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")