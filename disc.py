import os
import socket

# Função simples para pegar o IP da máquina
def pegar_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Usa o Google DNS pra testar
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Não consegui pegar o IP!"

# Opções do menu
limpeza = "0 - Limpeza de arquivos temporários"
rede = "1 - Teste de conexão (ping)"
firewall = "2 - Gerenciar Firewall"
otimizar = "3 - Otimizar o Windows"
gerenciar_rede = "4 - Gerenciar Rede"

while True:
    # Mostra o menu
    print("=" * 30)
    print(limpeza)
    print(rede)
    print(firewall)
    print(otimizar)
    print(gerenciar_rede)

    # Pede a opção pro usuário
    try:
        opcao = int(input("Escolha uma opção (0-10): "))
        
        if opcao == 0:
            print(f"Você escolheu: {limpeza}")
            # Executa comandos de limpeza como administrador
            comando = 'del /q /f /s %temp%\\* & del /q /f /s C:\\Windows\\Temp\\*'
            os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
            print("Arquivos temporários limpos (se você permitiu no UAC)!")

        elif opcao == 1:
            print(f"Você escolheu: {rede}")
            # Mostra o IP local
            print(f"Seu IP local é: {pegar_ip()}")
            # Pede o IP ou hostname pro ping
            destino = input("Digite um IP ou site pra testar (ou Enter pra usar 8.8.8.8): ")
            if destino == "":
                destino = "8.8.8.8"  # Usa o Google DNS como padrão
            print(f"Testando conexão com {destino}...")
            os.system(f"ping -n 4 {destino}")  # Faz 4 pings
            print("Teste de conexão concluído!")

        elif opcao == 2:
            print(f"Você escolheu: {firewall}")
            try:
                escolha = int(input("Escolha:\n1 - Ativar\n2 - Desativar\n"))
                if escolha == 1:
                    comando = 'netsh advfirewall set allprofiles state on'
                    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
                    print("Firewall ativado (se você permitiu no UAC)!")
                elif escolha == 2:
                    comando = 'netsh advfirewall set allprofiles state off'
                    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
                    print("Firewall desativado (se você permitiu no UAC)!")
                else:
                    print("Opção inválida! Escolha 1 ou 2.")
            except ValueError:
                print("Por favor, digite um número!")

        elif opcao == 3:
            print(f"Você escolheu: {otimizar}")
            print("Iniciando otimização do Windows... (confirme os prompts do UAC)")
            
            # Executa cleanmgr (Limpeza de Disco)
            print("Abrindo Limpeza de Disco...")
            os.system('powershell -Command "Start-Process cleanmgr -Verb RunAs"')
            print("Limpeza de Disco concluída (se você selecionou os arquivos)!")
            
            # Executa sfc /scannow (Verificador de Arquivos do Sistema)
            print("Verificando arquivos do sistema...")
            os.system('powershell -Command "Start-Process cmd -ArgumentList \'/c sfc /scannow\' -Verb RunAs"')
            print("Verificação de arquivos do sistema concluída!")
            
            # Executa chkdsk /f /r (Verificação de disco)
            print("Agendando verificação de disco (pode exigir reinicialização)...")
            os.system('powershell -Command "Start-Process cmd -ArgumentList \'/c chkdsk C: /f /r\' -Verb RunAs"')
            print("Verificação de disco agendada (reinicie o PC se necessário)!")
            
            # Executa defrag C: /O (Desfragmentação)
            print("Desfragmentando o disco C:...")
            os.system('powershell -Command "Start-Process cmd -ArgumentList \'/c defrag C: /O\' -Verb RunAs"')
            print("Desfragmentação concluída!")
            
            print("Otimização do Windows finalizada!")

        elif opcao == 4:
            print(f"Você escolheu: {gerenciar_rede}")
            try:
                escolha = int(input("Escolha:\n1 - Reiniciar serviço\n2 - Renovar IP\n3 - Limpar DNS\n4 - Redefinir rede\n"))
                if escolha == 1:
                    servico = input("Digite o nome do serviço (ex.: wuauserv, dnscache): ")
                    print(f"Reiniciando o serviço {servico}...")
                    comando = f'net stop {servico} & net start {servico}'
                    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
                    print(f"Serviço {servico} reiniciado (se você permitiu no UAC)!")
                elif escolha == 2:
                    print("Renovando IP...")
                    comando = 'ipconfig /release & ipconfig /renew'
                    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
                    print("IP renovado (se você permitiu no UAC)!")
                elif escolha == 3:
                    print("Limpando cache de DNS...")
                    comando = 'ipconfig /flushdns'
                    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
                    print("Cache de DNS limpo (se você permitiu no UAC)!")
                elif escolha == 4:
                    print("Redefinindo configurações de rede (pode exigir reinicialização)...")
                    comando = 'netsh winsock reset & netsh int ip reset'
                    os.system(f'powershell -Command "Start-Process cmd -ArgumentList \'/c {comando}\' -Verb RunAs"')
                    print("Rede redefinida (reinicie o PC para aplicar as mudanças)!")
                else:
                    print("Opção inválida! Escolha 1, 2, 3 ou 4.")
            except ValueError:
                print("Por favor, digite um número!")

        else:
            print("Opção inválida! Escolha entre 0 e 4.")

        # Pergunta se quer continuar
        continuar = input("Quer continuar? (s/n): ")
        if continuar.lower() != "s":
            print("Saindo do programa...")
            break

    except ValueError:
        print("Por favor, digite um número!")
