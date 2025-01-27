import os
import shutil
import threading
from tkinter import Tk, Label, Entry, Button, StringVar, IntVar, filedialog, messagebox, Radiobutton, Frame, ttk
from mutagen.easyid3 import EasyID3
from collections import defaultdict

# Variável global para controlar a interrupção do processo
stop_flag = False

def count_folders_and_files(folder_path):
    """Conta o número total de pastas e arquivos em uma pasta especificada."""
    total_folders = 0
    total_files = 0
    for _, dirs, files in os.walk(folder_path):
        total_folders += len(dirs)
        total_files += len(files)
    return total_folders, total_files

def list_mp3_files(folder_path, progress_var, status_label, root, limit=None):
    """Lista todos os arquivos MP3 em uma pasta especificada."""
    global stop_flag
    print(f"Listando arquivos MP3 na pasta: {folder_path}")
    mp3_files = []
    total_folders, total_files = count_folders_and_files(folder_path)
    processed_folders = 0
    processed_files = 0

    for root_dir, _, files in os.walk(folder_path):
        if stop_flag:
            break
        for file in files:
            if stop_flag:
                break
            if file.lower().endswith('.mp3'):
                mp3_files.append(os.path.join(root_dir, file))
            processed_files += 1
            progress_var.set((processed_files / total_files) * 100)
            status_label.config(text=f"Escaneando arquivos... ({processed_files}/{total_files})")
            root.update_idletasks()  # Força a atualização da interface gráfica
        processed_folders += 1
        status_label.config(text=f"Escaneando pastas... ({processed_folders}/{total_folders})")
        root.update_idletasks()  # Força a atualização da interface gráfica

    if limit:
        mp3_files = mp3_files[:limit]
    print(f"Número de arquivos MP3 encontrados: {len(mp3_files)}")
    return mp3_files

def group_by_artist(mp3_files):
    """Agrupa os arquivos MP3 por artista."""
    print("Agrupando arquivos MP3 por artista...")
    groups = defaultdict(list)
    for file in mp3_files:
        if stop_flag:
            break
        try:
            audio = EasyID3(file)
            artist = audio['artist'][0]
            groups[artist].append(file)
        except Exception as e:
            print(f"Erro ao ler metadados do arquivo {file}: {e}")
    print(f"Número de artistas encontrados: {len(groups)}")
    return groups

def select_songs_based_on_artist_count(groups_by_artist, songs_per_artist):
    """Seleciona um número específico de músicas por artista."""
    print(f"Selecionando até {songs_per_artist} músicas por artista...")
    selected_songs = []
    for artist, songs in groups_by_artist.items():
        if stop_flag:
            break
        selected_songs.extend(songs[:songs_per_artist])
    print(f"Número de músicas selecionadas: {len(selected_songs)}")
    return selected_songs

def limit_songs_by_size(selected_songs, max_size_bytes):
    """Limita a seleção de músicas com base no tamanho total."""
    print(f"Limitando músicas selecionadas para um total de {max_size_bytes} bytes...")
    total_size = 0
    limited_songs = []
    for song in selected_songs:
        if stop_flag:
            break
        song_size = os.path.getsize(song)
        if total_size + song_size <= max_size_bytes:
            limited_songs.append(song)
            total_size += song_size
        else:
            break
    print(f"Número de músicas após limitação por tamanho: {len(limited_songs)}")
    return limited_songs

def copy_or_link_selected_songs(songs, destination_folder, progress_var, status_label, root, copy_mode=True):
    """Copia ou cria atalhos para as músicas selecionadas na pasta de destino."""
    global stop_flag
    print(f"{'Copiando' if copy_mode else 'Criando atalhos para'} músicas na pasta de destino: {destination_folder}")
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    total_songs = len(songs)
    for i, song in enumerate(songs):
        if stop_flag:
            break
        destination_path = os.path.join(destination_folder, os.path.basename(song))
        if copy_mode:
            shutil.copy2(song, destination_path)
        else:
            os.symlink(song, destination_path)
        progress_var.set((i + 1) / total_songs * 100)
        status_label.config(text=f"Processando {i + 1} de {total_songs} músicas...")
        root.update_idletasks()  # Força a atualização da interface gráfica
    print("Processo de cópia/conexão concluído.")
    status_label.config(text="Processo concluído.")

# Funções auxiliares para a interface gráfica
def select_music_folder():
    folder_selected = filedialog.askdirectory()
    music_folder.set(folder_selected)

def select_destination_folder():
    folder_selected = filedialog.askdirectory()
    destination_folder.set(folder_selected)

