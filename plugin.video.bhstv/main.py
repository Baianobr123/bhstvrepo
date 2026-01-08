# -*- coding: utf-8 -*-
import sys
import xbmc
import xbmcgui
import xbmcplugin
import urllib.request
import urllib.parse
import re

URLS = {
    'canais': "https://gitlab.com/BHS_TV/bhs_tv/-/raw/main/CHANNELS.txt?ref_type=heads",
    'filmes': "https://gitlab.com/BHS_TV/bhs_tv/-/raw/main/MOVIES.txt?ref_type=heads",
    'series': "https://gitlab.com/BHS_TV/bhs_tv/-/raw/main/SERIES.txt?ref_type=heads"
}

IMG_SEARCH = "https://i.imgur.com/xeUbPyj.png"
IMG_TV = "https://i.imgur.com/31vnSVm.png"
IMG_MOVIES = "https://i.imgur.com/1gWW9MP.png"
IMG_SERIES = "https://i.imgur.com/hsVp6Rr.png"
FANART = "https://i.imgur.com/uuRf2gE.jpg"

HANDLE = int(sys.argv[1])
# User-Agent atualizado para simular um navegador padrão e evitar bloqueios de banda
U_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'

def get_data(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': U_AGENT})
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.read().decode('utf-8', 'ignore')
    except:
        return ""

def add_dir(name, url, icon, folder=True):
    li = xbmcgui.ListItem(label=name)
    li.setArt({'thumb': icon, 'icon': icon, 'fanart': FANART})
    li.setLabel2(' ') 
    xbmcplugin.addDirectoryItem(HANDLE, url, li, folder)

def parse_block(block):
    try:
        linhas = block.split('\n')
        info_linha = linhas[0]
        nome = info_linha.split(',')[-1].strip()
        logo_match = re.search(r'tvg-logo="(.*?)"', info_linha)
        img = logo_match.group(1) if logo_match else None
        link = None
        for l in linhas[1:]:
            if l.strip().startswith('http'):
                link = l.strip()
                break
        return nome, link, img
    except:
        return None, None, None

def main():
    param = sys.argv[2] if len(sys.argv) > 2 else ""
    xbmcplugin.setContent(HANDLE, 'movies')

    if not param:
        xbmcgui.Dialog().ok('[B] [COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [/B]', '[B] [COLOR white]Seja Bem-Vindo ao melhor addon do BRASIL!!!!!!!!!!!!![/B]\n[B][COLOR red]Sua conta está ativa, pronta para o uso!!!!!!!!!![/COLOR][/B]')
        add_dir('[B][COLOR silver]🔍 BHS TV - PESQUISAR[/COLOR][/B]', sys.argv[0] + '?mode=search', IMG_SEARCH)
        add_dir('📺 [B][COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [COLOR white]- TV AO VIVO[/COLOR][/B]', sys.argv[0] + '?mode=list_cats&type=canais', IMG_TV)
        add_dir('🎬 [B][COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [COLOR white]- FILMES[/COLOR][/B]', sys.argv[0] + '?mode=list_cats&type=filmes', IMG_MOVIES)
        add_dir('🍿 [B][COLOR white]BHS[/COLOR] [COLOR red]TV[/COLOR] [COLOR white]- SÉRIES / ANIMES[/COLOR][/B]', sys.argv[0] + '?mode=list_cats&type=series', IMG_SERIES)

    elif 'mode=list_cats' in param:
        t = 'canais' if 'type=canais' in param else ('series' if 'type=series' in param else 'filmes')
        data = get_data(URLS[t])
        cats = sorted(list(set(re.findall(r'group-title="(.*?)"', data))))
        for c in cats:
            url = sys.argv[0] + '?mode=list_items&type=' + t + '&cat=' + urllib.parse.quote_plus(c)
            icon = IMG_TV if t == 'canais' else (IMG_MOVIES if t == 'filmes' else IMG_SERIES)
            add_dir(c, url, icon)

    elif 'mode=search' in param or 'mode=list_items' in param:
        query = urllib.parse.parse_qs(param[1:])
        if 'mode=search' in param:
            text = xbmcgui.Dialog().input('Pesquisar')
            if not text: return
            text = text.lower()
            search_list = ['canais', 'filmes', 'series']
            target_cat = None
        else:
            t = query.get('type', ['canais'])[0]
            target_cat = urllib.parse.unquote_plus(query.get('cat', [''])[0])
            search_list = [t]
            text = None

        for t in search_list:
            data = get_data(URLS[t])
            blocos = re.split(r'#EXTINF:', data, flags=re.IGNORECASE)[1:]
            for b in blocos:
                if (text and text in b.lower()) or (target_cat and f'group-title="{target_cat}"' in b):
                    nome, link, img = parse_block('#EXTINF:' + b)
                    if nome and link:
                        icon = img or (IMG_TV if t == 'canais' else (IMG_MOVIES if t == 'filmes' else IMG_SERIES))
                        li = xbmcgui.ListItem(label=nome)
                        li.setArt({'thumb': icon, 'icon': icon, 'poster': icon, 'fanart': FANART})
                        
                        # Metadados essenciais
                        li.setInfo('video', {'title': nome})
                        li.setProperty('IsPlayable', 'true')
                        
                        # --- OTIMIZAÇÃO DE BUFFER E CARREGAMENTO ---
                        # Força o uso do InputStream Adaptive para gerenciar o cache
                        li.setProperty('inputstream', 'inputstream.adaptive')
                        # 'Verifypeer=false' remove o delay de validação SSL (o que causa o loading demorado)
                        f_path = link + '|User-Agent=' + urllib.parse.quote(U_AGENT) + '&Verifypeer=false'
                        
                        xbmcplugin.addDirectoryItem(HANDLE, f_path, li, False)

    xbmcplugin.endOfDirectory(HANDLE)

if __name__ == '__main__':
    main()