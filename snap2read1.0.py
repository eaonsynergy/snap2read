#Version 1.4
import os
import zipfile
import shutil
from py7zr import SevenZipFile
from PIL import Image, ImageOps

def crop_image(image_path, crop_margins):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            left = crop_margins.get("left", 0)
            right = crop_margins.get("right", 0)
            top = crop_margins.get("top", 0)
            bottom = crop_margins.get("bottom", 0)

            cropped = img.crop((left, top, width - right, height - bottom))
            return cropped
    except Exception as e:
        print(f"Erreur lors du traitement de l'image {image_path} : {e}")
        return Image.new("RGB", (width, height), color="red")

def create_pdf(folder_path, output_path, crop_margins):
    images = []
    for file in sorted(os.listdir(folder_path)):
        if file.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
            file_path = os.path.join(folder_path, file)
            cropped_image = crop_image(file_path, crop_margins)
            images.append(ImageOps.fit(cropped_image, (cropped_image.width, cropped_image.height), method=Image.Resampling.LANCZOS))

    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:], resolution=300)
        print(f"PDF généré : {output_path}")

def create_cbz(folder_path, output_path, crop_margins):
    with zipfile.ZipFile(output_path, 'w') as cbz:
        for file in sorted(os.listdir(folder_path)):
            if file.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                file_path = os.path.join(folder_path, file)
                cropped_image = crop_image(file_path, crop_margins)
                temp_path = os.path.join(folder_path, f"temp_{file}")
                cropped_image.save(temp_path)
                cbz.write(temp_path, arcname=file)
                os.remove(temp_path)
    print(f"CBZ généré : {output_path}")

def create_cb7(folder_path, output_path, crop_margins):
    with SevenZipFile(output_path, 'w') as cb7:
        for file in sorted(os.listdir(folder_path)):
            if file.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
                file_path = os.path.join(folder_path, file)
                cropped_image = crop_image(file_path, crop_margins)
                temp_path = os.path.join(folder_path, f"temp_{file}")
                cropped_image.save(temp_path)
                cb7.write(temp_path, arcname=file)
                os.remove(temp_path)
    print(f"CB7 généré : {output_path}")

def create_cbr(folder_path, output_path, crop_margins):
    if not shutil.which("rar"):
        print("L'outil CLI RAR n'est pas disponible sur ce système.")
        return

    temp_folder = os.path.join(folder_path, "temp")
    os.makedirs(temp_folder, exist_ok=True)

    for file in sorted(os.listdir(folder_path)):
        if file.lower().endswith(('.jpg', '.jpeg', '.webp', '.png')):
            file_path = os.path.join(folder_path, file)
            cropped_image = crop_image(file_path, crop_margins)
            cropped_image.save(os.path.join(temp_folder, file))

    command = ["rar", "a", "-ep", output_path, os.path.join(temp_folder, "*")]
    os.system(' '.join(command))

    shutil.rmtree(temp_folder)
    print(f"CBR généré : {output_path}")

def process_subfolders_to_archives(parent_folder, archive_type="pdf", crop_margins=None):
    crop_margins = crop_margins or {"top": 0, "bottom": 0, "left": 0, "right": 0}
    subfolders = [
        f for f in os.listdir(parent_folder) if os.path.isdir(os.path.join(parent_folder, f))
    ]

    if not subfolders:
        print("Aucun sous-dossier trouvé dans le dossier parent.")
        return

    for subfolder in subfolders:
        subfolder_path = os.path.join(parent_folder, subfolder)
        output_archive = os.path.join(parent_folder, f"{subfolder}.{archive_type}")
        print(f"Traitement du dossier : {subfolder}")

        if archive_type == "pdf":
            create_pdf(subfolder_path, output_archive, crop_margins)
        elif archive_type == "cbz":
            create_cbz(subfolder_path, output_archive, crop_margins)
        elif archive_type == "cb7":
            create_cb7(subfolder_path, output_archive, crop_margins)
        elif archive_type == "cbr":
            create_cbr(subfolder_path, output_archive, crop_margins)
        else:
            print(f"Type d'archive inconnu : {archive_type}")

# Exemple d'utilisation
# Remplacez 'IMG/' par le chemin de votre dossier parent contenant les sous-dossiers
process_subfolders_to_archives(
    'IMG/',
    archive_type="cbz",
    crop_margins={"top": 495, "bottom": 495, "left": 0, "right": 0}
)
