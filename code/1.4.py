# 添加时间限制
import datetime

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
os.makedirs(folder_path, exist_ok=True)  # 新增目录创建

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
    f"""2. 严格模仿以下格式：（四）编写依据
1.法律依据
（1）《中华人民共和国森林法》（2009年修正）；
（2）《中华人民共和国土地管理法》（2004年修正）；
（3）《中华人民共和国野生动物保护法》（2016年修订）；
（4）《中华人民共和国环境保护法》（2014年修订）；
（5）《中华人民共和国水土保持法》（2010年修订）；
（6）《中华人民共和国城乡规划法》（2015年修正）。
2.法规依据
（1）《中华人民共和国森林法实施条例》（2018年修订）；
（2）《中华人民共和国陆生野生动物保护实施条例》（2016年修订）；
（3）《中华人民共和国野生植物保护条例》（2017年修订）；
（4）《中华人民共和国水土保持法实施条例》（2011年修订）；
（5）《广西壮族自治区实施<中华人民共和国土地管理法>办法》（2001年）；
（6）《广西壮族自治区实施<中华人民共和国森林法>办法》（2016年）；
（7）《广西壮族自治区环境保护条例》（2016年修订）。
3.行政依据
（1）《建设项目使用林地审核审批管理办法》（国家林业局令第35号）；
（2）《国务院关于全国林地保护利用规划纲要（2010-2020年）的批复》（国函〔2010〕69号）；
（3）《国家林业局关于修改部分部门规章的决定》（国家林业局令第42号）；
（4）《国家林业局关于印发<建设项目使用林地审核审批管理规范>和<使用林地申请表>、<使用林地现场查验表>的通知》（林资发〔2015〕122号）；
（5）《自治区人民政府关于广西壮族自治区林地保护利用规划（2010－2020年）的批复》（桂政函〔2012〕302号）；
（6）《财政部国家林业局关于调整森林植被恢复费征收标准引导节约集约利用林地的通知》（财税〔2015〕122号）；
（7）《自治区财政厅林业厅关于调整我区森林植被恢复费征收标准引导节约集约利用林地的通知》（桂财税〔2016〕42号）；
（8）《广西壮族自治区林业局办公室关于启用2018年度森林督查暨森林资源管理一张图成果的通知》（桂林办资字〔2019〕16号）；
（9）《国土资源部国家发展和改革委员会关于发布实施〈限制用地项目目录（2012年本）〉和〈禁止用地项目目录（2012年本）〉的通知》（国土发〔2012〕98号）；
（10）《广西壮族自治区发展和改革委员会关于印发<广西第二批重点生态功能区县产业准入负面清单（试行）>的通知》（桂发改规划〔2017〕1652号）；
（11）《自治区林业厅关于认真审查建设项目使用林地申报材料重点内容的通知》（桂林政发〔2016〕7号）。
（12）《广西壮族自治区林业局 广西壮族自治区财政厅关于广西自治区级以上公益林落界调整成果的批复》(桂林发〔2020〕6号)。
4.技术标准、规范依据
（1）《建设项目使用林地可行性报告编制规范》（LY/T 2492-2015）；
（2）《国家重点保护野生动物名录》（2003年修改）；
（3）《国家重点保护野生植物名录》（2001年修改）；
（4）《广西壮族自治区第一批重点保护野生植物名录》（桂政发〔2010〕17号）；
（5）《野生动植物资源调查技术规程》（LY/T 1820—2009）；
（6）《林地保护利用规划林地落界技术规程》（LY/T1955-2011）；
（7）《县级林地保护利用规划编制技术规程》（LY/T 1956－2011）；
（8）《县级林地保护利用规划制图规范》（LY/T 2009－2012）；
（9）《林业地图图式》（LY/T 1821－2009）；
（10）《森林资源规划设计调查技术规程》（GB/T 26424—2010）；
（11）《广西壮族自治区伐区调查设计技术规程》（桂林政发〔2013〕17号）；
（12）《广西完善自治区级以上公益林区划界定技术操作细则》（2010年）；
（13）《广西第二次古树名木资源普查技术细则（试行）》（2016年）。
5.项目相关批复文件
 （1）扶绥县发展和改革局《广西壮族自治区投资项目备案证明》（项目代码：2020-451421-88-03-016343）；
（2）《扶绥县自然资源局关于扶绥恒大文化旅游康养城疗养项目的规划选址意见》。
6.技术成果材料
（1）扶绥县2018年度森林督查暨森林资源管理一张图成果；
（2）扶绥县自治区级以上公益林落界调整成果材料；
（3）扶绥县天然商品林落界成果材料；
（4）《广西壮族自治区扶绥县林地保护利用规划（2010～2020年）》；
（5）广西壮族自治区扶绥县2012年林地保护利用规划林地落界成果；
（6）《崇左市城市总体规划（2017～2035年）》；
（7）《扶绥县土地利用总体规划(2010～2020年)》；
（8）《中国-东盟南宁空港扶绥经济区总体规划(2019～2035年)（修编）》。
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
    output_file = os.path.join(output_dir, '1.4.txt')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                f.write(content)

except Exception as e:
    print(f"错误类型: {type(e).__name__}")
    print(f"错误详情: {str(e)}")