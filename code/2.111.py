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
    f"""2. 严格模仿以下格式,禁止生成特殊符号（'**'或'#'），禁止生成解释性语言（例如：‘注：XXX’）：二、使用林地现状调查
（一）使用林地调查结果
1.调查基本情况
（1）林地现状调查准备
①资料准备
扶绥县2018年度森林督查暨森林资源管理一张图成果、项目用地范围红线图。
②调查范围确认
将建设项目用地红线图叠加到扶绥县2018年度森林督查暨森林资源管理一张图成果上，确定项目使用林地范围。抄录林地“一张图”原小班号，并按林地地块界线，按顺序编排使用林地地块序号，制作建设项目使用林地外业调查图。
③项目区内自然保护区、森林公园等的确认
通过空间位置，确认项目区内是否涉及自然保护区（保护小区）、森林公园、湿地公园、风景名胜区、世界自然遗产地、重要水源保护地、沿海基干林带等重点生态区域等，确认项目区是否在城市规划区范围内。
（2）调查技术方法
①属性因子调查
a.使用林地地块主要属性因子确定
包括地类、林地权属、林地保护等级、森林类别、使用林地类型、林种、起源等属性因子，原则上直接依据林地“一张图”确定，使其与林地“一张图”属性保持一致。出现林地“一张图”中主要属性因子与现地不一致情况时，在不改变林地“一张图”小班界线的前提下，实地调查林地“一张图”原小班的属性，并进行对比分析，单独形成报告说明。当地林业主管部门对确实需要变更林地“一张图”有关界限或属性因子的，应当按林地“一张图”变更程序予以变更。
b.使用林地地块其他属性因子调查
通过实地调查填写，如优势树种（组）、龄组、平均树高、平均胸径、郁闭度（覆盖度）、活立木每公顷蓄积、经济(竹)林株数等。其中，活立木每公顷蓄积调查采用全林实测法或标准地法调查，经济(竹)林株数采用小样圆法、标准地法或全林实测法调查，调查方法参照《森林资源规划设计调查技术规程》（GB/T 26424-2010）及《广西壮族自治区伐区调查设计技术规程（2013年）》执行。
②专项调查
a.重点生态区域调查
通过实地调查和查阅相关资料，查清项目建设是否涉及自然保护区、森林公园、湿地公园、风景名胜区，若涉及上述区域林地，则调查涉及的功能区，调查是否有相关管理部门的意见材料。
b.古树名木、国家和省级重点保护野生植物调查
采用野外调查与座谈访问、查阅资料相结合的方法，调查记载项目区内古树名木、国家和省级重点保护野生植物的名称（学名）、位置、胸径、树高、树龄、保护等级、生境等，以及拟采取的处置措施。
c.国家和省级重点保护野生动物及其栖息地调查
采用查阅资料、社会调查和专家咨询的方法，进行项目区及周边野生动物生境情况调查，提出拟采取的保护措施。
③其他调查
a.林地权属争议调查
重点调查是否存在争议、争议情况、解决方案等。
b.违法使用林地情况调查
调查是否存在擅自改变林地用途、未批先用等违法使用林地行为及查处情况等。对于未批先用且确需办理使用林地手续的建设项目，应当按照县级林地保护利用规划档案资料，按实际使用林地年度确认违法使用林地的范围，确定未批先用面积及相关属性因子等，并在使用林地可行性报告中进行单独说明。
（3）质量管理
手持外业图判图并利用GPS辅助定位，采用GIS制图，求算面积，确保项目建设位置、使用林地面积准确。
（4）相关说明
①林地保护利用规划林地落界相关属性因子分类及填写规定见《林地保护利用规划林地落界技术规程》和《县级林地保护利用规划编制技术规程》。
②使用林地地类按乔木林地、竹林地、特殊灌木林地、一般灌木林地、疏林地、未成林造林地、苗圃地、采伐迹地、火烧迹地、宜林地、其他林地等划分地类。
③古树名木和重点保护野生动植物调查，参照《野生动植物资源调查技术规程》执行。
④计量单位：面积单位为hm²，保留4位小数；蓄积单位为m³，保留整数；林木（竹）株数（经济林、竹林及幼树填写），单位为株，保留整数。
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
    output_file = os.path.join(output_dir, '2.111.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")