import pandas as pd
import os
import re
import glob

# 配置参数
INPUT_FOLDER = 'excel_files'  # 输入文件夹，存放Excel文件
OUTPUT_FOLDER = os.path.join('code', 'md_output')   # 输出到程序根目录下的code文件夹

def excel_to_md(excel_file, output_dir=OUTPUT_FOLDER, filter_method='default', columns_to_exclude=None, columns_to_keep=None, exclude_patterns=None, target_table_pattern='建设项目使用林地因子调查表'):
    """将单个Excel文件中的指定表转换为Markdown文件
    
    参数:
        excel_file (str): Excel文件路径
        output_dir (str): 输出目录
        filter_method (str): 过滤方法，可选值为 'default', 'exclude', 'include', 'pattern'
        columns_to_exclude (list): 要排除的列索引列表 (基于0的索引)
        columns_to_keep (list): 要保留的列索引列表 (基于0的索引)
        exclude_patterns (list): 要排除的列名模式列表 (正则表达式)
        target_table_pattern (str): 目标表格标题的匹配模式
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print(f"处理文件: {excel_file}")
    
    # 设置默认值
    if columns_to_exclude is None:
        columns_to_exclude = []  # 例如 [16, 17] 表示排除第17和18列(0-based索引)
    
    if columns_to_keep is None:
        columns_to_keep = []  # 例如 [0, 1, 2, 3] 表示只保留前4列
    
    if exclude_patterns is None:
        exclude_patterns = []  # 例如 ['保护等级', '备注']
    
    try:
        # 读取Excel文件中的所有表
        excel = pd.ExcelFile(excel_file)
        
        # 遍历所有表
        for sheet_name in excel.sheet_names:
            print(f"  处理表: {sheet_name}")
            
            # 读取表数据 - 不使用标题行
            df = pd.read_excel(excel, sheet_name=sheet_name, header=None)
            
            # 如果表为空则跳过
            if df.empty or len(df) < 2:  # 确保至少有两行(标题行和列头行)
                print(f"  表 {sheet_name} 行数不足，已跳过")
                continue
            
            # 检查这个表是否是我们要找的"建设项目使用林地因子调查表"
            title = str(df.iloc[0, 0]).strip()
            if not re.search(target_table_pattern, title):
                print(f"  表 {sheet_name} 标题 '{title}' 不匹配目标模式 '{target_table_pattern}'，已跳过")
                continue
            
            print(f"  找到目标表: {title}")
            
            # 应用列过滤方法
            if filter_method == 'exclude' and columns_to_exclude:
                # 方案一：排除指定列索引
                print(f"  使用排除列索引方案，排除列: {columns_to_exclude}")
                all_columns = list(range(len(df.columns)))
                filtered_columns = [col for col in all_columns if col not in columns_to_exclude]
                df = df.iloc[:, filtered_columns]
                
            elif filter_method == 'include' and columns_to_keep:
                # 方案二：只保留指定列索引
                print(f"  使用保留列索引方案，保留列: {columns_to_keep}")
                df = df.iloc[:, columns_to_keep]
                
            elif filter_method == 'pattern' and exclude_patterns:
                # 方案三：基于第二行（索引1）列标题内容排除列
                print(f"  使用列标题模式排除方案，排除包含: {exclude_patterns}")
                # 获取第二行作为列标题 (索引1)
                header_row = df.iloc[1]
                cols_to_drop = []
                
                # 检查每一列的标题
                for col_idx, col_value in enumerate(header_row):
                    col_str = str(col_value)
                    # 如果列标题匹配任何排除模式，记录该列索引
                    if any(re.search(pattern, col_str) for pattern in exclude_patterns):
                        cols_to_drop.append(col_idx)
                
                if cols_to_drop:
                    print(f"  根据模式排除列索引: {cols_to_drop}")
                    all_columns = list(range(len(df.columns)))
                    filtered_columns = [col for col in all_columns if col not in cols_to_drop]
                    df = df.iloc[:, filtered_columns]
            
            # 构建markdown内容
            md_content = f"# {title}\n\n"
            
            # 将所有数据转换为markdown表格（包括标题行）
            md_content += df.to_markdown(index=False, tablefmt='pipe', colalign=['left']*len(df.columns))
            
            # 进一步处理，移除多余空格
            lines = md_content.split('\n')
            for i in range(len(lines)):
                # 替换连续的空格为单个空格，并移除|后和|前的空格
                lines[i] = re.sub(r'\|\s+', '|', lines[i])
                lines[i] = re.sub(r'\s+\|', '|', lines[i])
                # 替换nan为空字符串
                lines[i] = lines[i].replace('|nan', '|')
            
            md_content = '\n'.join(lines)
            
            # 保存为md文件 - 清理文件名中的非法字符
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
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
    
    # 提供三种方案示例
    print("\n=== 以下是三种过滤方案，请选择一种取消注释使用 ===")
    
    for excel_file in excel_files:
        # 方案一：直接排除指定列索引（适合当您知道列索引的情况）
        # 例如排除第20, 21, 22列（0-based索引，根据您的表格实际情况调整）
        # excel_to_md(excel_file, filter_method='exclude', columns_to_exclude=[19, 20, 21])
        
        # 方案二：只保留指定列（适合当您知道要保留哪些列的情况）
        # 例如只保留前19列（根据您的表格实际情况调整）
        # excel_to_md(excel_file, filter_method='include', columns_to_keep=list(range(19)))
        
        # 方案三：根据列名排除（最灵活的方案，推荐使用）
        # 自动查找并排除包含以下关键词的列
        excel_to_md(excel_file, filter_method='pattern', exclude_patterns=['保护等级', '备注', '原森林类型'])
    
    print(f"所有Excel文件处理完成！请在 {os.path.abspath(OUTPUT_FOLDER)} 查看生成的Markdown文件。")

if __name__ == "__main__":
    process_all_excel_files()
