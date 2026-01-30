

class produto:
    def __init__(self, nome, preco, quantidade, lote, validade, valor):
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
        self.lote = lote
        self.validade = validade
        self.valor = valor

    def display_info(self):
        print(f"Nome: {self.nome}")
        print(f"Preço: {self.preco}")
        print(f"Quantidade: {self.quantidade}")
        print(f"Lote: {self.lote}")
        print(f"Validade: {self.validade}")
        print(f"Valor do Lote: {self.valor}")
    
    def to_dict(self):
        return {
            'Nome': self.nome,
            'Preco': self.preco,
            'Quantidade': self.quantidade,
            'lote': self.lote,
            'validade': self.validade,
            'valor_lote': self.valor
        }