# Importação das bibliotecas necessárias
import cv2
import time
import serial
import pymysql.cursors
from datetime import datetime

# Função para inserir dados no banco de dados MySQL
def insert_data(name, percentual, date):
    try:
        # Conectar ao banco de dados MySQL usando PyMySQL
        connection = pymysql.connect(
            host='localhost',       # Host BD
            user='root',      # Usuário BD
            #password='',    # Senha BD
            #port='3306', # Porta BD
            database='gaptrash_materials'  # Nome do BD
        )

        cursor = connection.cursor()

        # Query de inserção de dados
        insert_query = """
        INSERT INTO tipo_do_material (name, percentual, date)
        VALUES (%s, %s, %s)
        """
        data = (name, percentual, date)

        # Executando a query e confirmando a transação
        cursor.execute(insert_query, data)
        connection.commit()

        print("Dados inseridos com sucesso no banco de dados!")

    except pymysql.MySQLError as error:
        print(f"Erro ao inserir no MySQL: {error}")

    finally:
        if connection:
            cursor.close()
            connection.close()

# Estabelecendo a conexão com o Arduino
try:
    conectado = serial.Serial("COM3", 115200, timeout=0.5)
    print("Conectado com a porta", conectado.portstr)
except serial.SerialException:
    print("Porta USB não detectada")

# Cores das classes
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

# Carrega as classes
class_names = []
with open("coco.names", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]

# Mapeamento de objetos para materiais
material_map = {
    "bottle": "Plástico",
    "spoon": "Metal",
    "cup": "Vidro",
    "book": "Papel"
}

# Captura do vídeo
cap = cv2.VideoCapture(1)

# Carregando os pesos da rede neural
net = cv2.dnn.readNet("yolov4-tiny.cfg", "yolov4-tiny.weights")

# Setando os parâmetros da rede neural
model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255)

# Classes a serem filtradas
target_classes = ["bottle", "spoon", "cup", "book"]

# Lendo os frames do vídeo
while True:
    # Captura do frame
    _, frame = cap.read()

    # Começo da contagem dos ms
    start = time.time()

    # Detecção
    classes, scores, boxes = model.detect(frame, 0.1, 0.2)

    # Fim da contagem dos ms
    end = time.time()

    # Inicializa a variável para armazenar a classe detectada
    detected_class = None

    # Percorrer todas as detecções
    for (classid, score, box) in zip(classes, scores, boxes):
        # Pegar o nome da classe detectada
        detected_class = class_names[classid]
        
        # Verificar se a classe detectada é uma das quatro filtradas (bottle, spoon, cup, book)
        if detected_class in target_classes:
            # Gerando uma cor para a classe
            color = COLORS[int(classid) % len(COLORS)]
            # Pegando o nome da classe pelo ID e seu score de acurácia
            material = material_map.get(detected_class, "Desconhecido")
            label = f"{material} : {score:.2f}"
            # Desenhando a box da detecção
            cv2.rectangle(frame, box, color, 2)
            # Escrevendo o nome do material em vez da classe em cima da box do objeto
            cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Adicionando o print para exibir o tipo do material no terminal
            print(material)

            # Inserir os dados no banco de dados
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_data(material, round(score * 100, 2), current_time)

            # Enviar o comando específico ao Arduino baseado na classe detectada
            if detected_class == "bottle":
                conectado.write(b'1')  # Enviar '1' para o Arduino
            elif detected_class == "spoon":
                conectado.write(b'2')  # Enviar '2' para o Arduino
            elif detected_class == "cup":
                conectado.write(b'3')  # Enviar '3' para o Arduino
            elif detected_class == "book":
                conectado.write(b'4')  # Enviar '4' para o Arduino

            break  # Sai do loop após detectar uma classe válida

        else:
            # Se a classe detectada não for bottle, spoon, cup ou book
            color = (0, 0, 255)  # Vermelho para indicar "Outros"
            label = f"Outros : {score:.2f}"  # Escrever "Outros"
            # Desenhando a box da detecção
            cv2.rectangle(frame, box, color, 2)
            # Escrevendo a palavra "Outros" em cima da box do objeto
            cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Enviar o comando '5' para o Arduino para objetos não filtrados
            conectado.write(b'5')
            print("Outros")

            # Inserir os dados no banco de dados
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_data("Outros", round(score * 100, 2), current_time)

            break  # Sai do loop após detectar uma classe não filtrada

    # Calculando o tempo que levou pra fazer a detecção
    fps_label = f"FPS: {round((1.0/(end - start)), 2)}"

    # Escrevendo o FPS na imagem
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 5)
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    # Mostrando a imagem
    cv2.imshow("GapTrash", frame)

    # Espera da resposta
    if cv2.waitKey(1) == 27:
        break

# Liberação da câmera e destruição de todas as janelas
cap.release()
cv2.destroyAllWindows()
