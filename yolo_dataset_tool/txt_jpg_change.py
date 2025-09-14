import os

def batch_rename_and_update_class(
    folder_path: str,
    custom_suffix: str = None,  # 要添加的自定义后缀（None 时不重命名）
    old_class_id: int = None,  # 旧类别编号（可选）
    new_class_id: int = None,  # 新类别编号（可选）
    delete_class_id: int = None,  # 需要删除的类别编号（可选）
):
    """
    批量修改 YOLO 标注文件的类别序号，删除指定类别，并可选地重命名图像及标注文件。
    """
    if not os.path.isdir(folder_path):
        print(f"错误：目录 '{folder_path}' 不存在！")
        return
    
    rename_count = 0
    update_count = 0
    delete_count = 0

    for filename in os.listdir(folder_path):
        file_base, file_ext = os.path.splitext(filename)
        file_path = os.path.join(folder_path, filename)

        # ------------------- 更新类别编号 / 删除类别行（仅适用于 .txt 标注文件） -------------------
        if file_ext == ".txt":
            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                
                updated_lines = []
                modified = False

                for line in lines:
                    parts = line.strip().split()
                    if len(parts) > 0 and parts[0].isdigit():  # 确保是 YOLO 格式
                        class_id = int(parts[0])

                        # 如果要删除该类别，跳过该行
                        if delete_class_id is not None and class_id == delete_class_id:
                            modified = True
                            continue

                        # 如果需要修改类别编号
                        if old_class_id is not None and new_class_id is not None and class_id == old_class_id:
                            parts[0] = str(new_class_id)
                            modified = True
                    
                    updated_lines.append(" ".join(parts) + "\n")

                # 统计修改情况
                if modified:
                    with open(file_path, "w") as f:
                        f.writelines(updated_lines)
                    
                    if delete_class_id is not None:
                        delete_count += 1
                        print(f"类别删除: {filename} (移除类别 {delete_class_id})")
                    if old_class_id is not None and new_class_id is not None:
                        update_count += 1
                        print(f"类别更新: {filename} ({old_class_id} -> {new_class_id})")

            except Exception as e:
                print(f"错误：无法更新文件 {filename}，错误信息：{e}")

        # ------------------- 重命名文件（仅当 custom_suffix 非空时） -------------------
        if custom_suffix and file_ext.lower() in [".jpg", ".jpeg", ".png", ".txt"]:
            new_filename = f"{file_base}{custom_suffix}{file_ext}"
            new_path = os.path.join(folder_path, new_filename)

            # 避免文件名冲突
            counter = 1
            while os.path.exists(new_path):
                new_filename = f"{file_base}{custom_suffix}_{counter}{file_ext}"
                new_path = os.path.join(folder_path, new_filename)
                counter += 1

            try:
                os.rename(file_path, new_path)
                rename_count += 1
                print(f"重命名: {filename} -> {new_filename}")
            except Exception as e:
                print(f"错误：无法重命名 {filename}，错误信息：{e}")

    print(f"\n处理完成！\n类别更新的文件数: {update_count}\n删除类别的文件数: {delete_count}\n重命名的文件数: {rename_count}")

# 示例调用 "E:\数据集\GREAT_dataset\0000\images\train\0" "C:\0-Work\yolo_dataset\dataset_AB\labels\000000096_AA.txt"
folder_path = r"C:\\0-Work\\yolo_dataset\\dataset_AB\\processed\\"  # 文件夹路径
custom_suffix = "B"                # None 时不重命名
old_class_id = None                     # 旧类别编号（可选）
new_class_id = None                     # 新类别编号（可选）
delete_class_id = None                   # 需要删除的类别编号（可选）

batch_rename_and_update_class(
    folder_path=folder_path,
    custom_suffix=custom_suffix,
    old_class_id=old_class_id,
    new_class_id=new_class_id,
    delete_class_id=delete_class_id,
)


