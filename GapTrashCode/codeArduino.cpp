#include <Servo.h>

Servo meuServo;  // Cria um objeto da classe Servo para controlar o servo motor

void setup() {
  Serial.begin(115200);  // Inicializa a comunicação serial
  meuServo.attach(9);    // Define o pino digital ao qual o servo motor está conectado (pode ser alterado se necessário)
  meuServo.write(0);     // Inicializa o servo na posição 0 graus
}

void loop() {
  // Verifica se há dados disponíveis para leitura na porta serial
  if (Serial.available() > 0) {
    int dado = Serial.read();  // Lê o dado recebido via serial
    
    // Verifica qual comando foi recebido e move o servo motor de acordo
    if (dado == '1') {
      meuServo.write(45);  // Move o servo para 45 graus
      Serial.println("Servo movido Plástico");
    }
    else if (dado == '2') {
      meuServo.write(90);  // Move o servo para 90 graus
      Serial.println("Servo movido para Metal");
    }
    else if (dado == '3') {
      meuServo.write(135);  // Move o servo para 135 graus
      Serial.println("Servo movido para Vidro");
    }
    else if (dado == '4') {
      meuServo.write(180);  // Move o servo para 180 graus
      Serial.println("Servo movido para Papel");
    }
    else if (dado == '5') {
      meuServo.write(0);  // Move o servo para 0 graus
      Serial.println("Servo movido para Outros");
    }
  }
}
