import tkinter as tk
from tkinter import ttk, messagebox
import services.db_services as Services


def run():
    root = tk.Tk()
    root.title("Estoque - Interface")
    root.geometry("900x420")

    columns = ('ID', 'nome', 'validade', 'valor', 'descricao', 'quantidade', 'lote')
    tree = ttk.Treeview(root, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col.capitalize())
        tree.column(col, width=120)
    tree.pack(fill='both', expand=True, padx=6, pady=6)

    frm = ttk.Frame(root)
    frm.pack(fill='x', padx=6, pady=4)

    labels = ['Nome', 'Descricao', 'validade', 'valor', 'Quantidade', 'lote']
    entries = {}
    for i, label in enumerate(labels):
        ttk.Label(frm, text=label).grid(row=0, column=i, padx=4)
        e = ttk.Entry(frm, width=16)
        e.grid(row=1, column=i, padx=4)
        entries[label] = e

    def load_products():
        for i in tree.get_children():
            tree.delete(i)
        products = Services.databaseService.exportAllProducts() or []
        for row in products:
            tree.insert('', 'end', values=row)

    def add_product():
        try:
            prod = {
                'Nome': entries['Nome'].get(),
                'Descricao': entries['Descricao'].get(),
                'validade': entries['validade'].get(),
                'valor': float(entries['valor'].get()) if entries['valor'].get() else 0.0,
                'Quantidade': int(entries['Quantidade'].get()) if entries['Quantidade'].get() else 0,
                'lote': entries['lote'].get()
            }
            Services.databaseService.importProduct(prod)
            messagebox.showinfo('Sucesso', 'Produto importado com sucesso')
            load_products()
        except Exception as e:
            messagebox.showerror('Erro', str(e))

    btn_frame = ttk.Frame(root)
    btn_frame.pack(fill='x', padx=6, pady=6)
    ttk.Button(btn_frame, text='Refresh', command=load_products).pack(side='left', padx=6)
    ttk.Button(btn_frame, text='Add Product', command=add_product).pack(side='left')

    load_products()
    root.mainloop()


if __name__ == '__main__':
    run()
