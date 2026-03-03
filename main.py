import sys
import time
import os
import keyboard
import pyperclip
import pyautogui
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QTextEdit, 
                             QLabel, QTabWidget, QTableWidget, QTableWidgetItem, 
                             QSystemTrayIcon, QMenu, QFileDialog, QMessageBox, 
                             QHeaderView, QInputDialog)
from PyQt6.QtGui import QIcon, QImage, QAction
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt

import database

# --- THREAD DE ESCUTA DO TECLADO ---
class TecladoWorker(QObject):
    disparar_acao = pyqtSignal(str, str) 
    
    def iniciar_escuta(self):
        keyboard.unhook_all()
        automacoes = database.get_todas_automacoes()
        resolutivas = database.get_todas_resolutivas()

        # Registra gatilhos para Automações
        for _, keyword_str, texto, img_path in automacoes:
            if keyword_str:
                keyboard.add_word_listener(keyword_str, 
                                         self.criar_callback(texto, img_path), 
                                         triggers=['space', 'enter'])

        # Registra gatilhos para Resolutivas
        for _, keyword_str, texto in resolutivas:
            if keyword_str:
                keyboard.add_word_listener(keyword_str, 
                                         self.criar_callback(texto, None), 
                                         triggers=['space', 'enter'])
        keyboard.wait()

    def criar_callback(self, texto, img_path):
        def callback():
            time.sleep(0.05)
            # Apaga a keyword digitada (ajuste o range se necessário)
            for _ in range(15): 
                keyboard.send('backspace')
            self.disparar_acao.emit(texto, img_path or "")
        return callback

