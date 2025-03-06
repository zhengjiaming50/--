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
keywords = ["项目使用林地森林植被恢复费"]  # 自定义关键词列表

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
    f"""2. 严格模仿以下，生成类似的文本，禁止生成特殊符号（'**'或'#'），禁止生成解释性语言，
    其次，避免使用“参考格式”里的独特数据（例如：恢复费用684.0424万元）（例如：‘注：XXX’）：
    最后，必须包含九个小标题，顺序不可调整：六、保障措施

（一）水土保持措施
①施工单位严格按照最大限度的考虑建设对环境的影响最小的施工方案进行施工，不能随意扩大开挖、弃土弃渣范围；做好废弃土石方的处理，以避免弃土掩埋林木、农田。
②建设施工过程中，应做好排水措施，以避免雨水对地表的冲刷而造成水土流失。
③合理安排施工季节，避免在雨季大规模施工，减少水土流失。
④项目区边界的边坡坡度应控制在相关规定以内，保护人畜活动安全和防止边坡坍塌，造成水土流失，同时相应挖水沟截水将其排出，以防止雨水冲刷边坡泥土，造成泥土流失。
⑤项目开工建设后，建设单位要按照环境保护和规划设计的要求，及时进行项目区周边绿化美化，尽快恢复周边森林植被，避免泥土裸露造成水土流失。
⑥要加强林地使用情况检查，防止用地单位或施工单位没及时采取水土保持措施或因施工造成的陡坡（陡壁）现象而造成水土流失。
（二）生物多样性保护措施
生物多样性包括生态系统多样性、物种多样性和遗传基因多样性三个层次，其中物种多样性是生物多样性的核心。本项目区涉及林地面积占项目区域林地面积比例不大，生境类型简单，生态系统的组成、功能简单。施工过程中采取以下保护措施即可：
①施工过程中一旦发现有重点保护野生动植物的存在，立即报告林业主管部门采取迁移措施加以保护。
②项目建设施工过程中，不许破坏作业区界外的森林及林下植被，注意保护植被。
③积极做好施工人员的环境保护意识教育，严禁乱砍滥伐树木，乱捕滥猎野生动物。
（三）生态环境保护措施
本项目拟使用林地面积占项目区域林地面积比例不大，所以生态环境保护措施主要是污染源（污染物）治理措施和水土保持措施。
①污染源（污染物）治理措施
施工现场产生的生活污水和生活垃圾，应设置集中及无害化处理设施，对垃圾实行日产日清。施工弃土应有妥善的处置方案，如构建挡土墙、植树绿化等，以避免扬尘、雨季流失而污染环境，减少对景观的不良影响。
②水土保持措施
各施工环节尽量不破坏植被资源，并要满足环境要求，对破坏的地表要及时进行植被恢复，并做好排水措施，防止水土严重流失现象发生。
（四）生态效能保护措施
项目建设使用林地对林地生态效能的影响是以人为主导和自然因素共同作用而成，项目建设后造成的项目区森林植被消失，导致项目区域林地涵养水源、保持水土等生态功能底下，不仅破坏了土壤的理化性状，还可能导致水土流失，严重的还可能导致崩塌、滑坡、泥石流等地质灾害，森林植被的消失还会导致局部地区气候、水文循环的改变。因此，需要采取相应保护措施保证项目区生态效能的稳定。
本项目拟使用林地面积34.3006hm²，因为拟使用林地所涉及植被都是常见物种，这部分林地的消失对项目区域的生态效益影响甚微，所以只需对项目区周边进行必要的绿化和异地森林植被恢复即可。
（五）地质水文保护措施
项目建设施工时注意做好排水措施，防止水土流失、崩塌等现象发生。现场施工人员的生活污水应建立临时化粪池进行集中处理，严禁直接排入水体。
（六）其他景观保护措施
项目建设对项目区域风景名胜和文物古迹不造成影响，项目建设设计是根据地形、地质情况，选择合理的施工方案，尽可能的避开林地区域，从而使得原有的自然景观得以最大限度的保留。随着施工期结束，在采取绿化工程措施以后，人工景观将逐步得到完善。
（七）古树名木保护措施
项目区内没有古树名木分布。
（八）森林植被恢复费征缴及使用情况
①根据《关于调整我区森林植被恢复费征收标准引导节约集约利用林地的通知》（桂财税〔2016〕42号)征收标准计算，项目建设使用林地森林植被恢复费用684.0424万元，用地单位足额缴纳森林植被恢复费，使森林植被恢复异地造林资金有保障。
②根据《中华人民共和国森林法》“森林植被恢复费专款专用，由林业主管部门依照有关规定统一安排植树造林，恢复森林植被，植树造林面积不得少于因占用、征用林地而减少的森林植被面积”的规定和“适地适树”的原则，用地单位足额交纳森林植被恢复费用于进行异地植树造林，恢复森林植被。
（九）森林植被异地恢复措施及落实情况
①用地单位按照使用林地的面积和国家规定的有关标准，足额缴纳森林植被恢复费，使森林植被恢复异地造林资金有保障。
②上级林业主管部门要定期督促、检查下级主管部门组织实施的异地造林恢复森林植被情况。
③根据《中华人民共和国森林法》及有关政策文件规定，用地单位缴纳的森林植被恢复费必须用于异地植树造林，专款专用，任何单位和个人都不得挪作他用。本项目植树造林经费全部来源于项目建设单位缴纳的森林植被恢复费。
④要加强对森林植被恢复费使用情况的监督和审计。
⑤做好造林作业设计，确定各项工程技术标准和种苗供应来源，加强对使用苗木的管理，切实保障造林中所使用的苗木全部为合格苗，以确保造林质量。
⑥造林施工期间，要严格按照设计的技术标准完成，施工管理人员要做好三个环节管理工作，即事先指导、中间检查、事后验收。
⑦造林后，要严格按照林业生产经营管理的各项制度加强管理，确保森林植被异地恢复造林成果。
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
    output_file = os.path.join(output_dir, '6.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")