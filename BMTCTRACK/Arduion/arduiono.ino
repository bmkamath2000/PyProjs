#include <WiFi.h>
#include <PubSubClient.h>

#define IR_PIN 34

const char* ssid       = "Ise Staffroom";
const char* password   = "JitIse@2026";
const char* mqttServer = "192.168.0.171";
const int   mqttPort   = 1883;
const char* topic      = "bus/passengers";

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

int  obstacleCount = 0;
bool lastState     = false;  // tracks if beam was broken last loop

void setup() {
  Serial.begin(115200);
  pinMode(IR_PIN, INPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  Serial.println("WiFi connected");

  mqtt.setServer(mqttServer, mqttPort);
  while (!mqtt.connected()) {
    mqtt.connect("esp32-bus");
    delay(500);
  }
  Serial.println("MQTT connected");
}

void loop() {
  mqtt.loop();

  bool beamBroken = digitalRead(IR_PIN) == LOW;

  // Count on the rising edge only (moment beam first breaks)
  if (beamBroken && !lastState) {
    obstacleCount++;
    Serial.print("Obstacle count: ");
    Serial.println(obstacleCount);

    String payload = "{\"count\":" + String(obstacleCount) + ",\"busId\":\"BUS_01\"}";
    mqtt.publish(topic, payload.c_str());
  }

  lastState = beamBroken;
  delay(50);  // debounce
}