# --- INTERFACE PRINCIPAL ---
class DeskBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        database.init_db()
        self.initUI()
        self.initTray()
        self.iniciar_listener()
        self.atualizar_tabelas()

    def initUI(self):
        self.setWindowTitle("DeskBot v1.2 - Service Desk Automation")
        self.resize(850, 650)
        self.setWindowIcon(QIcon("assets/icone.ico"))
        
        tabs = QTabWidget()
        
        # ABA: PROCEDIMENTOS (Texto + Imagem)
        self.tab_auto = QWidget()
        layout_auto = QVBoxLayout()
        self.in_nome = QLineEdit(placeholderText="Nome do Procedimento")
        self.in_keyword = QLineEdit(placeholderText="Gatilho (ex: /ajuda)")
        self.in_texto = QTextEdit(placeholderText="Texto (Use {var1} para capturar o que você copiou)")
        self.in_texto.setMaximumHeight(80)
        btn_img = QPushButton("📸 Selecionar Imagem")
        btn_img.clicked.connect(self.selecionar_imagem)
        self.caminho_img = ""
        btn_salvar = QPushButton("💾 Salvar Procedimento")
        btn_salvar.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold;")
        btn_salvar.clicked.connect(self.salvar_auto)
        
        self.tabela_auto = QTableWidget()
        self.tabela_auto.setColumnCount(3)
        self.tabela_auto.setHorizontalHeaderLabels(["Nome", "Gatilho", "Imagem"])
        self.tabela_auto.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout_auto.addWidget(QLabel("<b>Novo Procedimento:</b>"))
        layout_auto.addWidget(self.in_nome); layout_auto.addWidget(self.in_keyword)
        layout_auto.addWidget(self.in_texto); layout_auto.addWidget(btn_img); layout_auto.addWidget(btn_salvar)
        layout_auto.addWidget(QLabel("<br><b>Registrados:</b>"))
        layout_auto.addWidget(self.tabela_auto)
        self.tab_auto.setLayout(layout_auto)

        # ABA: RESOLUTIVAS (Apenas Texto)
        self.tab_res = QWidget()
        layout_res = QVBoxLayout()
        self.res_nome = QLineEdit(placeholderText="Nome da Resolutiva")
        self.res_keyword = QLineEdit(placeholderText="Gatilho (ex: /finalizar)")
        self.res_texto = QTextEdit(placeholderText="Texto de fechamento (Use {var1} para o número do chamado)")
        self.res_texto.setMaximumHeight(80)
        btn_salvar_res = QPushButton("✅ Salvar Resolutiva")
        btn_salvar_res.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        btn_salvar_res.clicked.connect(self.salvar_res)
        
        self.tabela_res = QTableWidget()
        self.tabela_res.setColumnCount(2)
        self.tabela_res.setHorizontalHeaderLabels(["Nome", "Gatilho"])
        self.tabela_res.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout_res.addWidget(QLabel("<b>Nova Resolutiva:</b>"))
        layout_res.addWidget(self.res_nome); layout_res.addWidget(self.res_keyword)
        layout_res.addWidget(self.res_texto); layout_res.addWidget(btn_salvar_res)
        layout_res.addWidget(QLabel("<br><b>Salvas:</b>"))
        layout_res.addWidget(self.tabela_res)
        self.tab_res.setLayout(layout_res)

        tabs.addTab(self.tab_auto, "Procedimentos")
        tabs.addTab(self.tab_res, "Resolutivas")
        self.setCentralWidget(tabs)

    def atualizar_tabelas(self):
        autos = database.get_todas_automacoes()
        self.tabela_auto.setRowCount(0)
        for row, (n, k, t, i) in enumerate(autos):
            self.tabela_auto.insertRow(row)
            self.tabela_auto.setItem(row, 0, QTableWidgetItem(n))
            self.tabela_auto.setItem(row, 1, QTableWidgetItem(k))
            self.tabela_auto.setItem(row, 2, QTableWidgetItem("Sim ✅" if i else "Não ❌"))

        res = database.get_todas_resolutivas()
        self.tabela_res.setRowCount(0)
        for row, (n, k, t) in enumerate(res):
            self.tabela_res.insertRow(row)
            self.tabela_res.setItem(row, 0, QTableWidgetItem(n))
            self.tabela_res.setItem(row, 1, QTableWidgetItem(k))

    def selecionar_imagem(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Selecionar JPG', '', 'Imagens (*.jpg *.png)')
        if fname: self.caminho_img = fname

    def salvar_auto(self):
        conn = sqlite3.connect("deskbot.db")
        conn.cursor().execute("INSERT INTO automacoes (nome, keyword, texto, caminho_imagem) VALUES (?, ?, ?, ?)",
                       (self.in_nome.text(), self.in_keyword.text(), self.in_texto.toPlainText(), self.caminho_img))
        conn.commit(); conn.close()
        self.atualizar_tabelas()
        QMessageBox.information(self, "Sucesso", "Salvo! Reinicie o app para ativar o novo gatilho.")

    def salvar_res(self):
        conn = sqlite3.connect("deskbot.db")
        conn.cursor().execute("INSERT INTO resolutivas (nome, keyword, texto) VALUES (?, ?, ?)",
                       (self.res_nome.text(), self.res_keyword.text(), self.res_texto.toPlainText()))
        conn.commit(); conn.close()
        self.atualizar_tabelas()
        QMessageBox.information(self, "Sucesso", "Resolutiva salva!")

    def executar_acao(self, texto, img_path):
        clipboard = QApplication.clipboard()
        
        # Lógica de Variável {var1}
        if "{var1}" in texto:
            valor_copiado = pyperclip.paste().strip()
            # Se o clipboard não parecer um ticket (vazio ou muito longo), pergunta
            if not valor_copiado or len(valor_copiado) > 30:
                valor, ok = QInputDialog.getText(self, "Entrada Requerida", "Informe o valor da variável:")
                if ok and valor: valor_copiado = valor
                else: return
            texto = texto.replace("{var1}", valor_copiado)

        # Enviar Imagem
        if img_path and os.path.exists(img_path):
            img = QImage(img_path)
            clipboard.setImage(img)
            time.sleep(0.3)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.6)
            pyautogui.press('enter')
            time.sleep(0.3)

        # Enviar Texto
        if texto:
            pyperclip.copy(texto)
            time.sleep(0.1)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.1)
            pyautogui.press('enter')

    def iniciar_listener(self):
        self.thread = QThread()
        self.worker = TecladoWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.iniciar_escuta)
        self.worker.disparar_acao.connect(self.executar_acao)
        self.thread.start()

    def initTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icone.ico"))
        menu = QMenu()
        menu.addAction("Abrir Painel").triggered.connect(self.show)
        menu.addAction("Sair").triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    import sqlite3
    window = DeskBotApp()
    window.show()
    sys.exit(app.exec())