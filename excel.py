import pandas as pd
import os
import re
import glob

# 配置参数
INPUT_FOLDER = 'excel_files'  # 输入文件夹，存放Excel文件
OUTPUT_FOLDER = os.path.join('code', 'md_output')   # 输出到程序根目录下的code文件夹

def excel_to_md(excel_file, output_dir=OUTPUT_FOLDER):
    """将单个Excel文件中的所有表转换为Markdown文件"""
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"处理文件: {excel_file}")
    
    try:
        # 读取Excel文件中的所有表
        excel = pd.ExcelFile(excel_file)
        
        # 遍历所有表
        for sheet_name in excel.sheet_names:
            print(f"  处理表: {sheet_name}")
            
            # 读取表数据 - 不使用标题行
            df = pd.read_excel(excel, sheet_name=sheet_name, header=None)
            
            # 如果表为空则跳过
            if df.empty or len(df) < 1:
                print(f"  表 {sheet_name} 为空，已跳过")
                continue
                
            # 获取第一行第一个单元格作为文件名和标题
            # 这里会提取合并单元格的值，因为合并单元格的值通常出现在第一个位置
            file_title = str(df.iloc[0, 0]).strip()
            
            # 如果标题为空，则使用sheet名称
            if not file_title or pd.isna(file_title):
                file_title = sheet_name
                print(f"  表 {sheet_name} 第一行第一列为空，使用表名作为文件名")
            else:
                print(f"  提取到标题: {file_title}")
            
            # 构建markdown内容
            md_content = f"# {file_title}\n\n"
            
            # 将所有数据转换为markdown表格（包括标题行）
            md_content += df.to_markdown(index=False)
            
            # 保存为md文件 - 清理文件名中的非法字符
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", file_title)
            file_path = os.path.join(output_dir, f"{safe_title}.md")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            print(f"  已生成: {file_path}")
    except Exception as e:
        print(f"  处理文件 {excel_file} 时出错: {str(e)}")

def process_all_excel_files():
    """处理指定文件夹中的所有Excel文件"""
    # 确保输入文件夹存在
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"已创建输入文件夹: {INPUT_FOLDER}，请将Excel文件放入此文件夹")
        return
    
    # 查找所有Excel文件
    excel_files = glob.glob(os.path.join(INPUT_FOLDER, "*.xlsx"))
    excel_files.extend(glob.glob(os.path.join(INPUT_FOLDER, "*.xls")))
    
    if not excel_files:
        print(f"在 {INPUT_FOLDER} 文件夹中未找到Excel文件。")
        print(f"请将Excel文件放在 {os.path.abspath(INPUT_FOLDER)} 文件夹中。")
        return
    
    print(f"找到 {len(excel_files)} 个Excel文件")
    
    # 处理每个Excel文件
    for excel_file in excel_files:
        excel_to_md(excel_file)
    
    print(f"所有Excel文件处理完成！请在 {os.path.abspath(OUTPUT_FOLDER)} 查看生成的Markdown文件。")

if __name__ == "__main__":
    process_all_excel_files()
