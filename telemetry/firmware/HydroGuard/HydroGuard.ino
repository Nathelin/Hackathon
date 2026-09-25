/* B10K: extremos a 3V3/GND, cursor a GPIO 34, 33, 32 y 35.
 * Los valores físicos se simulan en Python usando el ADC, no una sonda real.
 * Compatible con el firmware de cuatro canales del primer prototipo.
 */
constexpr uint8_t PINS[] = {34, 33, 32, 35};
uint32_t lastSample = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
  for (uint8_t pin : PINS) analogSetPinAttenuation(pin, ADC_11db);
}

void loop() {
  if (millis() - lastSample < 150) return;
  lastSample = millis();
  Serial.print("{\"channels\":[");
  for (uint8_t i = 0; i < 4; i++) {
    analogRead(PINS[i]); // Descartar la primera conversión tras cambiar de canal.
    uint32_t total = 0;
    for (uint8_t n = 0; n < 16; n++) total += analogRead(PINS[i]);
    if (i) Serial.print(',');
    Serial.printf("{\"pin\":%u,\"raw\":%u}", PINS[i], unsigned(total / 16));
  }
  Serial.println("]}");
}
