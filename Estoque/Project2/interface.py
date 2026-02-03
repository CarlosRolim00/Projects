import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import services.db_services as Services


def run():
    root = tk.Tk()
    root.title("Estoque - Gerenciador de Produtos")
    root.geometry("1200x700")
    root.resizable(True, True)
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use('clam')

    # Frame superior - Busca
    search_frame = ttk.LabelFrame(root, text="Busca", padding=10)
    search_frame.pack(fill='x', padx=10, pady=10)
    
    ttk.Label(search_frame, text="Filtrar por nome:").pack(side='left', padx=5)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
    search_entry.pack(side='left', padx=5)

    # Frame para tabela
    tree_frame = ttk.LabelFrame(root, text="Produtos Cadastrados", padding=10)
    tree_frame.pack(fill='both', expand=True, padx=10, pady=5)

    columns = ('ID', 'Nome', 'Validade', 'Valor', 'Descrição', 'Quantidade', 'Lote')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
    
    # Configurar colunas
    col_widths = {'ID': 40, 'Nome': 120, 'Validade': 100, 'Valor': 80, 'Descrição': 150, 'Quantidade': 80, 'Lote': 80}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=col_widths.get(col, 100), anchor='center')
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    tree.pack(side='left', fill='both', expand=True)
    scrollbar.pack(side='right', fill='y')

    # (Removido) Bloco de entrada embutida: agora usa popup para adicionar/editar produtos

    def validate_inputs(prod):
        if not prod['Nome'].strip():
            raise ValueError("Nome do produto é obrigatório")
        if not prod['validade'].strip():
            raise ValueError("Data de validade é obrigatória")
        
        # Validar data
        try:
            datetime.strptime(prod['validade'], '%d/%m/%Y')
        except ValueError:
            raise ValueError("Data inválida! Use o formato DD/MM/YYYY")
        
        try:
            if prod['valor']:
                float(prod['valor'])
        except ValueError:
            raise ValueError("Valor deve ser um número")
        
        try:
            if prod['quantidade']:
                int(prod['quantidade'])
        except ValueError:
            raise ValueError("Quantidade deve ser um número inteiro")

    def create_date_formatter(entry):
        """Retorna um handler para formatar data como DD/MM/YYYY preservando o cursor."""
        def on_format(event=None):
            cur = entry.get()
            cur_pos = entry.index(tk.INSERT)
            digits = ''.join([c for c in cur if c.isdigit()])[:8]

            # montar formato
            parts = []
            if len(digits) >= 2:
                parts.append(digits[:2])
                if len(digits) >= 4:
                    parts.append(digits[2:4])
                    if len(digits) > 4:
                        parts.append(digits[4:8])
                elif len(digits) > 2:
                    parts.append(digits[2:])
            else:
                parts.append(digits)

            formatted = '/'.join(parts)

            if formatted != cur:
                digits_before = sum(1 for ch in cur[:cur_pos] if ch.isdigit())
                new_pos = digits_before
                if digits_before > 2:
                    new_pos += 1
                if digits_before > 4:
                    new_pos += 1

                entry.delete(0, 'end')
                entry.insert(0, formatted)
                entry.icursor(min(new_pos, len(formatted)))

        return on_format

    def format_date_value(val):
        """Converte `val` para string no formato DD/MM/YYYY quando possível."""
        if not val:
            return ''
        s = str(val).strip()
        # já está no formato desejado
        try:
            datetime.strptime(s, '%d/%m/%Y')
            return s
        except Exception:
            pass

        # tentar formatos comuns
        for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%d.%m.%Y', '%Y%m%d'):
            try:
                dt = datetime.strptime(s, fmt)
                return dt.strftime('%d/%m/%Y')
            except Exception:
                continue

        # tentar extrair 8 dígitos
        digits = ''.join(c for c in s if c.isdigit())
        if len(digits) == 8:
            # testar YYYYMMDD
            try:
                dt = datetime.strptime(digits, '%Y%m%d')
                return dt.strftime('%d/%m/%Y')
            except Exception:
                pass
            # testar DDMMYYYY
            try:
                dt = datetime.strptime(digits, '%d%m%Y')
                return dt.strftime('%d/%m/%Y')
            except Exception:
                pass

        # fallback: retornar original
        return s

    def load_products(filter_text=""):
        for i in tree.get_children():
            tree.delete(i)
        
        try:
            products = Services.databaseService.exportAllProducts() or []
          
            for row in products:
                if not row:
                    continue
                
                try:
                    # Extrair cada parte do produto
                    product_id = row[0]
                    product_name = row[1]
                    product_validity = row[2]
                    product_value = row[3]
                    product_description = row[4]
                    product_quantity = row[5]
                    product_batch = row[6] 
                    product_inStore = row[7]
                    if product_inStore == 0:
                        continue  # Pular produtos que não estão em estoque
                    # Filtrar por nome se houver texto de busca
                    if filter_text.lower() in str(product_name).lower():
                        tree.insert('', 'end', values=(product_id, product_name, product_validity, 
                                                       product_value, product_description, 
                                                       product_quantity, product_batch))
                except IndexError as e:
                    print(f"Erro ao processar linha do produto: {e}")
                    continue
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao carregar produtos:\n{str(e)}')


    def open_add_popup():
        add_window = tk.Toplevel(root)
        add_window.title("Adicionar Produto")
        add_window.geometry("500x400")
        add_window.resizable(False, False)

        main_frame = ttk.Frame(add_window, padding=15)
        main_frame.pack(fill='both', expand=True)

        popup_entries = {}

        fields_info = [
            ('Nome', ''),
            ('validade', ''),
            ('valor', ''),
            ('descricao', ''),
            ('quantidade', ''),
            ('lote', '')
        ]

        for i, (label, value) in enumerate(fields_info):
            ttk.Label(main_frame, text=label.capitalize(), font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=8)
            entry = ttk.Entry(main_frame, width=40)
            entry.insert(0, value)
            entry.grid(row=i, column=1, sticky='ew', pady=8, padx=10)
            popup_entries[label] = entry

            if label == 'validade':
                entry.bind('<KeyRelease>', create_date_formatter(entry))

        main_frame.columnconfigure(1, weight=1)

        btn_frame_popup = ttk.Frame(main_frame)
        btn_frame_popup.grid(row=len(fields_info), column=0, columnspan=2, pady=20)

        def save_new_product():
            try:
                prod = {
                    'Nome': popup_entries['Nome'].get(),
                    'descricao': popup_entries['descricao'].get(),
                    'validade': popup_entries['validade'].get(),
                    'valor': float(popup_entries['valor'].get()) if popup_entries['valor'].get() else 0.0,
                    'quantidade': int(popup_entries['quantidade'].get()) if popup_entries['quantidade'].get() else 0,
                    'lote': popup_entries['lote'].get()
                }

                validate_inputs(prod)
                Services.databaseService.importProduct(prod)
                Services.databaseService.saveLog(f"Adicao do produto {prod['Nome']}, na quantidade {prod['quantidade']} com validade {prod['validade']}", prod['Nome'])
                messagebox.showinfo('Sucesso', 'Produto adicionado com sucesso!')
                
                add_window.destroy()
                load_products(search_var.get())
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao adicionar produto:\n{str(e)}')

        ttk.Button(btn_frame_popup, text='✓ Salvar', command=save_new_product).pack(side='left', padx=10)
        ttk.Button(btn_frame_popup, text='✕ Cancelar', command=add_window.destroy).pack(side='left', padx=10)

    def load_selected_product():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning('Aviso', 'Selecione um produto para editar')
            return
        
        item = tree.item(selection[0])
        values = item['values']
        
        # Criar janela popup
        edit_window = tk.Toplevel(root)
        edit_window.title("Editar Produto")
        edit_window.geometry("500x400")
        edit_window.resizable(False, False)
        
        # Frame principal da janela
        main_frame = ttk.Frame(edit_window, padding=15)
        main_frame.pack(fill='both', expand=True)
        
        # Dicionário para armazenar os campos
        edit_entries = {}
        
        # Criar campos de entrada pré-preenchidos
        fields_info = [
            ('Nome', str(values[1]).strip() if values[1] else ''),
            ('validade', format_date_value(values[2]) if values[2] else ''),
            ('valor', str(values[3]).strip() if values[3] else ''),
            ('descricao', str(values[4]).strip() if values[4] else ''),
            ('quantidade', str(values[5]).strip() if values[5] else ''),
            ('lote', str(values[6]).strip() if values[6] else '')
        ]
        
        for i, (label, value) in enumerate(fields_info):
            ttk.Label(main_frame, text=label.capitalize(), font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=8)
            entry = ttk.Entry(main_frame, width=40)
            entry.insert(0, value)
            entry.grid(row=i, column=1, sticky='ew', pady=8, padx=10)
            edit_entries[label] = entry
            
            # Aplicar formatação de data se for o campo de validade
            if label == 'validade':
                entry.bind('<KeyRelease>', create_date_formatter(entry))
        
        main_frame.columnconfigure(1, weight=1)
        
        # Frame de botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=len(fields_info), column=0, columnspan=2, pady=20)
        
        def save_changes():
            try:
                # capture product name before destroying widgets
                product_name = edit_entries['Nome'].get()

                updated_data = {
                    'validade': edit_entries['validade'].get(),
                    'valor': float(edit_entries['valor'].get()) if edit_entries['valor'].get() else 0.0,
                    'descricao': edit_entries['descricao'].get(),
                    'quantidade': int(edit_entries['quantidade'].get()) if edit_entries['quantidade'].get() else 0,
                    'lote': edit_entries['lote'].get()
                }

                Services.databaseService.updateProduct(product_name, updated_data)
                # log before destroying the window, using captured name
                Services.databaseService.saveLog(f"update Product {product_name}", product_name)
                messagebox.showinfo('Sucesso', 'Produto atualizado com sucesso!')
                edit_window.destroy()
                load_products(search_var.get())
            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao atualizar produto:\n{str(e)}')

        ttk.Button(btn_frame, text='✓ Salvar', command=save_changes).pack(side='left', padx=10)
        ttk.Button(btn_frame, text='✕ Cancelar', command=edit_window.destroy).pack(side='left', padx=10)

    def delete_product():
        selection = tree.selection()
        if not selection:
            messagebox.showwarning('Aviso', 'Selecione um produto para deletar')
            return
        
        if messagebox.askyesno('Confirmar', 'Tem certeza que deseja deletar este produto?'):
            try:
                item = tree.item(selection[0])
                product_id = item['values'][0]
                print(f"Deletando produto ID {product_id}...")
                Services.databaseService.deleteProduct(product_id)
                Services.databaseService.saveLog(f"Delecao do produto ID {product_id}", item['values'][1])
                messagebox.showinfo('Sucesso', 'Produto deletado com sucesso!')
                load_products(search_var.get())

            except Exception as e:
                messagebox.showerror('Erro', f'Erro ao deletar: {str(e)}')

    # Frame de botões
    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill='x', padx=10, pady=10)

    ttk.Button(btn_frame, text='✓ Adicionar Produto', command=open_add_popup).pack(side='left', padx=5)
    ttk.Button(btn_frame, text='📋 Carregar para Editar', command=load_selected_product).pack(side='left', padx=5)
    ttk.Button(btn_frame, text='🔄 Atualizar Lista', command=lambda: load_products(search_var.get())).pack(side='left', padx=5)
    ttk.Button(btn_frame, text='🗑 Deletar Produto', command=delete_product).pack(side='left', padx=5)
    
    # Atualizar lista ao digitar na busca
    def on_search_change(event=None):
        load_products(search_var.get())
    
    search_entry.bind('<KeyRelease>', on_search_change)

    load_products()
    root.mainloop()


if __name__ == '__main__':
    run()
