from googleapiclient.discovery import build
import pytube
from pytube import exceptions
import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog

API_KEY = 'AIzaSyCWJT2WyA1MqdaaXv6kFVo_doBhbpDur8U'

def create_table():
    connection = sqlite3.connect('historico.db')
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS historico (id INTEGER PRIMARY KEY,url TEXT, titulo TEXT)')
    connection.commit()
    connection.close()

def insert_data(url, titulo):
    connection = sqlite3.connect('historico.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO historico (url, titulo) VALUES (?,?)', (url, titulo))
    connection.commit()
    connection.close()

def get_data():
    connection = sqlite3.connect('historico.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM historico')
    registros = cursor.fetchall()
    connection.close()
    return registros

def baixar_audio_yt(url, pasta_destino):
    try:
        youtube = pytube.YouTube(url)
        audio = youtube.streams.filter(only_audio=True).first()
        destino = audio.download(output_path=pasta_destino)
        nome_musica = youtube.title
        artist = youtube.author
        titulo = f"{nome_musica} - {artist}"
        nome_mp3 = f"{titulo}.mp3"
        nome_destino = os.path.join(pasta_destino, nome_mp3)
        insert_data(url, titulo)
        os.rename(destino, nome_destino)
        messagebox.showinfo('Download Concluído!', f"Você baixou uma música de {artist}")

        return nome_destino
    except pytube.exceptions.ExtractError:
        messagebox.showerror("Erro", "Erro ao extrair áudio do vídeo.")
    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro ao baixar o áudio: {str(e)}")

def search_yt(query):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.search().list(
        part='id',
        type='video',
        maxResults=5,
        q=query
    )
    response = request.execute()
    videos = [item['id']['videoId'] for item in response['items']]
    return videos

def download_audio():
    query = entry_url.get().strip()
    if not query:
        messagebox.showwarning("Aviso", "Por favor, insira uma consulta para buscar.")
        return
    videos = search_yt(query)
    if not videos:
        messagebox.showwarning("Aviso", "Nenhum vídeo encontrado.")
        return
    select_video = videos[0]
    url = f'https://www.youtube.com/watch?v={select_video}'
    pasta_destino = filedialog.askdirectory(title='Selecione a pasta de destino')
    if pasta_destino:
        audio_file = baixar_audio_yt(url, pasta_destino)
        if audio_file:
            exibir_historico()

def open_folder():
    pasta_destino = filedialog.askdirectory(title="Selecione a pasta de destino.")
    if pasta_destino:
        os.startfile(pasta_destino)

def exibir_historico():
    registros = get_data()
    if registros:
        historico = "\n\n".join([f'Título: {registro[2]}' for registro in registros])
        output_area.delete('1.0', tk.END)
        output_area.insert(tk.END, historico)
    else:
        output_area.delete('1.0', tk.END)
        output_area.insert(tk.END, "Nenhum download realizado!")

create_table()

root = tk.Tk()
root.title('Download de Áudio do Youtube')
root.geometry("400x400")
root.resizable(False, False)
root.config(bg="#F0F0F0")

style = ttk.Style()
style.configure("TLabel", background='#F0F0F0')
style.configure("TButton", background='#D0D0D0', font=("Arial, 12"), width=15)
style.configure("TEntry", font=("Arial, 12"))

label_url = ttk.Label(root, text='URL DO VÍDEO AQUI')
label_url.pack()

entry_url = ttk.Entry(root, width=60, font=("Arial, 12"))
entry_url.pack()

button_download = ttk.Button(root, text='Baixar Áudio', command=download_audio)
button_download.pack(pady=10)

button_open_folder = ttk.Button(root, text="Abrir Pasta", command=open_folder)
button_open_folder.pack(pady=10)

output_area = tk.Text(root, width=50, height=10)
output_area.pack(pady=10)

button_historico = ttk.Button(root, text="Exibir Histórico", command=exibir_historico)
button_historico.pack(pady=10)

root.mainloop()
