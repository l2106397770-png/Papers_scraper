import os
import pandas as pd
import argparse

def merge_csv_files(input_dir='../papers', output_file='merged_result.csv'):
    """
    合并目录下所有CSV文件，重新生成ID列（从1开始递增）
    
    参数:
    input_dir: 输入CSV文件所在目录，默认../papers
    output_file: 输出合并后的CSV文件名，默认merged_result.csv
    """
    # 定义目标列顺序（排除原ID列，最后会重新添加）
    target_columns = ['Title', 'Authors', 'Keywords', 'Abstract', 'PDF_Link', 'Type']
    
    # 存储所有CSV数据的列表
    all_data = []
    
    # 检查输入目录是否存在
    if not os.path.exists(input_dir):
        print(f"错误: 输入目录 {input_dir} 不存在！")
        return
    
    # 遍历目录下所有文件
    for filename in os.listdir(input_dir):
        # 只处理CSV文件
        if filename.endswith('.csv'):
            file_path = os.path.join(input_dir, filename)
            print(f"正在读取文件: {file_path}")
            
            try:
                # 读取CSV文件，指定编码（处理中文问题）
                df = pd.read_csv(
                    file_path,
                    sep=',',  # 假设是制表符分隔，根据实际情况可改为','
                    encoding='utf-8-sig',
                    usecols=target_columns  # 只读取需要的列，排除原ID
                )
                
                # 检查列是否完整
                missing_cols = set(target_columns) - set(df.columns)
                if missing_cols:
                    print(f"警告: 文件 {filename} 缺少列 {missing_cols}，已跳过该文件")
                    continue
                
                # 确保列顺序正确
                df = df[target_columns]
                
                # 添加到数据列表pip
                all_data.append(df)
                
            except Exception as e:
                print(f"错误: 读取文件 {filename} 时出错 - {str(e)}")
                continue
    
    # 检查是否有有效数据
    if not all_data:
        print("错误: 没有找到可合并的有效CSV文件")
        return
    
    # 合并所有数据
    merged_df = pd.concat(all_data, ignore_index=True, sort=False)
    
    # 重新生成ID列（从1开始递增）
    merged_df.insert(0, 'ID', range(1, len(merged_df) + 1))
    
    # 保存合并后的文件
    merged_df.to_csv(
        output_file,
        sep='\t',  # 保持制表符分隔，可改为',' if needed
        index=False,
        encoding='utf-8-sig'
    )
    
    print(f"\n合并完成！")
    print(f"总记录数: {len(merged_df)}")
    print(f"输入目录: {os.path.abspath(input_dir)}")
    print(f"输出文件: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='合并指定目录下的所有CSV文件，重新生成ID列')
    
    # 添加参数：输入目录（默认../papers）
    parser.add_argument(
        '-i', '--input-dir',
        type=str,
        default='../papers',
        help='CSV文件所在目录（默认：../papers）'
    )
    
    # 添加参数：输出文件（默认merged_result.csv）
    parser.add_argument(
        '-o', '--output-file',
        type=str,
        default='../papers/merge/merged_result.csv',
        help='合并后的输出文件名（默认：merged_result.csv）'
    )
    
    # 添加参数：CSV分隔符（默认制表符，可选逗号）
    parser.add_argument(
        '-s', '--separator',
        type=str,
        default='\t',
        choices=['\t', ','],
        help='CSV文件分隔符（默认：制表符\\t，可选：逗号,）'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 覆盖分隔符设置（如果用户指定了逗号）
    if args.separator == ',':
        # 重新定义read_csv和to_csv的分隔符
        import pandas as pd
        original_read_csv = pd.read_csv
        original_to_csv = pd.DataFrame.to_csv
        
        def custom_read_csv(*args, **kwargs):
            kwargs['sep'] = ','
            return original_read_csv(*args, **kwargs)
        
        def custom_to_csv(*args, **kwargs):
            kwargs['sep'] = ','
            return original_to_csv(*args, **kwargs)
        
        pd.read_csv = custom_read_csv
        pd.DataFrame.to_csv = custom_to_csv
    
    # 调用合并函数
    merge_csv_files(
        input_dir=args.input_dir,
        output_file=args.output_file
    )