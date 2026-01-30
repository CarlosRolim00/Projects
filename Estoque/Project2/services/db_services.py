import database.connection as db_connection

class databaseService:
    def importProduct(Produto):
        try:
            conn, cursor = db_connection.connect_db()
            if databaseService.verifyLote(Produto['lote']) and databaseService.verifyProduct(Produto['Nome']):
                print("Product already exists. Product not imported.")
                cursor.close()
                conn.close()
                return
            else:
                cursor.execute("""
                    INSERT INTO produto (Nome, validade, valor, descricao, quantidade, lote)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (Produto['Nome'], Produto['validade'], Produto['valor'], Produto['Descricao'], Produto['Quantidade'], Produto['lote']))
                conn.commit()
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"Error importing product: {e}")
            cursor.close()
            conn.close()

    def exportProductByName(name):
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("""
                SELECT * FROM produto WHERE Nome = ?
            """, (name))
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        except Exception as e:
            print(f"Error exporting product: {e}")

    def exportProductByNameLote(name, lote):
        try:
            if not databaseService.verifyLote(lote) or not databaseService.verifyProduct(name):
                return print("Lote or product does not exist.")
            else:
                conn, cursor = db_connection.connect_db()
                cursor.execute("""
                    SELECT * FROM produto WHERE Nome = ? AND lote = ?
                """, (name, lote))
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                return result
        except Exception as e:
            print(f"Error exporting product by name and lote: {e}")
    
    def exportAllProducts():
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("SELECT * FROM produto")
            result = cursor.fetchall()
            cursor.close()
            conn.close()

            for row in result:
                print(row)
            return result
        except Exception as e:
            print(f"Error exporting all products: {e}")

    def updateProduct(name, updated_data):
        try:
            conn, cursor = db_connection.connect_db()
            if not databaseService.verifyProduct(name):
                print("Product does not exist. Cannot update.")
                cursor.close()
                conn.close()
                return
            else:
                cursor.execute("""
                    UPDATE produto
                    SET validade = ?, valor = ?, descricao = ?, quantidade = ?, lote = ?
                    WHERE Nome = ?
                """, (updated_data['validade'], updated_data['valor'], updated_data['Descricao'], updated_data['Quantidade'], updated_data['lote'], name))
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error updating product: {e}")
            cursor.close()
            conn.close()


    def verifyProduct(nome):
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("SELECT * FROM produto WHERE Nome = ?", (nome,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Error verifying product: {e}")
            cursor.close()
            conn.close()
            return False

    def verifyLote(lote):
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("SELECT * FROM produto WHERE lote = ?", (lote,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Error verifying lote: {e}")
            cursor.close()
            conn.close()
            return False