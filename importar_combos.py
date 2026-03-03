import sqlite3
import os

DB_PATH = "deskbot.db"

def importar():
    if not os.path.exists(DB_PATH):
        print("❌ Erro: O arquivo deskbot.db não foi encontrado. Execute o main.py primeiro.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- LISTA DE RESOLUTIVAS (TEXTO PURO) ---
    # Formato: (Nome, Gatilho, Texto)
    resolutivas = [
        ("Abertura Padrão", "/bom", "Olá! Tudo bem? Sou o **Edson** do Service Desk do **TRT-2**. Como posso ajudar?"),
        ("Aguarde um momento", "/so", "Só um momento por gentileza, enquanto faço a abertura do seu chamado."),
        ("Meu E-mail", "/em", "edson.martins@amazoninf.com.br"),
        ("Nº de Chamado", "/info", "Informo que o seu contato via WhatsApp foi registrado, segue o número do chamado: **{var1}**. Será enviada uma cópia desse chamado para o seu e-mail."),
        ("Envio para Equipe", "/res", "Seu chamado será encaminhado para o setor responsável. Quando for encerrado, você receberá em seu e-mail a resposta: \"Chamado **{var1}** foi resolvido\"."),
        ("Cobrança de Urgência", "/cob", "Realizei a cobrança de urgência na sua tratativa! Número do chamado **{var1}**. Este chamado de cobrança será encerrado, mas o principal continua o mesmo."),
        ("Balcão Virtual", "/bal", "A orientação é contatar o Balcão Virtual: https://ww2.trt2.jus.br/contato/balcao-virtual. No campo 'sala de atendimento' coloque o chamado: **{var1}**."),
        ("Transferência para Voz", "/liga", "Entraremos em contato via ligação. O prosseguimento será por lá e encerrarei o chat. Número do chamado: **{var1}**."),
        ("Fechamento de Chat", "/fim", "Agradeço pelo contato. Este atendimento via WhatsApp será encerrado. Caso necessário, ligue para (11) 2898-3443. Tenha um excelente dia!"),
        ("Time-out Inatividade", "/ftime", "Informo que este atendimento foi encerrado por falta de retorno. Caso precise, retorne o contato com o Service Desk. Tenha um excelente dia!"),
        ("Ligação Interrompida", "/caiu", "A ligação foi interrompida. Tentamos contato sem sucesso. Estamos encerrando o chamado e permanecemos à disposição."),
        ("Prompt para IA", "/ia", "Atue como Service Desk N1. Corrija a descrição técnica abaixo sem alterar os dados, use parágrafos e negrito em termos chaves. Crie uma 'Resolução Aplicada' formal."),
        ("Template Equipamentos", "/eq", "**Equipamento/Sistema:**\n**Solicitação:**\n**Tombo:**\n**Local:**\n**Telefone:**\n( ) Corp. ( ) Pessoal\n( ) Home Office ( ) Presencial"),
        ("Erro SJT.APl.039 (2º Grau)", "/pje2", "Advogada(o) informa que está sem acesso ao PJe no 2º grau. Erro: Não existe localização/perfil para o usuário informado (SJT.APl.039)."),
        ("CNJ com Empatia", "/2cnj", "Dr., compreendo a dificuldade. Será necessário contatar o suporte do CNJ (61 2326-5353), pois eles detêm a autonomia sobre a plataforma de autenticação."),
    ]

    # --- LISTA DE PROCEDIMENTOS (COM ESPAÇO PARA IMAGEM NO FUTURO) ---
    # Formato: (Nome, Gatilho, Texto, Caminho_Imagem)
    procedimentos = [
        ("Captura de Tela", "/cap", "Poderia por gentileza enviar uma captura de tela completa do erro? Que pegue desde a URL até a hora do computador.", ""),
        ("Limpeza de Navegador", "/limpa", "Realize a limpeza no Chrome: Ctrl+Shift+Del > Todo o período > Limpar dados. No Firefox: Menu > Configurações > Privacidade > Limpar dados.", ""),
        ("Busca de Certificado", "/busca", "No ícone do PJe (perto da hora), clique com o botão direito > Configurações de Certificados > ABA A3 > Busca Automática.", ""),
        ("Mídias no PJe", "/midia", "Requisitos PJe: Formatos MP3 ou MP4, máximo 200MB. Verifique se o nome do arquivo não tem espaços ou símbolos. Vídeo: https://youtu.be/c-Ni_lyxgx0", ""),
        ("PJeOffice Pro Mac", "/pjemac", "No Mac, se aparecer 'desenvolvedor não identificado', vá em Preferências do Sistema > Segurança e Privacidade > Geral > Abrir assim mesmo.", ""),
        ("Manuais PJeOffice Pro", "/manu", "Downloads PJeOffice Pro:\n64 bits: https://bit.ly/pje-pro-64\nSiga o manual de configuração rigorosamente.", ""),
    ]

    print("🚀 Iniciando importação de combos...")

    # Inserindo Resolutivas
    for nome, key, txt in resolutivas:
        try:
            cursor.execute("INSERT OR REPLACE INTO resolutivas (nome, keyword, texto) VALUES (?, ?, ?)", (nome, key, txt))
        except Exception as e:
            print(f"⚠️ Erro ao inserir {key}: {e}")

    # Inserindo Procedimentos
    for nome, key, txt, img in procedimentos:
        try:
            cursor.execute("INSERT OR REPLACE INTO automacoes (nome, keyword, texto, caminho_imagem) VALUES (?, ?, ?, ?)", (nome, key, txt, img))
        except Exception as e:
            print(f"⚠️ Erro ao inserir {key}: {e}")

    conn.commit()
    conn.close()
    print("✅ Importação concluída com sucesso! Abra o DeskBot para conferir.")

if __name__ == "__main__":
    importar()