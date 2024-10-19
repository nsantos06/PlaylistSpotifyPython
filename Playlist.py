import spotipy
from spotipy import SpotifyOAuth
import time

scope = 'playlist-modify-public'
CLIENT_ID = 'b6b33012e8f04ea0a9d2756afbc38eab'
CLIENT_SECRET = 'b276fa9b33c24838a0a9b2160c1ba1a3d7'
REDIRECT_URI = 'http://localhost:8080'

# Criando Objeto Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               scope=scope,
                                               redirect_uri=REDIRECT_URI))

# Pegando o ID do usuário
user_id = sp.me()['id']

def escolher_ou_criar_playlist():
    """
    Função para permitir ao usuário escolher entre criar uma nova playlist ou usar uma já existente.
    """
    escolha = input("Você quer criar uma nova playlist ou usar uma existente?\nDigite '1' para criar nova, '2' para usar existente: ")

    if escolha == '1':
        # Fluxo para criar uma nova playlist
        return criar_playlist_nova()
    elif escolha == '2':
        # Fluxo para escolher uma playlist existente
        return escolher_playlist_existente()
    else:
        print("Escolha inválida, tente novamente.")
        return escolher_ou_criar_playlist()

def criar_playlist_nova():
    """
    Função para criar uma nova playlist.
    """
    # Nome e descrição da playlist. Após, ela é criada.
    playlist = input("Nome da Playlist: ")
    description = input("Descrição: ")
    playlist = sp.user_playlist_create(user=user_id, name=playlist, description=description)
    print(f"Playlist '{playlist['name']}' criada com sucesso!")
    
    # Retorna o ID da playlist criada
    return playlist['id']

def escolher_playlist_existente():
    """
    Função para listar as playlists do usuário e permitir que ele escolha uma existente para adicionar faixas.
    """
    playlists = sp.user_playlists(user_id)
    print(f"Playlists disponíveis:\n")
    playlist_ids = []
    
    # Listando as playlists do usuário
    for idx, playlist in enumerate(playlists['items']):
        print(f"{idx + 1}. {playlist['name']}")
        playlist_ids.append(playlist['id'])

    # Solicitando que o usuário escolha uma playlist existente
    escolha = int(input("\nEscolha o número da playlist para adicionar faixas: ")) - 1

    # Retorna o ID da playlist escolhida
    playlist_escolhida_id = playlist_ids[escolha]
    playlist_escolhida_nome = playlists['items'][escolha]['name']
    print(f"Você escolheu a playlist: {playlist_escolhida_nome}")

    return playlist_escolhida_id

def adicionar_album_ou_musicas(playlist_id):
    """
    Função que permite ao usuário escolher entre adicionar um álbum inteiro
    ou várias músicas de artistas diferentes à playlist.
    """
    escolha = input("Deseja adicionar um álbum inteiro ou várias músicas?\nDigite '1' para álbum, '2' para várias músicas: ")

    if escolha == '1':
        adicionando_albuns_playlist(playlist_id)
    elif escolha == '2':
        adicionando_multiplas_musicas(playlist_id)
    else:
        print("Escolha inválida, tente novamente.")
        return adicionar_album_ou_musicas(playlist_id)

def adicionando_albuns_playlist(playlist_id):
    """
    Função para adicionar álbuns a uma playlist já existente ou recém-criada.
    """
    all_tracks = []

    while True:
        artist = input("Artista (digite '0' para finalizar): ")
        if artist == '0':
            break
        album = input("Álbum: ")

        searchQuery = artist + ' ' + album
        searchResults = sp.search(q=searchQuery, type='album')

        if len(searchResults['albums']['items']) == 0:
            print("Álbum não encontrado.")
            continue

        album_id = searchResults['albums']['items'][0]['id']
        album_name = searchResults['albums']['items'][0]['name']
        print(f"Álbum encontrado: {album_name}")

        album_tracks = sp.album_tracks(album_id)
        album_tracks_uris = [track['uri'] for track in album_tracks['items']]

        all_tracks.extend(album_tracks_uris)
        print(f"Faixas do álbum '{album_name}' foram preparadas para adição.")

    if all_tracks:
        max_tracks_per_request = 100
        for i in range(0, len(all_tracks), max_tracks_per_request):
            track_chunk = all_tracks[i:i + max_tracks_per_request]
            sp.playlist_add_items(playlist_id=playlist_id, items=track_chunk)
            print(f"{len(track_chunk)} faixas foram adicionadas à playlist.")
            time.sleep(1)

        print(f"Todas as faixas foram adicionadas à playlist.")
    else:
        print("Nenhuma faixa foi adicionada à playlist.")

def adicionando_multiplas_musicas(playlist_id):
    """
    Função para adicionar várias músicas de diferentes artistas à playlist.
    """
    all_tracks = []

    while True:
        artist = input("Artista (digite '0' para finalizar): ")
        if artist == '0':
            break
        track = input("Nome da faixa: ")

        searchQuery = artist + ' ' + track
        searchResults = sp.search(q=searchQuery, type='track')

        if len(searchResults['tracks']['items']) == 0:
            print("Faixa não encontrada.")
            continue

        track_uri = searchResults['tracks']['items'][0]['uri']
        track_name = searchResults['tracks']['items'][0]['name']
        artist_name = searchResults['tracks']['items'][0]['artists'][0]['name']

        all_tracks.append(track_uri)
        print(f"Faixa '{track_name}' de {artist_name} foi adicionada à lista.")

    if all_tracks:
        max_tracks_per_request = 100
        for i in range(0, len(all_tracks), max_tracks_per_request):
            track_chunk = all_tracks[i:i + max_tracks_per_request]
            sp.playlist_add_items(playlist_id=playlist_id, items=track_chunk)
            print(f"{len(track_chunk)} faixas foram adicionadas à playlist.")
            time.sleep(1)

        print(f"Todas as músicas foram adicionadas à playlist.")
    else:
        print("Nenhuma faixa foi adicionada à playlist.")

def mostrar_playlist():
    """
    Função para mostrar as playlists do usuário.
    """
    playlists = sp.user_playlists(user_id)
    account_name = sp.me()['display_name']
    print(f'Nome das playlists na conta do(a) {account_name}:\n')
    for playlist in playlists['items']:
        print(playlist['name'])


# Fluxo do programa
playlist_id = escolher_ou_criar_playlist()
adicionar_album_ou_musicas(playlist_id)
