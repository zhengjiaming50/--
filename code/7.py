import os
from openai import OpenAI

# 设置API密钥
client = OpenAI(
    api_key = "a40b7290-ad68-44f5-861a-9b33dd26e794",  # 替换为您的实际API密钥
    base_url = "https://ark.cn-beijing.volces.com/api/v3",
)

# 设置主题和文件夹（用于存放中间处理内容）

folder_path = os.path.join(os.path.dirname(__file__), "output_texts")
os.makedirs(folder_path, exist_ok=True)  # 确保保存原始txt文件的文件夹存在

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
    f"""2. 严格模仿以下格式：七、使用林地可行性结论
2020年4月，项目经扶绥县发展和改革局备案，取得《广西壮族自治区投资项目备案证明》（项目代码：2020-451421-88-03-016343）；2020年4月，项目取得《扶绥县自然资源局关于扶绥恒大文化旅游康养城疗养项目的规划选址意见》。
项目建设符合国家政策和产业发展，符合崇左市土地利用总体规划和扶绥县总体规划，符合扶绥县林地保护利用规划，符合《中国-东盟南宁空港扶绥经济区总体规划(2019～2035年)（修编）》用地规划，项目建设报批程序合法有效。项目建设依法使用部分的林地是必要的。
综合分析，项目为经营性项目，项目建设拟使用林地地类有乔木林地、采伐迹地、特殊灌木林地，森林类别为重点商品林地、一般商品林地，林地保护等级为Ⅲ级、Ⅳ级，符合《建设项目使用林地审核审批管理办法》（国家林业局令第35号）第四条第一款第（五）项"战略性新兴产业项目，勘查项目，大中型矿山，符合相关旅游规划的生态旅游开发项目，可以使用Ⅱ级及以下保护林地。其他工矿、仓储建设项目和符合规划的经营性项目，可以使用Ⅲ级及以下保护林地"的规定；同时，也符合《国家林业局关于印发<建设项目使用林地审核审批管理规范>和<使用林地申请表>、<使用林地现场查验表>的通知》（林资发〔2015〕122号）等法律法规的要求。本项目使用林地具有必要性和迫切性；使用林地的条件具备，拟采用的方案合理可行，拟采用的保护措施合理；使用林地的相关技术措施得当，对生态环境影响不大；对林地保护利用规划目标影响很小，符合林地保护利用规划；项目经济效益显著，同时兼顾社会、生态效益；项目建设使用林地对项目区域的生物多样性影响极小，项目使用林地后对项目区域林业发展影响不大。
因此，本项目建设使用林地是必要的、是可行的。

生成类似的文本，禁止生成特殊符号（'**'或'#'），禁止生成解释性语言（例如：'注：XXX'）
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
    output_file = os.path.join(output_dir, '7.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")