def start_process(root):
    global stop_flag
    stop_flag = False
    print("Iniciando o processo...")
    try:
        music_folder_path = music_folder.get()
        destination_folder_path = destination_folder.get()
        test_limit_value = test_limit.get()
        songs_per_artist_value = songs_per_artist.get()
        max_size_gb_value = max_size_gb.get()
        copy_mode_value = copy_mode.get() == 1

        print(f"Pasta de músicas: {music_folder_path}")
        print(f"Pasta de destino: {destination_folder_path}")
        print(f"Limite de arquivos: {test_limit_value}")
        print(f"Músicas por artista: {songs_per_artist_value}")
        print(f"Tamanho máximo (GB): {max_size_gb_value}")
        print(f"Modo de cópia: {'Copiar' if copy_mode_value else 'Criar Atalhos'}")

        # Etapa 1: Escaneamento dos arquivos MP3
        status_label.config(text="Iniciando escaneamento dos arquivos MP3...")
        root.update_idletasks()
        songs = list_mp3_files(music_folder_path, progress_var, status_label, root, limit=test_limit_value)
        print(f"Número de músicas encontradas: {len(songs)}")
        overall_progress_var.set(33)  # Atualiza o progresso geral para 33%
        root.update_idletasks()

        if stop_flag:
            raise Exception("Processo interrompido pelo usuário.")

        if songs:
            # Etapa 2: Agrupamento e seleção de músicas
            status_label.config(text="Agrupando e selecionando músicas...")
            root.update_idletasks()
            groups_by_artist = group_by_artist(songs)
            selected_songs = select_songs_based_on_artist_count(groups_by_artist, songs_per_artist_value)
            if copy_mode_value:
                limited_songs = limit_songs_by_size(selected_songs, max_size_gb_value * (1024 ** 3))
            else:
                limited_songs = selected_songs
            overall_progress_var.set(66)  # Atualiza o progresso geral para 66%
            root.update_idletasks()

            if stop_flag:
                raise Exception("Processo interrompido pelo usuário.")

            if limited_songs:
                # Etapa 3: Cópia ou criação de atalhos dos arquivos selecionados
                status_label.config(text="Copiando ou criando atalhos das músicas selecionadas...")
                root.update_idletasks()
                copy_or_link_selected_songs(limited_songs, destination_folder_path, progress_var, status_label, root, copy_mode=copy_mode_value)
                overall_progress_var.set(100)  # Atualiza o progresso geral para 100%
                root.update_idletasks()
                if stop_flag:
                    raise Exception("Processo interrompido pelo usuário.")
                messagebox.showinfo("Sucesso", "Processo concluído com sucesso!")
            else:
                messagebox.showwarning("Aviso", "Nenhuma música selecionada dentro do limite de tamanho.")
        else:
            messagebox.showwarning("Aviso", "Nenhum arquivo MP3 encontrado na pasta especificada.")
    except Exception as e:
        print(f"Erro: {e}")
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
    finally:
        start_button.config(state='normal')
        stop_button.config(state='disabled')
        status_label.config(text="")

def start_process_thread():
    print("Iniciando a thread...")
    status_label.config(text="Iniciando o processo...")
    start_button.config(state='disabled')
    stop_button.config(state='normal')
    process_thread = threading.Thread(target=start_process, args=(root,))
    process_thread.start()
    print("Thread iniciada.")

def stop_process():
    global stop_flag
    stop_flag = True
    print("Processo interrompido pelo usuário.")
    status_label.config(text="Processo interrompido pelo usuário.")
    root.update_idletasks()

# Criação da interface gráfica
root = Tk()
root.title("Seleção de Músicas MP3")
root.geometry("600x450")
root.configure(bg="#f0f4f7")

# Variáveis para armazenar os valores dos campos de entrada
music_folder = StringVar()
destination_folder = StringVar()
test_limit = IntVar(value=999999)
songs_per_artist = IntVar(value=3)
max_size_gb = IntVar(value=10)
copy_mode = IntVar(value=1)
progress_var = IntVar(value=0)
overall_progress_var = IntVar(value=0)

# Layout da interface gráfica
frame = Frame(root, padx=10, pady=10, bg="#f0f4f7")
frame.pack(fill='both', expand=True)

Label(frame, text="Pasta de Músicas:", bg="#f0f4f7").grid(row=0, column=0, sticky='e')
Entry(frame, textvariable=music_folder, width=50).grid(row=0, column=1)
Button(frame, text="Selecionar", command=select_music_folder, bg="#d9e4f5", activebackground="#c3d3ef").grid(row=0, column=2)

Label(frame, text="Pasta de Destino:", bg="#f0f4f7").grid(row=1, column=0, sticky='e')
Entry(frame, textvariable=destination_folder, width=50).grid(row=1, column=1)
Button(frame, text="Selecionar", command=select_destination_folder, bg="#d9e4f5", activebackground="#c3d3ef").grid(row=1, column=2)

Label(frame, text="Limite de Arquivos:", bg="#f0f4f7").grid(row=2, column=0, sticky='e')
Entry(frame, textvariable=test_limit).grid(row=2, column=1)

Label(frame, text="Músicas por Artista:", bg="#f0f4f7").grid(row=3, column=0, sticky='e')
Entry(frame, textvariable=songs_per_artist).grid(row=3, column=1)

Label(frame, text="Tamanho Máximo (GB):", bg="#f0f4f7").grid(row=4, column=0, sticky='e')
Entry(frame, textvariable=max_size_gb).grid(row=4, column=1)

Label(frame, text="Modo:", bg="#f0f4f7").grid(row=5, column=0, sticky='e')
Radiobutton(frame, text="Copiar", variable=copy_mode, value=1, bg="#f0f4f7").grid(row=5, column=1, sticky='w')
Radiobutton(frame, text="Criar Atalhos", variable=copy_mode, value=0, bg="#f0f4f7").grid(row=5, column=1, sticky='e')

start_button = Button(frame, text="Iniciar", command=start_process_thread, bg="#b5d1f0", activebackground="#a4c4e8")
start_button.grid(row=6, column=0, columnspan=2, pady=10)

stop_button = Button(frame, text="Parar", command=stop_process, bg="#f0b5b5", activebackground="#f0a4a4", state='disabled')
stop_button.grid(row=6, column=2, pady=10)

progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress.grid(row=7, column=0, columnspan=3, pady=10)

overall_progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate", variable=overall_progress_var)
overall_progress.grid(row=8, column=0, columnspan=3, pady=10)

status_label = Label(frame, text="", bg="#f0f4f7")
status_label.grid(row=9, column=0, columnspan=3)

root.mainloop()
