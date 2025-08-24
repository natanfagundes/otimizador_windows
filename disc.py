import os
import socket
import subprocess
import platform
import shlex
import logging
import ctypes
from pathlib import Path

# Configura o log pra guardar o que o script faz
logging.basicConfig(filename='manutencao.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Checa se tá rodando no Windows
def checar_sistema():
    if platform.system() != "Windows":
        print("Esse script é só pra Windows, sorry!")
        logging.error("Sistema não é Windows")
        exit(1)

# Verifica se o script tá com permissão de admin
def tem_permissao_admin():
    return ctypes.windll.shell32.IsUserAnAdmin()

# Função pra rodar comandos com feedback decente
def rodar_comando(comando, msg, precisa_shell=False):
    if not tem_permissao_admin():
        print(f"Precisa rodar como admin pra {msg.lower()}!")
        logging.warning(f"{msg} falhou: sem permissão de admin")
        return False
    try:
        result = subprocess.run(
            comando,
            shell=precisa_shell,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"{msg} deu certo!")
        logging.info(f"{msg} concluído: {result.stdout}")
        return True
    except subprocess.SubprocessError as e:
        print(f"Deu ruim no {msg.lower()}: {e}")
        logging.error(f"{msg} falhou: {e} - {e.stderr}")
        return False

# Checa se o winget tá instalado
def tem_winget():
    try:
        result = subprocess.run('winget --version', shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        print("Winget não tá instalado. Baixe da Microsoft Store!")
        logging.error("Winget não encontrado")
        return False

# Pega o IP da máquina
def pegar_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        logging.error("Falha ao pegar IP")
        return "Não rolou pegar o IP!"

# Limpa arquivos temporários
def limpar_temp():
    logging.info("Limpando arquivos temporários")
    print("Vai limpar os arquivos temporários...")
    if input("Confirma? (s/n): ").lower() != 's':
        print("Beleza, cancelado.")
        logging.info("Limpeza cancelada")
        return
    rodar_comando(
        ['del', '/q', '/f', '/s', r'%temp%\*', '&&', 'del', '/q', '/f', '/s', r'C:\Windows\Temp\*'],
        "Limpeza de arquivos temporários",
        precisa_shell=True
    )

# Testa conexão com ping
def testar_conexao():
    ip_local = pegar_ip()
    print(f"Seu IP: {ip_local}")
    destino = input("Digite um IP ou site (ou Enter pra 8.8.8.8): ") or "8.8.8.8"
    logging.info(f"Ping em {destino}")
    print(f"Pingando {destino}...")
    rodar_comando(['ping', '-n', '4', shlex.quote(destino)], f"Teste de conexão com {destino}")

# Gerencia o firewall
def gerenciar_firewall():
    try:
        escolha = int(input("1 - Ligar firewall\n2 - Desligar firewall\nEscolha: "))
        if escolha == 1:
            rodar_comando(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'on'], "Ativação do firewall")
        elif escolha == 2:
            if input("Desligar o firewall pode ser arriscado. Confirma? (s/n): ").lower() != 's':
                print("Cancelado.")
                logging.info("Desativação do firewall cancelada")
                return
            rodar_comando(['netsh', 'advfirewall', 'set', 'allprofiles', 'state', 'off'], "Desativação do firewall")
        else:
            print("Escolha 1 ou 2, por favor!")
    except ValueError:
        print("Digita um número, cara!")
        logging.error("Entrada inválida no firewall")

# Otimiza o Windows (limpeza, verificação, desfragmentação)
def otimizar_windows():
    logging.info("Iniciando otimização")
    print("Vai otimizar o Windows (limpeza, verificação e desfragmentação)...")
    if input("Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Otimização cancelada")
        return
    
    print("Limpando disco...")
    rodar_comando(['cleanmgr', '/sageribbon'], "Limpeza de disco")
    
    print("Verificando arquivos do sistema...")
    rodar_comando(['sfc', '/scannow'], "Verificação de arquivos")
    
    print("Agendando verificação de disco (pode precisar reiniciar)...")
    rodar_comando(['chkdsk', 'C:', '/f', '/r'], "Verificação de disco")
    
    print("Desfragmentando disco C:...")
    rodar_comando(['defrag', 'C:', '/O'], "Desfragmentação do disco C:")

    print("Otimização concluída!")
    logging.info("Otimização concluída")

# Gerencia a rede
def gerenciar_rede():
    try:
        escolha = int(input("1 - Reiniciar serviço\n2 - Renovar IP\n3 - Limpar DNS\n4 - Redefinir rede\nEscolha: "))
        acoes = {
            1: lambda: rodar_comando(
                ['net', 'stop', shlex.quote(input("Nome do serviço (ex.: wuauserv): ")), '&&', 'net', 'start', shlex.quote(input("Nome do serviço novamente: "))],
                "Reinício de serviço",
                precisa_shell=True
            ),
            2: lambda: rodar_comando(['ipconfig', '/release', '&&', 'ipconfig', '/renew'], "Renovação de IP", precisa_shell=True),
            3: lambda: rodar_comando(['ipconfig', '/flushdns'], "Limpeza de DNS", precisa_shell=True),
            4: lambda: rodar_comando(
                ['netsh', 'winsock', 'reset', '&&', 'netsh', 'int', 'ip', 'reset'],
                "Redefinição de rede",
                precisa_shell=True
            )
        }
        if escolha == 4:
            if input("Redefinir a rede pode exigir reiniciar o PC. Confirma? (s/n): ").lower() != 's':
                print("Cancelado.")
                logging.info("Redefinição de rede cancelada")
                return
        if escolha in acoes:
            acoes[escolha]()
        else:
            print("Escolha 1, 2, 3 ou 4!")
    except ValueError:
        print("Digita um número, por favor!")
        logging.error("Entrada inválida na gestão de rede")

# Gerencia drivers
def gerenciar_drivers():
    backup_dir = Path.home() / "Desktop" / "backup"
    backup_dir.mkdir(exist_ok=True)
    try:
        escolha = int(input("1 - Fazer backup de drivers\n2 - Instalar drivers\nEscolha: "))
        acoes = {
            1: lambda: rodar_comando(['dism', '/online', '/export-driver', f'/destination:{backup_dir}'], f"Backup de drivers em {backup_dir}"),
            2: lambda: rodar_comando(['dism', '/online', '/add-driver', f'/driver:{backup_dir}', '/recurse'], "Instalação de drivers")
        }
        if escolha in acoes:
            acoes[escolha]()
            if escolha == 1:
                print(f"Backup salvo em {backup_dir}")
        else:
            print("Escolha 1 ou 2!")
    except ValueError:
        print("Digita um número, cara!")
        logging.error("Entrada inválida na gestão de drivers")

# Diagnóstico de memória
def checar_memoria():
    logging.info("Iniciando diagnóstico de memória")
    print("Verificando memória...")
    rodar_comando(['wmic', 'memorychip'], "Diagnóstico de memória")

# Atualiza programas com winget
def atualizar_programas():
    logging.info("Iniciando atualização com winget")
    print("Atualizando programas...")
    if not tem_winget():
        return
    if input("Vai atualizar tudo com winget, pode demorar. Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Atualização cancelada")
        return
    rodar_comando(['winget', 'upgrade', '--all'], "Atualização de programas")

# Desfragmenta discos
def desfragmentar():
    logging.info("Iniciando desfragmentação")
    print("Desfragmentando discos...")
    if input("Só pra HDs, não SSDs. Pode demorar. Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Desfragmentação cancelada")
        return
    rodar_comando(['defrag', '/C', '/O'], "Desfragmentação de discos")

# Repara arquivos do sistema
def reparar_sistema():
    logging.info("Iniciando reparo do sistema")
    print("Reparando sistema...")
    if input("DISM e SFC podem demorar e alterar arquivos. Confirma? (s/n): ").lower() != 's':
        print("Cancelado.")
        logging.info("Reparo cancelado")
        return
    print("Rodando DISM...")
    rodar_comando(['DISM', '/Online', '/Cleanup-Image', '/RestoreHealth'], "Reparo DISM")
    print("Rodando SFC...")
    rodar_comando(['sfc', '/scannow'], "Verificação SFC")

# Menu principal
def main():
    checar_sistema()
    opcoes = {
        0: ("Limpar arquivos temporários", limpar_temp, "Apaga arquivos temporários pra liberar espaço"),
        1: ("Testar conexão (ping)", testar_conexao, "Faz ping pra checar conexão"),
        2: ("Gerenciar firewall", gerenciar_firewall, "Liga ou desliga o firewall"),
        3: ("Otimizar Windows", otimizar_windows, "Limpa disco, verifica arquivos e desfragmenta"),
        4: ("Gerenciar rede", gerenciar_rede, "Controla serviços de rede, IP e DNS"),
        5: ("Gerenciar drivers", gerenciar_drivers, "Faz backup ou restaura drivers"),
        6: ("Checar memória", checar_memoria, "Mostra info da RAM"),
        7: ("Atualizar programas (winget)", atualizar_programas, "Atualiza todos os programas"),
        8: ("Desfragmentar discos", desfragmentar, "Otimiza HDs (evite em SSDs)"),
        9: ("Reparar sistema", reparar_sistema, "Conserta arquivos do Windows")
    }

    while True:
        print("\n" + "=" * 30)
        print("Menu de Manutenção")
        print("=" * 30)
        for key, (nome, _, desc) in opcoes.items():
            print(f"{key} - {nome}: {desc}")
        
        try:
            opcao = int(input("\nEscolha uma opção (0-9): "))
            if opcao in opcoes:
                print(f"\nRodando: {opcoes[opcao][0]}")
                opcoes[opcao][1]()
            else:
                print("Opção inválida, escolhe entre 0 e 9!")
            
            if input("\nQuer continuar? (s/n): ").lower() != 's':
                print("Tchau!")
                logging.info("Script finalizado")
                break
        except ValueError:
            print("Digita um número, por favor!")
            logging.error("Entrada inválida no menu")

if __name__ == "__main__":
    main()
