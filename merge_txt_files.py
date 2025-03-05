import os
import glob
import re
import argparse
import sys
import time

def version_sort_key(filename):
    """
    提取文件名中的版本号部分用于排序
    例如: @2.131.txt -> [2, 131]
    """
    # 移除路径，只取文件名
    basename = os.path.basename(filename)
    # 移除扩展名
    basename = os.path.splitext(basename)[0]
    # 移除@前缀(如果有)
    if basename.startswith('@'):
        basename = basename[1:]
        
    # 将版本号分割并转换为整数列表
    parts = []
    for part in basename.split('.'):
        try:
            # 尝试将部分转换为整数
            parts.append(int(part))
        except ValueError:
            # 如果不是纯数字，则保留原样
            parts.append(part)
    
    return parts

def merge_txt_files(input_dir, output_file, add_filename=False, encoding='utf-8'):
    """
    将指定目录下的所有txt文件按版本号排序后合并成一个文件
    
    参数:
        input_dir (str): 包含txt文件的目录路径
        output_file (str): 合并后的输出文件路径
        add_filename (bool): 是否在每个文件内容前添加文件名标题
        encoding (str): 文件编码
    """
    # 获取所有txt文件
    txt_files = glob.glob(os.path.join(input_dir, '*.txt'))
    
    if not txt_files:
        print(f"错误: 在 {input_dir} 目录中未找到txt文件")
        return False
    
    # 按版本号排序
    txt_files = sorted(txt_files, key=version_sort_key)
    
    print(f"找到 {len(txt_files)} 个txt文件，按版本号排序合并中...")
    print("排序后的文件列表:")
    for i, file in enumerate(txt_files):
        print(f"{i+1}. {os.path.basename(file)}")
    
    try:
        # 合并文件
        with open(output_file, 'w', encoding=encoding) as outfile:
            for txt_file in txt_files:
                print(f"处理: {txt_file}")
                try:
                    with open(txt_file, 'r', encoding=encoding) as infile:
                        if add_filename:
                            outfile.write(f"\n\n# 文件: {os.path.basename(txt_file)}\n\n")
                        outfile.write(infile.read())
                except Exception as e:
                    print(f"警告: 处理文件 {txt_file} 时出错: {str(e)}")
        
        print(f"合并完成！输出文件: {output_file}")
        return True
    except Exception as e:
        print(f"错误: 合并文件时发生异常: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='按版本号排序合并TXT文件')
    parser.add_argument('-i', '--input', default='output_reports', help='输入目录路径(默认: output_reports)')
    parser.add_argument('-o', '--output', default='报告.txt', help='输出文件路径(默认: merged_report.txt)')
    parser.add_argument('--add-filename', action='store_true', help='在合并文件中添加原文件名')
    parser.add_argument('--encoding', default='utf-8', help='文件编码(默认: utf-8)')
    
    args = parser.parse_args()
    
    # 检查输入目录是否存在
    if not os.path.exists(args.input):
        print(f"错误: 输入目录 {args.input} 不存在")
        return 1
    
    # 确保输出目录存在
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"错误: 无法创建输出目录: {str(e)}")
            return 1
    
    # 执行合并
    success = merge_txt_files(
        args.input, 
        args.output, 
        args.add_filename,
        args.encoding
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    start_time = time.time()
    exit_code = main()
    elapsed_time = time.time() - start_time
    print(f"程序运行时间: {elapsed_time:.2f}秒")
    sys.exit(exit_code)
