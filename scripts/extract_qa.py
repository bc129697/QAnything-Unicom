#### 本脚本用于qanything导出的数据中，对知识库中的qa文件进行数据提取，并保存为excel文件






import os
import json
import pandas as pd

def extract_question_answer(json_data):
    """
    从 JSON 数据中提取 question 和 answer 字段。
    """
    try:
        # 提取 faq_dict 中的 question 和 answer
        faq_dict = json_data.get("kwargs", {}).get("metadata", {}).get("faq_dict", {})
        question = faq_dict.get("question", "")
        answer = faq_dict.get("answer", "")
        return question, answer
    except Exception as e:
        print(f"Error extracting data: {e}")
        return None, None

def process_json_files(folder_path):
    """
    遍历文件夹中的所有 JSON 文件，提取 question 和 answer。
    """
    results = []
    
    # 遍历文件夹中的所有文件
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".json"):  # 只处理 JSON 文件
                file_path = os.path.join(root, file_name)
                try:
                    # 读取 JSON 文件内容
                    with open(file_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                    
                    # 提取 question 和 answer
                    question, answer = extract_question_answer(json_data)
                    if question and answer:  # 如果成功提取到数据
                        results.append({"question": question, "answer": answer})
                        if "引用" in answer:
                            print(f"File {file_path} contains reference.")
                            print(f"Question: {question}")
                            print(f"Answer: {answer}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
    
    return results

def save_to_excel(data, output_file):
    """
    将提取的数据保存为 Excel 文件。
    """
    df = pd.DataFrame(data)
    df.to_excel(output_file, index=False)
    print(f"Data saved to {output_file}")






import sys
if __name__ == "__main__":
    # 输入文件夹路径和输出 Excel 文件路径
    folder_path = "path/to/your/json/files" if len(sys.argv) < 2 else sys.argv[1] # 替换为你的 JSON 文件夹路径
    output_file = "output.xlsx"              # 输出的 Excel 文件名

    # 处理 JSON 文件并提取数据
    extracted_data = process_json_files(folder_path)

    # # 保存为 Excel 文件
    # if extracted_data:
    #     save_to_excel(extracted_data, output_file)
    # else:
    #     print("No valid data found to save.")