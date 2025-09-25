import subprocess
from pathlib import Path

def convert_xls_to_xlsx(input_folder, output_folder):
    # 确保输出文件夹存在
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # 遍历所有.xls文件（不包含.xlsx）
    for xls_path in Path(input_folder).glob('*.xls'):
        try:
            # 使用LibreOffice进行转换
            subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'xlsx',
                '--outdir', output_folder, str(xls_path)
            ], check=True, capture_output=True, text=True)
            print(f"转换成功: {xls_path}")
        except subprocess.CalledProcessError as e:
            print(f"转换失败: {xls_path}")
            print(f"错误信息: {e.stderr}")

if __name__ == "__main__":
    input_folder = input("请输入源文件夹路径: ").strip()
    output_folder = input("请输入输出文件夹路径: ").strip()
    convert_xls_to_xlsx(input_folder, output_folder)