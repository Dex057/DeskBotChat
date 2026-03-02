import sys
import time
import os
import keyboard
import pyperclip
import pyautogui
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLineEdit, QTextEdit, 
                             QLabel, QTabWidget, QTableWidget, QTableWidgetItem, 
                             QSystemTrayIcon, QMenu, QFileDialog, QMessageBox, QHeaderView)
from PyQt6.QtGui import QIcon, QImage, QAction
from PyQt6.QtCore import pyqtSignal, QObject, QThread, Qt
import database

class TecladoWorker(QObject):
    disparar_acao = pyqtSignal(str, str) 
    
    def iniciar_escuta(self):
        keyboard.unhook_all()
        automacoes = database.get_todas_automacoes()
        resolutivas = database.get_todas_resolutivas()

        for _, keyword, texto, img_path in automacoes:
            if keyword:
                keyboard.add_word_listener(keyword, self.criar_callback(texto, img_path), triggers=['space', 'enter'])

        for _, keyword, texto in resolutivas:
            if keyword:
                keyboard.add_word_listener(keyword, self.criar_callback(texto, None), triggers=['space', 'enter'])
        keyboard.wait()

    def criar_callback(self, texto, img_path):
        def callback():
            time.sleep(0.05)
            # Apaga o gatilho digitado
            for _ in range(15): keyboard.send('backspace')
            self.disparar_acao.emit(texto, img_path or "")
        return callback

class DeskBotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        database.init_db()
        self.initUI()
        self.initTray()
        self.iniciar_listener()
        self.atualizar_tabelas() # Carrega os dados ao abrir

    def initUI(self):
        self.setWindowTitle("DeskBot v1.1 - Painel de Controle")
        self.resize(900, 700)
        
        tabs = QTabWidget()
        
        self.tab_auto = QWidget()
        layout_auto = QVBoxLayout()
        
        # Form Cadastro
        form_auto = QVBoxLayout()
        self.in_nome = QLineEdit(placeholderText="Nome do Procedimento")
        self.in_keyword = QLineEdit(placeholderText="Keyword (ex: /ajuda)")
        self.in_texto = QTextEdit(placeholderText="Texto do passo a passo...")
        self.in_texto.setMaximumHeight(100)
        
        btn_img = QPushButton("📸 Selecionar Manual (JPG)")
        btn_img.clicked.connect(self.selecionar_imagem)
        self.caminho_img = ""
        
        btn_salvar = QPushButton("Salvar Automação")
        btn_salvar.setStyleSheet("background-color: #2ecc71; color: white; height: 30px;")
        btn_salvar.clicked.connect(self.salvar_auto)
        
        form_auto.addWidget(QLabel("<b>Cadastrar Novo Procedimento:</b>"))
        form_auto.addWidget(self.in_nome)
        form_auto.addWidget(self.in_keyword)
        form_auto.addWidget(self.in_texto)
        form_auto.addWidget(btn_img)
        form_auto.addWidget(btn_salvar)
        
        # Tabela de Visualização
        self.tabela_auto = QTableWidget()
        self.tabela_auto.setColumnCount(3)
        self.tabela_auto.setHorizontalHeaderLabels(["Nome", "Gatilho", "Tem Imagem?"])
        self.tabela_auto.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout_auto.addLayout(form_auto)
        layout_auto.addWidget(QLabel("<br><b>Procedimentos Registrados:</b>"))
        layout_auto.addWidget(self.tabela_auto)
        self.tab_auto.setLayout(layout_auto)

        self.tab_res = QWidget()
        layout_res = QVBoxLayout()
        
        form_res = QVBoxLayout()
        self.res_nome = QLineEdit(placeholderText="Nome (ex: Resolutiva Padrão)")
        self.res_keyword = QLineEdit(placeholderText="Keyword (ex: /res_ok)")
        self.res_texto = QTextEdit(placeholderText="Texto de encerramento...")
        self.res_texto.setMaximumHeight(100)
        
        btn_salvar_res = QPushButton("Salvar Resolutiva")
        btn_salvar_res.setStyleSheet("background-color: #3498db; color: white; height: 30px;")
        btn_salvar_res.clicked.connect(self.salvar_res)
        
        form_res.addWidget(QLabel("<b>Cadastrar Nova Resolutiva:</b>"))
        form_res.addWidget(self.res_nome)
        form_res.addWidget(self.res_keyword)
        form_res.addWidget(self.res_texto)
        form_res.addWidget(btn_salvar_res)
        
        self.tabela_res = QTableWidget()
        self.tabela_res.setColumnCount(2)
        self.tabela_res.setHorizontalHeaderLabels(["Nome", "Gatilho"])
        self.tabela_res.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout_res.addLayout(form_res)
        layout_res.addWidget(QLabel("<br><b>Resolutivas Salvas:</b>"))
        layout_res.addWidget(self.tabela_res)
        self.tab_res.setLayout(layout_res)

        tabs.addTab(self.tab_auto, "Procedimentos")
        tabs.addTab(self.tab_res, "Resolutivas")
        self.setCentralWidget(tabs)

    def atualizar_tabelas(self):
        # Limpa e Recarrega Automações
        autos = database.get_todas_automacoes()
        self.tabela_auto.setRowCount(0)
        for row, (nome, key, texto, img) in enumerate(autos):
            self.tabela_auto.insertRow(row)
            self.tabela_auto.setItem(row, 0, QTableWidgetItem(nome))
            self.tabela_auto.setItem(row, 1, QTableWidgetItem(key))
            status_img = "Sim" if img else "Não"
            self.tabela_auto.setItem(row, 2, QTableWidgetItem(status_img))

        # Limpa e Recarrega Resolutivas
        res = database.get_todas_resolutivas()
        self.tabela_res.setRowCount(0)
        for row, (nome, key, texto) in enumerate(res):
            self.tabela_res.insertRow(row)
            self.tabela_res.setItem(row, 0, QTableWidgetItem(nome))
            self.tabela_res.setItem(row, 1, QTableWidgetItem(key))

    def selecionar_imagem(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Imagem', '', 'Imagens (*.jpg *.png)')
        if fname: self.caminho_img = fname

    def salvar_auto(self):
        import sqlite3
        conn = sqlite3.connect("deskbot.db")
        conn.cursor().execute("INSERT INTO automacoes (nome, keyword, texto, caminho_imagem) VALUES (?, ?, ?, ?)",
                       (self.in_nome.text(), self.in_keyword.text(), self.in_texto.toPlainText(), self.caminho_img))
        conn.commit()
        conn.close()
        self.atualizar_tabelas()
        QMessageBox.information(self, "Sucesso", "Procedimento salvo! Reinicie o app para ativar o atalho.")

    def salvar_res(self):
        import sqlite3
        conn = sqlite3.connect("deskbot.db")
        conn.cursor().execute("INSERT INTO resolutivas (nome, keyword, texto) VALUES (?, ?, ?)",
                       (self.res_nome.text(), self.res_keyword.text(), self.res_texto.toPlainText()))
        conn.commit()
        conn.close()
        self.atualizar_tabelas()
        QMessageBox.information(self, "Sucesso", "Resolutiva salva!")

    def initTray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icone.ico"))
        menu = QMenu()
        menu.addAction("Abrir Painel").triggered.connect(self.show)
        menu.addAction("Sair").triggered.connect(QApplication.instance().quit)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def executar_acao(self, texto, img_path):
        clipboard = QApplication.clipboard()
        if img_path and os.path.exists(img_path):
            img = QImage(img_path)
            clipboard.setImage(img)
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(0.3)
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

    def closeEvent(self, event):
        event.ignore()
        self.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = DeskBotApp()
    window.show()
    sys.exit(app.exec())