import concurrent.futures
import sqlite3
import grpc

import sensores_pb2
import sensores_pb2_grpc

DB_PATH = "sensores.db"

# Inicializar BD SQLite con datos iniciales si no existen
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sectores (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            plazas_totales INTEGER NOT NULL,
            plazas_libres INTEGER NOT NULL
        )
    ''')
    cursor.execute("SELECT COUNT(*) FROM sectores")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO sectores (id, nombre, plazas_totales, plazas_libres)
            VALUES (?, ?, ?, ?)
        ''', [
            ("sec-a", "Sector A - Subterráneo", 50, 10),
            ("sec-b", "Sector B - Superficie", 30, 0),
            ("sec-c", "Sector C - VIP", 15, 5)
        ])
        conn.commit()
    conn.close()

# Implementacion de metodos del gRPC
class SensoresServicer(sensores_pb2_grpc.SensoresServiceServicer):

    # Consultar datos de sector por ID y retornar plazas disponibles
    def ConsultarSector(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT id, nombre, plazas_totales, plazas_libres FROM sectores WHERE id = ?", (request.sector_id,))
        row = cursor.fetchone()
        conn.close()

        # Retornar respuesta gRPC si existe, codigo NOT_FOUND si no
        if row:
            return sensores_pb2.SectorResponse(
                sector_id=row[0],
                nombre=row[1],
                plazas_totales=row[2],
                plazas_libres=row[3]
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Sector no encontrado")
            return sensores_pb2.SectorResponse()
        
    # Lista de sectores disponibles
    def ListarSectores(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Obtener todos los sectores
        cursor.execute("SELECT id, nombre, plazas_totales, plazas_libres FROM sectores")
        rows = cursor.fetchall()
        conn.close()

        # Lista de respuestas gRPC
        sectores = [
            sensores_pb2.SectorResponse(
                sector_id=r[0], nombre=r[1], plazas_totales=r[2], plazas_libres=r[3]
            ) for r in rows
        ]
        return sensores_pb2.SectoresListResponse(sectores=sectores)

    # Restar 1 a plazas libres (operación atómica para evitar race condition)
    def OcuparPlaza(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # UPDATE atómico: solo decrementa si hay plazas libres > 0
        cursor.execute(
            "UPDATE sectores SET plazas_libres = plazas_libres - 1 WHERE id = ? AND plazas_libres > 0",
            (request.sector_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            # No se actualizó: el sector no existe o está lleno
            cursor.execute("SELECT plazas_libres FROM sectores WHERE id = ?", (request.sector_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return sensores_pb2.OperacionResponse(exito=False, mensaje="Sector inexistente", plazas_libres_restantes=0)
            return sensores_pb2.OperacionResponse(exito=False, mensaje="Sector lleno", plazas_libres_restantes=0)

        # Leer el valor actualizado para informar al cliente
        cursor.execute("SELECT plazas_libres FROM sectores WHERE id = ?", (request.sector_id,))
        nuevas_libres = cursor.fetchone()[0]
        conn.close()

        return sensores_pb2.OperacionResponse(exito=True, mensaje="Plaza ocupada con éxito", plazas_libres_restantes=nuevas_libres)

    # Sumar 1 a plazas libres (operación atómica para evitar race condition)
    def LiberarPlaza(self, request, context):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # UPDATE atómico: solo incrementa si plazas_libres < plazas_totales
        cursor.execute(
            "UPDATE sectores SET plazas_libres = plazas_libres + 1 WHERE id = ? AND plazas_libres < plazas_totales",
            (request.sector_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            # No se actualizó: el sector no existe o ya está a máxima capacidad
            cursor.execute("SELECT plazas_totales, plazas_libres FROM sectores WHERE id = ?", (request.sector_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return sensores_pb2.OperacionResponse(exito=False, mensaje="Sector inexistente", plazas_libres_restantes=0)
            return sensores_pb2.OperacionResponse(exito=False, mensaje="Sector ya está a máxima capacidad", plazas_libres_restantes=row[1])

        # Leer el valor actualizado para informar al cliente
        cursor.execute("SELECT plazas_libres FROM sectores WHERE id = ?", (request.sector_id,))
        nuevas_libres = cursor.fetchone()[0]
        conn.close()

        return sensores_pb2.OperacionResponse(exito=True, mensaje="Plaza liberada con éxito", plazas_libres_restantes=nuevas_libres)

# Iniciar servidor gRPC en el puerto 50051
def serve():
    init_db()
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    sensores_pb2_grpc.add_SensoresServiceServicer_to_server(SensoresServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Servidor gRPC de Sensores corriendo en puerto 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()