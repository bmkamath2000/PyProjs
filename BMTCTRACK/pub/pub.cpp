#include <WiFi.h>
#include <PubSubClient.h>

#define IR1_PIN 34  // first beam (inner)
#define IR2_PIN 35  // second beam (outer)

const char* ssid       = "Ise Staffroom";
const char* password   = "XXXXXXXXXXXXX";
const char* mqttServer = "192.168.0.171"; // your broker IP
const int   mqttPort   = 1883;
const char* topic      = "bus/passengers";

WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);

int passengerCount = 0;
bool ir1Triggered = false;
bool ir2Triggered = false;
unsigned long ir1Time = 0;

void setup() {
  pinMode(IR1_PIN, INPUT);
  pinMode(IR2_PIN, INPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  mqtt.setServer(mqttServer, mqttPort);
  while (!mqtt.connected()) {
    mqtt.connect("esp32-bus");
    delay(500);
  }
}

void loop() {
  mqtt.loop();

  bool s1 = digitalRead(IR1_PIN) == LOW; // beam broken = LOW
  bool s2 = digitalRead(IR2_PIN) == LOW;

  // Detect direction: IR1 first = entering, IR2 first = exiting
  if (s1 && !ir1Triggered) { ir1Triggered = true; ir1Time = millis(); }
  if (s2 && ir1Triggered && (millis() - ir1Time < 1000)) {
    passengerCount++;   // entered
    ir1Triggered = false;
    publishCount();
  }
  if (s2 && !ir1Triggered) {
    if (passengerCount > 0) passengerCount--;  // exited
    publishCount();
  }
  if (!s1) ir1Triggered = false;
}

void publishCount() {
  String payload = "{\"count\":" + String(passengerCount) + 
                   ",\"busId\":\"BUS_01\"}";
  mqtt.publish(topic, payload.c_str());
}
