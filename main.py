import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os


class AppAtelie(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Ateliê da Mamãe")
        self.geometry("900x500")  # Aumenta um pouco o tamanho para os novos campos
        self.center_window()

        # --- Configuração do Estilo (Modo Noturno) ---
        self.style = ttk.Style(self)
        self.style.theme_use("clam")  # Um tema base que permite mais customização
        self.configure_dark_mode_style()  # Aplica o estilo de modo noturno

        # --- Configuração do Banco de Dados ---
        self.db_name = 'atelie.db'
        self.create_table()

        # --- Criação das Abas ---
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Aba 1: Produtos Cadastrados
        self.tab_produtos_cadastrados = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.tab_produtos_cadastrados, text="Produtos Cadastrados")

        # Aba 2: Cadastro de Produtos
        self.tab_cadastro_produtos = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.tab_cadastro_produtos, text="Cadastro de Produtos")

        # --- Conteúdo das Abas ---
        self.setup_produtos_cadastrados_tab()
        self.setup_cadastro_produtos_tab()

        # Carrega os produtos na tabela ao iniciar a aplicação
        self.load_products()

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (self.winfo_width() / 2)  # Usa a largura/altura da janela configurada
        y = (screen_height / 2) - (self.winfo_height() / 2)
        self.geometry(f'+{int(x)}+{int(y)}')

    def configure_dark_mode_style(self):
        # Cores
        bg_dark = "#2e2e2e"  # Fundo escuro
        fg_light = "#f0f0f0"  # Letras claras
        accent_color = "#4CAF50"  # Cor de destaque (verde, similar ao padrão do Google)
        button_active_bg = "#5cb85c"  # Cor do botão ao passar o mouse

        # Estilo para Frames e Janela (fundo)
        self.style.configure('TFrame', background=bg_dark)
        self.configure(bg=bg_dark)  # Define o fundo da janela principal

        # Estilo para Labels
        self.style.configure('TLabel', background=bg_dark, foreground=fg_light)
        self.style.configure('Treeview.Heading', background=bg_dark, foreground=fg_light, font=('Arial', 10, 'bold'))
        self.style.configure('Treeview', background=bg_dark, foreground=fg_light, fieldbackground=bg_dark)

        # Estilo para as abas do Notebook
        self.style.configure('TNotebook', background=bg_dark)
        self.style.configure('TNotebook.Tab', background='#424242', foreground=fg_light, borderwidth=0)
        self.style.map('TNotebook.Tab', background=[('selected', accent_color)])

        # Estilo para Entradas (Entry)
        self.style.map('TEntry', fieldbackground=[('focus', '#424242'), ('!focus', '#3a3a3a')],
                       foreground=[('focus', fg_light), ('!focus', fg_light)], borderwidth=[(None, 1)])

        # Estilo para Botões
        self.style.configure('TButton', background=accent_color, foreground='#ffffff', font=('Arial', 10, 'bold'),
                             borderwidth=0)
        self.style.map('TButton', background=[('active', button_active_bg)])

        # Estilo para Scrollbar
        self.style.configure("Vertical.TScrollbar", background=bg_dark, troughcolor="#424242", bordercolor=bg_dark,
                             arrowcolor=fg_light)
        self.style.map("Vertical.TScrollbar",
                       background=[('active', accent_color)],
                       troughcolor=[('active', '#525252')]
                       )

    # --- Funções do Banco de Dados ---
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas por nome
        return conn

    def create_table(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_produto TEXT NOT NULL,
                variante_produto TEXT,
                descricao TEXT,
                materiais_principais TEXT,
                custo_producao_estimado REAL,
                tempo_producao_estimado REAL,
                preco_venda REAL,
                margem_lucro REAL
            )
        ''')
        conn.commit()
        conn.close()

    def insert_product(self, tipo, variante, descricao, materiais, custo_prod, tempo_prod, preco_venda, margem_lucro):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (tipo_produto, variante_produto, descricao, materiais_principais,
                                  custo_producao_estimado, tempo_producao_estimado, preco_venda, margem_lucro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tipo, variante, descricao, materiais, custo_prod, tempo_prod, preco_venda, margem_lucro))
        conn.commit()
        conn.close()

    def delete_product(self, product_id):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM produtos WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()

    def get_products(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM produtos ORDER BY id DESC')  # Ordena por ID decrescente para ver os mais novos primeiro
        products = cursor.fetchall()
        conn.close()
        return products

    # --- Conteúdo da Aba 1: Produtos Cadastrados ---
    def setup_produtos_cadastrados_tab(self):
        # Frame para os botões (Excluir)
        btn_frame = ttk.Frame(self.tab_produtos_cadastrados)
        btn_frame.pack(pady=5, padx=10, fill="x")

        self.btn_excluir = ttk.Button(btn_frame, text="Excluir Produto Selecionado",
                                      command=self.confirm_delete_product)
        self.btn_excluir.pack(side="right")  # Botão à direita

        # Configura o Treeview (tabela)
        columns = (
        "ID", "Tipo", "Variante", "Descrição", "Materiais", "Custo (R$)", "Tempo (min)", "Preço (R$)", "Margem (%)")
        self.tree = ttk.Treeview(self.tab_produtos_cadastrados, columns=columns, show="headings", style='Treeview')

        # Configura os cabeçalhos das colunas
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")

        # Ajustes de largura para colunas específicas
        self.tree.column("ID", width=40, stretch=tk.NO)
        self.tree.column("Tipo", width=100)
        self.tree.column("Variante", width=100)
        self.tree.column("Descrição", width=180)
        self.tree.column("Materiais", width=120)
        self.tree.column("Custo (R$)", width=80)
        self.tree.column("Tempo (min)", width=80)
        self.tree.column("Preço (R$)", width=80)
        self.tree.column("Margem (%)", width=80)

        self.tree.pack(expand=True, fill="both", padx=10, pady=5)

        # Adiciona uma scrollbar
        scrollbar = ttk.Scrollbar(self.tab_produtos_cadastrados, orient="vertical", command=self.tree.yview,
                                  style="Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def load_products(self):
        # Limpa a tabela antes de carregar novos dados
        for item in self.tree.get_children():
            self.tree.delete(item)

        products = self.get_products()
        for product in products:
            self.tree.insert("", tk.END, values=(
                product["id"],
                product["tipo_produto"],
                product["variante_produto"],
                product["descricao"],
                product["materiais_principais"],
                f"{product['custo_producao_estimado']:.2f}",  # Formata para 2 casas decimais
                f"{product['tempo_producao_estimado']:.0f}",  # Tempo pode ser inteiro ou float
                f"{product['preco_venda']:.2f}",
                f"{product['margem_lucro']:.2f}"
            ))

    def confirm_delete_product(self):
        selected_item = self.tree.focus()  # Obtém o ID do item selecionado na Treeview
        if not selected_item:
            messagebox.showwarning("Excluir Produto", "Selecione um produto para excluir.")
            return

        # Pega os valores da linha selecionada
        values = self.tree.item(selected_item, 'values')
        product_id = values[0]
        product_name = values[1]  # Tipo do produto

        # Pede confirmação ao usuário
        response = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o produto '{product_name}' (ID: {product_id})?"
        )

        if response:
            try:
                self.delete_product(product_id)
                self.load_products()  # Recarrega a tabela após a exclusão
                messagebox.showinfo("Sucesso", "Produto excluído com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir produto: {e}")

    # --- Conteúdo da Aba 2: Cadastro de Produtos ---
    def setup_cadastro_produtos_tab(self):
        input_frame = ttk.Frame(self.tab_cadastro_produtos)
        input_frame.pack(pady=20, padx=20, fill="x")

        # Layout com grid
        row_idx = 0

        # Campo: Tipo (Ex: Necessaire, Carteira, Mochila)
        ttk.Label(input_frame, text="Tipo Prod.:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_tipo_produto = ttk.Entry(input_frame, width=40)
        self.entry_tipo_produto.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Variante (Ex: P, M, G, Slim, Grande)
        ttk.Label(input_frame, text="Variante:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_variante_produto = ttk.Entry(input_frame, width=40)
        self.entry_variante_produto.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Descrição (Detalhes adicionais)
        ttk.Label(input_frame, text="Descrição:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_descricao = ttk.Entry(input_frame, width=40)
        self.entry_descricao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Materiais Principais (Ex: Tecido, Zíper, Forro)
        ttk.Label(input_frame, text="Materiais:").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_materiais = ttk.Entry(input_frame, width=40)
        self.entry_materiais.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Custo Prod. (R$)
        ttk.Label(input_frame, text="Custo Prod. (R$):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_custo_producao = ttk.Entry(input_frame, width=40)
        self.entry_custo_producao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Tempo Prod. (min)
        ttk.Label(input_frame, text="Tempo Prod. (min):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_tempo_producao = ttk.Entry(input_frame, width=40)
        self.entry_tempo_producao.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Preço Venda (R$)
        ttk.Label(input_frame, text="Preço Venda (R$):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.entry_preco_venda = ttk.Entry(input_frame, width=40)
        self.entry_preco_venda.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Campo: Margem Lucro (%) - será atualizado automaticamente
        ttk.Label(input_frame, text="Margem Lucro (%):").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
        self.label_margem_lucro = ttk.Label(input_frame, text="0.00%")  # Label para exibir a margem
        self.label_margem_lucro.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)
        row_idx += 1

        # Configura as colunas para expandir
        input_frame.grid_columnconfigure(1, weight=1)

        # Adiciona um trace para calcular a margem de lucro em tempo real
        self.entry_custo_producao.bind("<KeyRelease>", self.update_margem_lucro)
        self.entry_preco_venda.bind("<KeyRelease>", self.update_margem_lucro)

        # Botão de Cadastro
        self.btn_cadastrar = ttk.Button(self.tab_cadastro_produtos, text="Cadastrar Produto",
                                        command=self.cadastrar_produto)
        self.btn_cadastrar.pack(pady=20)

    def update_margem_lucro(self, event=None):
        try:
            custo_str = self.entry_custo_producao.get().replace(',', '.')
            preco_str = self.entry_preco_venda.get().replace(',', '.')

            custo = float(custo_str) if custo_str else 0.0
            preco = float(preco_str) if preco_str else 0.0

            if preco > 0:
                margem = ((preco - custo) / preco) * 100
                self.label_margem_lucro.config(text=f"{margem:.2f}%")
            else:
                self.label_margem_lucro.config(text="0.00%")  # Se preço for zero, margem é zero ou indefinida
        except ValueError:
            self.label_margem_lucro.config(text="Inválido")  # Mostra inválido se a entrada não for numérica

    def cadastrar_produto(self):
        # Coleta e limpa os dados
        tipo = self.entry_tipo_produto.get().strip()
        variante = self.entry_variante_produto.get().strip()
        descricao = self.entry_descricao.get().strip()
        materiais = self.entry_materiais.get().strip()

        custo_prod_str = self.entry_custo_producao.get().strip().replace(',', '.')
        tempo_prod_str = self.entry_tempo_producao.get().strip().replace(',', '.')
        preco_venda_str = self.entry_preco_venda.get().strip().replace(',', '.')

        # Validação dos campos obrigatórios
        if not tipo:
            messagebox.showwarning("Validação", "O campo 'Tipo Prod.' é obrigatório.")
            return
        if not custo_prod_str:
            messagebox.showwarning("Validação", "O campo 'Custo Prod. (R$)' é obrigatório.")
            return
        if not tempo_prod_str:
            messagebox.showwarning("Validação", "O campo 'Tempo Prod. (min)' é obrigatório.")
            return
        if not preco_venda_str:
            messagebox.showwarning("Validação", "O campo 'Preço Venda (R$)' é obrigatório.")
            return

        # Conversão e validação de números
        try:
            custo_prod = float(custo_prod_str)
            tempo_prod = float(tempo_prod_str)
            preco_venda = float(preco_venda_str)
        except ValueError:
            messagebox.showwarning("Validação", "Custo, Tempo e Preço devem ser números válidos.")
            return

        if custo_prod < 0 or tempo_prod < 0 or preco_venda < 0:
            messagebox.showwarning("Validação", "Valores numéricos não podem ser negativos.")
            return

        # Calcula a margem de lucro (já validamos que preco_venda não será zero aqui)
        margem_lucro = ((preco_venda - custo_prod) / preco_venda) * 100 if preco_venda > 0 else 0.0

        try:
            self.insert_product(tipo, variante, descricao, materiais, custo_prod, tempo_prod, preco_venda, margem_lucro)
            messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")
            self.load_products()  # Recarrega a tabela para mostrar o novo produto

            # Limpa os campos após o cadastro
            self.entry_tipo_produto.delete(0, tk.END)
            self.entry_variante_produto.delete(0, tk.END)
            self.entry_descricao.delete(0, tk.END)
            self.entry_materiais.delete(0, tk.END)
            self.entry_custo_producao.delete(0, tk.END)
            self.entry_tempo_producao.delete(0, tk.END)
            self.entry_preco_venda.delete(0, tk.END)
            self.label_margem_lucro.config(text="0.00%")  # Reseta a margem no label

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao cadastrar o produto: {e}")


if __name__ == "__main__":
    app = AppAtelie()
    app.mainloop()