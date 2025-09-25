import os
import subprocess


import os
os.environ["UNO_PATH"] = "/usr/lib/libreoffice/program"


# def convert_doc_to_docx(input_file, output_dir):
#     """
#     将 .doc 文件转换为 .docx 文件。
    
#     :param input_file: 输入的 .doc 文件路径
#     :param output_dir: 输出目录
#     """
#     # 确保输出目录存在
#     os.makedirs(output_dir, exist_ok=True)
    
#     # 获取文件名（不含扩展名）
#     file_name = os.path.splitext(os.path.basename(input_file))[0]
    
#     # 构造输出文件路径
#     output_file = os.path.join(output_dir, f"{file_name}.docx")
    
#     try:
#         # 使用 unoconv 命令进行转换
#         subprocess.run(
#             ["unoconv", "-f", "docx", "-o", output_file, input_file],
#             check=True
#         )
#         print(f"成功转换: {input_file} -> {output_file}")
#     except subprocess.CalledProcessError as e:
#         print(f"转换失败: {input_file}, 错误: {e}")

# def batch_convert_docs_to_docx(input_dir, output_dir):
#     """
#     批量将 .doc 文件转换为 .docx 文件。
    
#     :param input_dir: 包含 .doc 文件的输入目录
#     :param output_dir: 输出目录
#     """
#     # 遍历输入目录中的所有 .doc 文件
#     for file_name in os.listdir(input_dir):
#         if file_name.endswith(".doc"):
#             input_file = os.path.join(input_dir, file_name)
#             convert_doc_to_docx(input_file, output_dir)

# if __name__ == "__main__":
#     # 输入目录和输出目录
#     input_directory = input('请给出word文档所在路径：')
#     output_directory = input('请给出word文档输出路径：')
    
    
#     # 批量转换
#     batch_convert_docs_to_docx(input_directory, output_directory)


import subprocess
from pathlib import Path

def convert_doc_to_docx(input_folder, output_folder):
    # 确保输出文件夹存在
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # 遍历所有.doc文件
    for doc_path in Path(input_folder).glob('*.doc'):
        try:
            # 使用LibreOffice进行转换
            subprocess.run([
                'libreoffice', '--headless', '--convert-to', 'docx',
                '--outdir', output_folder, str(doc_path)
            ], check=True, capture_output=True, text=True)
            print(f"转换成功: {doc_path}")
        except subprocess.CalledProcessError as e:
            print(f"转换失败: {doc_path}")
            print(f"错误信息: {e.stderr}")

if __name__ == "__main__":
    input_folder = input("请输入源文件夹路径: ").strip()
    output_folder = input("请输入输出文件夹路径: ").strip()
    convert_doc_to_docx(input_folder, output_folder)