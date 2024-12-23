import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import sys

# Fonction pour obtenir la liste des disques
def get_disks():
    disks = []
    try:
        result = subprocess.check_output("lsblk -d -o NAME,SIZE", shell=True)
        result = result.decode("utf-8").strip().splitlines()
        for line in result[1:]:  # Ignorer l'entête
            parts = line.split()
            if len(parts) == 2:
                disk_name = f"/dev/{parts[0]}"
                disk_size = parts[1]
                disks.append((disk_name, disk_size))
    except Exception as e:
        print(f"Erreur lors de la récupération des disques: {e}")
    return disks

# Fonction pour créer une image disque avec dd
def create_disk_image(disk, output_filename):
    try:
        command = f"sudo dd if={disk} of={output_filename} bs=64K status=progress"
        subprocess.run(command, shell=True, check=True)
        print(f"Image disque créée avec succès: {output_filename}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erreur lors de la création de l'image disque: {e}")

# Fonction pour créer un fichier ISO à partir de l'image disque
def create_iso_from_image(image_filename, iso_filename):
    try:
        command = (
            f"sudo mkisofs -o {iso_filename} -allow-limited-size "
            f"-b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table {image_filename}"
        )
        subprocess.run(command, shell=True, check=True)
        print(f"ISO créé avec succès: {iso_filename}")
    except subprocess.CalledProcessError as e:
        raise Exception(f"Erreur lors de la création de l'ISO: {e}")

# Fonction principale
def main():
    root = tk.Tk()
    root.title("Créer une image ISO de votre disque")
    root.geometry("400x300")

    disks = get_disks()
    if not disks:
        messagebox.showerror("Erreur", "Aucun disque détecté. Assurez-vous d'avoir des privilèges administratifs.")
        sys.exit(1)

    label = tk.Label(root, text="Sélectionnez un disque à cloner :")
    label.pack(pady=10)

    disk_menu = ttk.Combobox(root, values=[f"{d[0]} ({d[1]})" for d in disks])
    disk_menu.pack(pady=10)

    def on_create_image():
        selected_disk = disk_menu.get().split()[0]  # Obtenir le nom du disque
        if selected_disk:
            output_filename = simpledialog.askstring(
                "Nom de fichier",
                "Entrez le nom du fichier image (sans extension) :",
            )
            if not output_filename:
                messagebox.showerror("Erreur", "Nom de fichier non spécifié.")
                return

            output_img = f"{output_filename}.img"
            try:
                create_disk_image(selected_disk, output_img)

                iso_filename = f"{output_filename}.iso"
                create_iso_from_image(output_img, iso_filename)
                messagebox.showinfo("Succès", f"ISO créé avec succès : {iso_filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner un disque.")

    create_button = tk.Button(root, text="Créer l'image ISO", command=on_create_image)
    create_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
