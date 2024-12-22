import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import sys

# Fonction pour obtenir la liste des disques
def get_disks():
    disks = []
    try:
        # Utilisation de lsblk pour lister les disques
        result = subprocess.check_output("lsblk -d -o NAME,SIZE", shell=True)
        result = result.decode("utf-8").strip().splitlines()
        for line in result:
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
        # Utilisation de dd pour créer une image du disque
        command = f"sudo dd if={disk} of={output_filename} bs=64K status=progress"
        subprocess.run(command, shell=True, check=True)
        print(f"Image disque créée avec succès: {output_filename}")
    except Exception as e:
        print(f"Erreur lors de la création de l'image disque: {e}")

# Fonction pour créer un fichier ISO à partir de l'image disque
def create_iso_from_image(image_filename, iso_filename):
    try:
        # Utilisation de mkisofs pour créer un ISO bootable
        command = f"sudo mkisofs -o {iso_filename} -b isolinux.bin -c boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table {image_filename}"
        subprocess.run(command, shell=True, check=True)
        print(f"ISO créé avec succès: {iso_filename}")
    except Exception as e:
        print(f"Erreur lors de la création de l'ISO: {e}")

# Fonction principale
def main():
    # Création de la fenêtre Tkinter
    root = tk.Tk()
    root.title("Créer une image ISO de votre disque")

    # Obtention des disques disponibles
    disks = get_disks()
    
    if not disks:
        messagebox.showerror("Erreur", "Aucun disque trouvé. Assurez-vous d'être sous Linux et d'avoir des privilèges administratifs.")
        sys.exit(1)

    # Label et menu déroulant pour choisir un disque
    label = tk.Label(root, text="Sélectionnez un disque à cloner :")
    label.pack(pady=10)
    
    # Création du menu déroulant
    disk_names = [disk[0] for disk in disks]
    disk_menu = ttk.Combobox(root, values=disk_names)
    disk_menu.pack(pady=10)

    # Bouton pour démarrer la création de l'image
    def on_create_image():
        selected_disk = disk_menu.get()
        if selected_disk:
            # Demander le nom du fichier de sortie
            output_filename = f"{selected_disk.replace('/', '')}_backup.img"
            try:
                create_disk_image(selected_disk, output_filename)
                # Une fois l'image créée, demander le nom de l'ISO
                iso_filename = output_filename.replace(".img", ".iso")
                create_iso_from_image(output_filename, iso_filename)
                messagebox.showinfo("Succès", f"Image ISO créée avec succès : {iso_filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Une erreur est survenue: {e}")
        else:
            messagebox.showerror("Erreur", "Veuillez sélectionner un disque.")

    create_button = tk.Button(root, text="Créer l'image ISO", command=on_create_image)
    create_button.pack(pady=20)

    # Lancer l'interface
    root.mainloop()

if __name__ == "__main__":
    main()
