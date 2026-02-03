import database.connection as db_connection

class databaseService:
    @staticmethod
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
                """, (Produto['Nome'], Produto['validade'], Produto['valor'], Produto['descricao'], Produto['quantidade'], Produto['lote']))
                conn.commit()
                cursor.close()
                conn.close()
            
        except Exception as e:
            print(f"Error importing product: {e}")
            cursor.close()
            conn.close()

    @staticmethod
    def deleteProduct(product_id):  
        try:
            conn, cursor = db_connection.connect_db()
            if not databaseService.verifyProductById(product_id):
                print("Product does not exist. Cannot delete.")
                cursor.close()
                conn.close()
                return
            else:
                cursor.execute("UPDATE produto SET in_store = 0 WHERE produto_id = ?", (product_id  ,))
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error deleting product: {e}")
            cursor.close()
            conn.close()

    @staticmethod
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

    @staticmethod
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
    
    @staticmethod
    def exportAllProducts():
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("SELECT produto_id, nome, validade, valor, descricao, quantidade, lote, in_store FROM produto")
            result = cursor.fetchall()
            cursor.close() 
            conn.close()
            return result
        except Exception as e:
            print(f"Error exporting all products: {e}")

    @staticmethod
    def updateProduct(name, updated_data):
        try:
            conn, cursor = db_connection.connect_db()
            if not databaseService.verifyProduct(name):
                print("Product does not exist. Cannot update.")
                cursor.close()
                conn.close()
                return
            else:
                if updated_data['quantidade'] == 0:
                    updated_data['in_store'] = 0
                else:
                    updated_data['in_store'] = 1
                cursor.execute("""
                    UPDATE produto
                    SET validade = ?, valor = ?, descricao = ?, quantidade = ?, lote = ?, in_store = ?
                    WHERE Nome = ?
                """, (updated_data['validade'], updated_data['valor'], updated_data['descricao'], updated_data['quantidade'], updated_data['lote'], updated_data['in_store'], name))
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error updating product: {e}")
            cursor.close()
            conn.close()


    @staticmethod
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
    def verifyProductById(produto_id):
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("SELECT * FROM produto WHERE produto_id = ?", (produto_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Error verifying product by ID: {e}")
            cursor.close()
            conn.close()
            return False

    @staticmethod
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
        
    @staticmethod
    def saveLog(action, product_name):
        try:
            conn, cursor = db_connection.connect_db()
            if not databaseService.get_product_id_by_name(product_name):
                print("Product does not exist. Log not saved.")
                cursor.close()
                conn.close()
                return
            else:
                cursor.execute("""
                    INSERT INTO logs (action, produto_id, product_name)
                    VALUES (?, ?, ?)
                """, (action, databaseService.get_product_id_by_name(product_name), product_name))
                conn.commit()
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error saving log: {e}")
            cursor.close()
            conn.close()

    @staticmethod
    def get_product_id_by_name(name):
        try:
            conn, cursor = db_connection.connect_db()
            cursor.execute("SELECT produto_id FROM produto WHERE Nome = ?", (name,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return row[0]
            return None
        except Exception as e:
            print(f"Error getting product id: {e}")
            try:
                cursor.close()
            except:
                pass
            try:
                conn.close()
            except:
                pass
            return None