import requests
import subprocess
import time
import logging
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import track
from typing import List, Optional, Dict, Union
import random
import string

logging.basicConfig(
    filename='tool_finder_dark.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message=s)'
)

console = Console()

TOOL_LIST_URL = "https://raw.githubusercontent.com/joaodarkofc/tooldark/main/ferramentas.json"

def random_characters(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def glitch_effect(duration, char_per_line, lines):
    for _ in range(lines):
        glitch_text = random_characters(char_per_line)
        console.print(glitch_text, style="bold green")
        time.sleep(duration / lines)

def display_welcome():
    glitch_effect(1.5, 50, 10)
    
    banner_text = """
#######             ##    #####  #            ##              #####              ##     #
   #                 #     #  #                #               #   #              #     #
   #                 #     # #                 #               #    #             #     #
   #     ###   ###   #     ###  ##  #####   ####   ##  ####    #    # ####  ####  #  ## #
   #    #   # #   #  #     # #   #   #  #  #   #  #  #  # #    #    #    #   # #  # ##  #
   #    #   # #   #  #     #     #   #  #  #   #  ####  #      #    #  ###   #    ##    #
   #    #   # #   #  #     #     #   #  #  #   #  #     #      #   #  #  #   #    # ##
  ###    ###   ###  ###   ##    ### ######  #####  ### ###    #####   ### # ###  ### ## #
    """
    
    console.print(banner_text, style="bold magenta")
    console.print("Bem-vindo ao Tool Finder Dark!", style="bold cyan")
    console.print("Encontre e instale ferramentas para diferentes categorias.", style="italic")

def loading_animation(duration, description="Carregando..."):
    for _ in track(range(duration), description=description):
        time.sleep(0.1)

def fetch_tool_list(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        response.close()
        return data
    except requests.exceptions.RequestException as e:
        console.print(f"Erro ao obter a lista de ferramentas: {e}", style="bold red")
        logging.error(f"Erro ao obter a lista de ferramentas: {e}")
        return None

def show_tool_list(tools):
    if not tools:
        console.print("Nenhuma ferramenta encontrada.", style="bold yellow")
        return
    
    table = Table(title="Ferramentas Disponíveis", style="bold blue")
    table.add_column("Nome da Ferramenta", style="bold green")
    table.add_column("Descrição", style="italic yellow")

    for tool in tools:
        description = tool.get("description", "Sem descrição")
        table.add_row(tool["name"], description)

    console.print(table)

def is_tool_installed(tool_name):
    try:
        subprocess.run([tool_name, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=False)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
    except Exception as e:
        console.print(f"Erro ao verificar se a ferramenta '{tool_name}' está instalada: {e}", style="bold red")
        logging.error(f"Erro ao verificar se a ferramenta '{tool_name}' está instalada: {e}")
        return False

def install_tool(tool):
    if not tool:
        console.print("Nenhuma ferramenta para instalar.", style="bold yellow")
        return
    
    tool_name = tool["name"]
    install_command = tool["install_command"]
    
    console.print(f"Tentando instalar {tool_name}...", style="bold blue")
    loading_animation(10, description="Instalando ferramenta...")

    try:
        subprocess.run(install_command, check=True, shell=True)
        console.print(f"{tool_name} instalado com sucesso!", style="bold green")
    except subprocess.CalledProcessError:
        console.print(f"Erro ao instalar '{tool_name}': comando falhou.", style="bold red")
        logging.error(f"Erro ao instalar '{tool_name}': comando falhou.")
    except Exception as e:
        console.print(f"Erro ao instalar '{tool_name}': {e}", style="bold red")
        logging.error(f"Erro ao instalar '{tool_name}': {e}")

def user_input(tools):
    if not tools:
        console.print("Lista de ferramentas vazia.", style="bold red")
        return None
    
    search_term = Prompt.ask("Digite um termo para buscar ferramentas (ou pressione Enter para mostrar todas)")

    if search_term.lower() == 'sair':
        confirm_exit = Prompt.ask("Você realmente deseja sair? (sim/não)")
        if confirm_exit.lower() == "sim":
            console.print("Saindo do Tool Finder Dark.", style="bold cyan")
            return None
        else:
            search_term = ""

    filtered_tools = [tool for tool in tools if search_term.lower() in tool["name"].lower() or search_term.lower() in tool["description"].lower()]
    
    if not filtered_tools:
        console.print("Nenhuma ferramenta encontrada com esse termo.", style="bold yellow")
        return None
    
    show_tool_list(filtered_tools)

    choices = [tool["name"] for tool in filtered_tools]
    choices.append("sair")

    tool_name = Prompt.ask("Digite o nome da ferramenta para instalar (ou 'sair' para encerrar)", choices=choices)

    if tool_name.lower() == 'sair':
        confirm_exit = Prompt.ask("Você realmente deseja sair? (sim/não)")
        if confirm_exit.lower() == "sim":
            console.print("Saindo do Tool Finder Dark.", style="bold cyan")
            return None

    selected_tool = next((tool for tool in filtered_tools if tool["name"].lower() == tool_name.lower()), None)

    return selected_tool

def main():
    display_welcome()

    tools = fetch_tool_list(TOOL_LIST_URL)

    while True:
        if tools:
            selected_tool = user_input(tools)
            
            if selected_tool:
                if not is_tool_installed(selected_tool["name"]):
                    install_tool(selected_tool)
                else:
                    console.print(f"{selected_tool['name']} já está instalado.", style="bold cyan")

            continue_choice = Prompt.ask("Deseja voltar ao menu? (sim/não)", choices=["sim", "não"])
            if continue_choice.lower() == "não":
                console.print("Saindo do Tool Finder Dark.", style="bold cyan")
                break
        else:
            console.print("Não foi possível obter a lista de ferramentas.", style="bold red")
            break

if __name__ == "__main__":
    main()
