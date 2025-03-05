# 添加时间限制
import datetime
import glob

# 设置时间限制
limit_date = datetime.datetime(2025, 3, 4)
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
keywords = ["使用林地因子调查表","使用林地分森林类别按地类面积统计表"]  # 自定义关键词列表

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
    f"""2. 严格模仿以下格式，生成类似的文本，禁止生成特殊符号（'*'或'#'），禁止生成解释性语言（例如：'注：XXX'）：（三）使用林地生态影响分析
1.对生物多样性的影响分析
（1）对植物多样性的影响
经实地调查，项目区内没有国家或广西重点保护野生植物，没有古树名木的分布，植物种类和植被类型简单。项目建设使用林地将永久地改变其性质，使原有的植物消失，但消失的这些植被类型和植物种类都是项目区域植物区系的常见植被。项目建设虽会使这些植物资源总量有所减少，但组成本地区植物区系的各种植被种类及群落类型不会因此而发生大的变化，对项目区域植物多样性的负面影响极小。
因此，项目建设对国家或广西重点保护野生植物、古树名木没有影响，对项目区域植物多样性的负面影响很小。
（2）对动物多样性的影响
项目区位于崇左市扶绥县空港大道王村至扶绥边境段南侧，人为活动较频繁，林地上原生植物已不存在，生境类型简单。项目建设期间，由于各种人为活动和机器噪音，对周围的野生动物的正常活动及其栖息环境产生一定的影响，而且野生动物具有较强的流动性和迁徙性，在项目开工建设时，野生动物可以迁徙到项目区以外适合栖息的区域。
在项目建设后，由于其保护设施的阻隔，对两栖类、爬行类、兽类野生动物的活动将会产生一些不利影响，但不会影响它们的摄食、生存，以及种群的繁衍。
在项目区及周边范围内未发现国家和广西重点保护的野生动物分布。因此，项目建设对国家和广西重点保护的野生动物影响很小，对区域内野生动物的种群、数量的影响很小。
因此，项目建设对野生动植物影响不大，对动物多样性影响很小。
2.对森林生态效能的影响分析
项目建设拟使用的林地中，乔木林地面积31.7841hm²、特殊灌木林地面积0.2462hm²，林木主要是巨尾桉和龙眼，其生态效能较低。工程建设虽将导致这部分林地消失，从而使项目区内的地表植被丧失，但涉及植被都是常见物种，且项目建设完成后将对项目区进行绿化，因此它的消失对项目区域环境空气质量、气温变化和空气湿度等气候因子影响极小，对森林生态效能影响不大。
因此，建设项目使用林地对项目区及周边区域的生态环境质量影响极小。
3.对自然景观的影响分析
项目建设在施工过程中，土地平整、破坏植被，造成山坡裸露，弃土弃渣等会对景观造成一定影响，使这些景观由自然景观向人工景观转化。随着项目建设完成，通过对项目区内采取相关措施，及时进行植物绿化等，这些影响将逐步得到消除。
因此，项目建设使用林地对项目区域内自然景观影响不大。
（四）使用林地可行性分析
1.项目建设必要性分析
项目位于崇左市扶绥县空港大道王村至扶绥边境段南侧，东至吴圩—那桐高速、南至德古岭、西至王村、北至空港大道，交通便利，地理位置优越，项目建设有效提高康养文化产业设施及基础设施水平，促进康养文化产业发展；另外为当地提供一定的就业岗位，带动当地群众发展相关产业,推动当地经济快速增长。
项目经扶绥县发展和改革局备案，取得《广西壮族自治区投资项目备案证明》（项目代码：2020-451421-88-03-016343）；项目取得《扶绥县自然资源局关于扶绥恒大文化旅游康养城疗养项目的规划选址意见》，确认项目用地范围。项目建设符合国家政策和产业发展，符合崇左市城市总体规划，符合扶绥县林地保护利用规划，符合《中国-东盟南宁空港扶绥经济区总体规划(2019～2035年)（修编）》用地规划，项目建设依法使用部分的林地是必要的。
综上所述，项目建设依据充分且具有必要性，而由于项目建设选址不可避免的使用到林地，因而项目建设使用林地也具有必要性。
2.项目选址合理性分析
项目位于崇左市扶绥县空港大道王村至扶绥边境段南侧，道路、水、电、网络等均可通达。项目区不属于《崇左市城市总体规划（2017～2035年）》确定的城市建设用地范围内，符合土地利用总体规划。2020年4月，项目取得《广西壮族自治区投资项目备案证明》（项目代码：2020-451421-88-03-016343），备案项目建设情况；2020年4月，项目取得《扶绥县自然资源局关于扶绥恒大文化旅游康养城疗养项目的规划选址意见》，确认用地范围。项目属经营性项目，拟使用林地森林类别为重点商品林地、一般商品林地，林地保护等级为Ⅲ级、Ⅳ级，没有涉及自然保护区、森林公园、湿地公园、风景名胜区、世界自然遗产地、重要水源保护地、沿海基干林带等重点生态区域等范围内的林地。项目建设从上报、审核等均按照国家有关规定、标准进行勘测、研究、论证。使用林地符合《建设项目使用林地审核审批管理办法》（国家林业局令第35号）的规定。
综上所述，项目选址合理。
3.项目用地规模及使用林地规模分析
项目建设使用土地总面积37.3421hm²，综合考虑《崇左市城市总体规划（2017～2035年）》以及造价成本，结合政府对土地开发强度的指标进行开发，项目建设在规划选址等均已考虑集约用地，最终确定建设方案，项目用地规模合理。根据扶绥县2018年度森林督查暨森林资源管理一张图成果及外业调查结果，项目建设拟使用林地面积34.3006hm²，因此项目建设使用林地已是不可避免，但使用林地面积占扶绥县林地总面积的比重不大。
4.项目使用林地争议情况及违法使用林地情况分析
项目建设拟使用林地权属为集体，林地权属清楚，无争议。
在调查过程中未发现用地单位有先使用林地后办手续或擅自改变林地用途现象，也未见有非法采伐林木的行为，用地单位按照国家有关林地管理的要求，向当地林业主管部门提出建设用地申请。符合林地管理有关法律、法规的规定要求。
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
    output_file = os.path.join(output_dir, '4.3.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")