import os
import re
import fitz  # PyMuPDF para PDF
import docx
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from django.conf import settings
from .models import Ticket, SolucionTicket

class TicketSolutionSearch:
    def __init__(self):
        self.model = SentenceTransformer('all-mpnet-base-v2')
        self.tickets_data = []
        self.embeddings = None
        self.neigh = None
        self.load_data_and_build_index()

    def extraer_texto_pdf(self, ruta):
        texto = ""
        with fitz.open(ruta) as doc:
            for pagina in doc:
                texto += pagina.get_text()
        return texto

    def extraer_texto_docx(self, ruta):
        texto = ""
        doc = docx.Document(ruta)
        for parrafo in doc.paragraphs:
            texto += parrafo.text + "\n"
        return texto

    def cargar_textos_de_documentos(self, ruta_carpeta):
        textos = []
        for nombre in os.listdir(ruta_carpeta):
            ruta = os.path.join(ruta_carpeta, nombre)
            if nombre.endswith('.pdf'):
                textos.append(self.extraer_texto_pdf(ruta))
            elif nombre.endswith('.docx'):
                textos.append(self.extraer_texto_docx(ruta))
        return textos

    def load_data_and_build_index(self):
        self.tickets_data = []
        textos = []

        # ➤ Cargar datos desde base de datos
        for ticket in Ticket.objects.all():
            solucion = SolucionTicket.objects.filter(ticket=ticket).first()
            if solucion and ticket.descripcion and solucion.comentario:
                desc = ticket.descripcion.strip().lower()
                coment = solucion.comentario.strip()
                if len(coment) > 10 and desc != 'nan':
                    self.tickets_data.append({
                        'ticket_id': ticket.id,
                        'problema': desc,
                        'solucion': coment,
                        'origen': 'bd'
                    })
                    textos.append(desc)

        # ➤ Cargar textos desde manuales PDF/DOCX
        ruta_manual = os.path.join(settings.BASE_DIR, 'app_ticket', 'manuales')
        documentos = self.cargar_textos_de_documentos(ruta_manual)

        for doc_text in documentos:
            doc_text = re.sub(r'\n+', ' ', doc_text)  # Unifica saltos de línea
            doc_text = re.sub(r'\s{2,}', ' ', doc_text)  # Elimina espacios dobles

            # Expresión que busca cualquier frase que contenga un "problema" y su correspondiente "solución"
            patrones = re.findall(
                r'(problema\s*[:\-\.]?\s*)(.*?)(soluci[oó]n\s*[:\-\.]?\s*)(.*?)(?=(problema\s*[:\-\.]?|$))',
                doc_text,
                flags=re.IGNORECASE | re.DOTALL
            )

            for match in patrones:
                problema = match[1].strip()
                solucion = match[3].strip()

                if len(problema) > 20 and len(solucion) > 20:
                    self.tickets_data.append({
                        'ticket_id': None,
                        'problema': problema,
                        'solucion': solucion,
                        'origen': 'manual'
                    })
                    textos.append(problema)



        # ➤ Generar embeddings
        if textos:
            self.embeddings = self.model.encode(textos, convert_to_numpy=True, normalize_embeddings=True)
            n_neighbors = min(5, len(self.embeddings))
            self.neigh = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
            self.neigh.fit(self.embeddings)
        else:
            self.embeddings = None
            self.neigh = None

    def query(self, texto_usuario, top_k=3, umbral_similitud=0.35):
        if not self.neigh:
            return []

        texto_usuario = texto_usuario.strip().lower()
        query_vec = self.model.encode([texto_usuario], convert_to_numpy=True, normalize_embeddings=True)
        distances, indices = self.neigh.kneighbors(query_vec, n_neighbors=top_k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            similitud = 1 - dist
            if similitud >= umbral_similitud:
                entry = self.tickets_data[idx]
                results.append({
                    'ticket_id': entry['ticket_id'],
                    'problema': entry['problema'],
                    'solucion': entry['solucion'],
                    'similitud': round(similitud, 3),
                    'origen': entry.get('origen', 'bd')
                })

        if not results:
            results.append({
                'ticket_id': None,
                'problema': texto_usuario,
                'solucion': 'No se encontró una solución similar.',
                'similitud': 0.0,
                'origen': 'none'
            })

        return results
