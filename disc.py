import os
import socket
import subprocess
import platform
import logging
import ctypes
from pathlib import Path

# Configura o log
logging.basicConfig(filename='manutencao.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Checa se é Windows
def checar_sistema():
    if platform.system() != "Windows":
        print("Esse script é só pra Windows!")
        logging.error("Sistema não é Windows")
        exit(1)

# Verifica se tem permissão de admin
def tem_permissao_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

# Função para executar comandos como admin usando os.system com PowerShell
def executar_comando_admin(comando, msg):
    if not tem_permissao_admin():
        print(f"Precisa rodar como admin pra {msg.lower()}! Iniciando elevação...")
    else:
        print(f"Executando {msg}...")
    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
    print(f"{msg} concluído (se permitido no UAC)!")
    logging.info(f"{msg} executado: {comando}")

# Checa se winget está instalado
def tem_winget():
    try:
        result = subprocess.run('winget --version', shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("Winget não instalado. Baixe da Microsoft Store!")
        logging.error("Winget não encontrado")
        return False

# Pega o IP local
def pegar_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        logging.error(f"Falha ao pegar IP: {e}")
        return "Não consegui pegar o IP!"

# Limpa arquivos temporários
def limpar_temp():
    logging.info("Limpando arquivos temporários")
    print("Vai limpar arquivos temporários...")
    if input("Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Limpeza cancelada")
        return
    comando = 'del /q /f /s %temp%\\* & del /q /f /s C:\\Windows\\Temp\\*'
    executar_comando_admin(comando, "Limpeza de arquivos temporários")

# Testa conexão com ping
def testar_conexao():
    ip_local = pegar_ip()
    print(f"Seu IP local: {ip_local}")
    destino = input("Digite IP ou site (Enter para 8.8.8.8): ") or "8.8.8.8"
    logging.info(f"Testando conexão com {destino}")
    print(f"Pingando {destino}...")
    os.system(f"ping -n 4 {destino}")  # Não precisa admin

# Gerencia firewall
def gerenciar_firewall():
    try:
        escolha = int(input("1 - Ativar firewall\n2 - Desativar firewall\nEscolha: "))
        if escolha == 1:
            comando = 'netsh advfirewall set allprofiles state on'
            executar_comando_admin(comando, "Ativação do firewall")
        elif escolha == 2:
            if input("Desativar firewall é arriscado. Confirma? (s/n): ").lower() != 's':
                print("Cancelado.")
                logging.info("Desativação cancelada")
                return
            comando = 'netsh advfirewall set allprofiles state off'
            executar_comando_admin(comando, "Desativação do firewall")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Digite um número!")
        logging.error("Entrada inválida no firewall")

# Otimiza Windows
def otimizar_windows():
    logging.info("Iniciando otimização")
    print("Vai otimizar o Windows...")
    if input("Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Otimização cancelada")
        return
    # Limpeza de disco
    executar_comando_admin('cleanmgr', "Limpeza de disco")
    # SFC
    executar_comando_admin('sfc /scannow', "Verificação de arquivos do sistema")
    # CHKDSK
    executar_comando_admin('chkdsk C: /f /r', "Verificação de disco")
    # Defrag
    executar_comando_admin('defrag C: /O', "Desfragmentação do disco C:")
    print("Otimização concluída!")
    logging.info("Otimização concluída")

# Gerencia rede
def gerenciar_rede():
    try:
        escolha = int(input("1 - Reiniciar serviço\n2 - Renovar IP\n3 - Limpar DNS\n4 - Redefinir rede\nEscolha: "))
        if escolha == 1:
            servico = input("Nome do serviço (ex: dnscache): ")
            comando = f'net stop {servico} & net start {servico}'
            executar_comando_admin(comando, f"Reinício do serviço {servico}")
        elif escolha == 2:
            comando = 'ipconfig /release & ipconfig /renew'
            executar_comando_admin(comando, "Renovação de IP")
        elif escolha == 3:
            comando = 'ipconfig /flushdns'
            executar_comando_admin(comando, "Limpeza de DNS")
        elif escolha == 4:
            if input("Redefinir rede exige reinício. Confirma? (s/n): ").lower() != 's':
                print("Cancelado.")
                logging.info("Redefinição cancelada")
                return
            comando = 'netsh winsock reset & netsh int ip reset'
            executar_comando_admin(comando, "Redefinição de rede")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Digite um número!")
        logging.error("Entrada inválida na rede")

# Gerencia drivers
def gerenciar_drivers():
    backup_dir = str(Path.home() / "Desktop" / "backup")
    os.makedirs(backup_dir, exist_ok=True)
    try:
        escolha = int(input("1 - Backup drivers\n2 - Instalar drivers\nEscolha: "))
        if escolha == 1:
            comando = f'dism /online /export-driver /destination:"{backup_dir}"'
            executar_comando_admin(comando, "Backup de drivers")
            print(f"Backup salvo em {backup_dir}")
        elif escolha == 2:
            comando = f'dism /online /add-driver /driver:"{backup_dir}" /recurse'
            executar_comando_admin(comando, "Instalação de drivers")
        else:
            print("Opção inválida!")
    except ValueError:
        print("Digite um número!")
        logging.error("Entrada inválida nos drivers")

# Checa memória
def checar_memoria():
    logging.info("Iniciando checagem de memória")
    print("Verificando memória...")
    os.system('wmic memorychip')  # Não precisa admin

# Atualiza programas com winget
def atualizar_programas():
    logging.info("Iniciando atualização com winget")
    if not tem_winget():
        return
    if input("Atualizar tudo com winget? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Atualização cancelada")
        return
    executar_comando_admin('winget upgrade --all', "Atualização de programas")

# Desfragmenta discos
def desfragmentar():
    logging.info("Iniciando desfragmentação")
    print("Desfragmentando discos (evite em SSDs)...")
    if input("Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Desfragmentação cancelada")
        return
    executar_comando_admin('defrag /C /O', "Desfragmentação de discos")

# Repara sistema
def reparar_sistema():
    logging.info("Iniciando reparo do sistema")
    print("Vai reparar o sistema...")
    if input("Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Reparo cancelado")
        return
    executar_comando_admin('DISM /Online /Cleanup-Image /RestoreHealth', "Reparo DISM")
    executar_comando_admin('sfc /scannow', "Reparo SFC")

# Menu principal
def main():
    checar_sistema()
    opcoes = {
        0: ("Limpar arquivos temporários", limpar_temp),
        1: ("Testar conexão (ping)", testar_conexao),
        2: ("Gerenciar firewall", gerenciar_firewall),
        3: ("Otimizar Windows", otimizar_windows),
        4: ("Gerenciar rede", gerenciar_rede),
        5: ("Gerenciar drivers", gerenciar_drivers),
        6: ("Checar memória", checar_memoria),
        7: ("Atualizar programas (winget)", atualizar_programas),
        8: ("Desfragmentar discos", desfragmentar),
        9: ("Reparar sistema", reparar_sistema)
    }

    while True:
        print("\n" + "=" * 30)
        print("Menu de Manutenção")
        print("=" * 30)
        for key, (nome, _) in opcoes.items():
            print(f"{key} - {nome}")
        try:
            opcao = int(input("\nEscolha uma opção (0-9): "))
            if opcao in opcoes:
                print(f"\nExecutando: {opcoes[opcao][0]}")
                opcoes[opcao][1]()
            else:
                print("Opção inválida!")
            if input("\nContinuar? (s/n): ").lower() != 's':
                print("Saindo...")
                logging.info("Script finalizado")
                break
        except ValueError:
            print("Digite um número!")
            logging.error("Entrada inválida no menu")

if __name__ == "__main__":
    main()
