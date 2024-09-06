# Importação das bibliotecas necessárias
import cv2
import time
import serial

try:
#Estabelecendo a conexão com o arduino
    conectado = serial.Serial("COM4", 115200, timeout=0.5)
    #print(conectado)
    print("Conectado com a porta", conectado.portstr)
except serial.SerialException:
    print("Porta USB não detectada")

# Cores das classes
COLORS = [(0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)]

# Carrega as classes
class_names = []
with open("coco.names", "r") as f:
    class_names = [cname.strip() for cname in f.readlines()]
    
# Captura do vídeo
cap = cv2.VideoCapture(0)

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
        # Verificar se a classe detectada é uma das filtradas
        if class_names[classid] in target_classes:
            detected_class = class_names[classid]
            # Gerando uma cor para a classe
            color = COLORS[int(classid) % len(COLORS)]
            # Pegando o nome da classe pelo ID e seu score de acurácia
            label = f"{class_names[classid]} : {score}"
            # Desenhando a box da detecção
            cv2.rectangle(frame, box, color, 2)
            # Escrevendo o nome da classe em cima da box do objeto
            cv2.putText(frame, label, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Adicionando o print para exibir o nome da classe detectada no terminal
            print(f"Objeto detectado: {detected_class}")
            
            # Validação para enviar comandos específicos ao Arduino
            if detected_class == "bottle":
                conectado.write(b'1')  # Enviar '1' para o Arduino
                #print("Comando 1 enviado para o Arduino.")
            elif detected_class == "spoon":
                conectado.write(b'2')  # Enviar '2' para o Arduino
                #print("Comando 2 enviado para o Arduino.")
            elif detected_class == "cup":
                conectado.write(b'3')  # Enviar '3' para o Arduino
                #print("Comando 3 enviado para o Arduino.")
            elif detected_class == "book":
                conectado.write(b'4')  # Enviar '4' para o Arduino
                #print("Comando 4 enviado para o Arduino.")
            
            break  # Sai do loop após detectar uma classe válida
    
    # Calculando o tempo que levou pra fazer a detecção
    fps_label = f"FPS: {round((1.0/(end - start)), 2)}"
    
    # Escrevendo o FPS na imagem
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 5)
    cv2.putText(frame, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    
    # Mostrando a imagem
    cv2.imshow("Detections", frame)
    
    # Espera da resposta
    if cv2.waitKey(1) == 27:
        break

# Liberação da câmera e destruição de todas as janelas
cap.release()
cv2.destroyAllWindows()
