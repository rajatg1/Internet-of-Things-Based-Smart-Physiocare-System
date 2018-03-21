#include <Time.h>
#include <TimeLib.h>

#include <ESP8266WiFi.h>
#include <FirebaseArduino.h>
#include <algorithm>

const char *WIFI_SSID = "Timothy's iPhone";
const char *WIFI_PW = "1234567890";

#define FIREBASE_HOST "rehab-thing.firebaseio.com"
#define FIREBASE_AUTH ""

#define SENSOR "muscle"

#define MESSAGE_MAX_LEN 512

static const int myo_sensor_pin = A0;
static const int calibration_time = 15; // in seconds

static int emg_threshold = -1;

/* // JSON schema
 * {
 *   "sensor":"string",
 *   "time":int,
 *   "emg":int,
 *   "threshold":boolean
 * }
 */

void calibrate_threshold() {
  for (int i = 0; i < calibration_time; i++) {
    int emg = analogRead(myo_sensor_pin);
    emg_threshold = std::max(emg_threshold, emg);
    delay(1000);
  }
}

void print_mac() {
  uint8_t mac[6];
  WiFi.macAddress(mac);
  Serial.print("mac address: ");
  Serial.print(mac[0], HEX);
  Serial.print(":");
  Serial.print(mac[1], HEX);
  Serial.print(":");
  Serial.print(mac[2], HEX);
  Serial.print(":");
  Serial.print(mac[3], HEX);
  Serial.print(":");
  Serial.print(mac[4], HEX);
  Serial.print(":");
  Serial.println(mac[5], HEX);
}

void setup() {
  Serial.begin(9600);

  calibrate_threshold();
  Serial.print("session threshold: ");
  Serial.println(emg_threshold);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PW);
  print_mac();
  Serial.print("connecting to ");
  Serial.println(WIFI_SSID);
  
  while (WiFi.status() != WL_CONNECTED) {
    Serial.println("... failed to connect... retrying in 10 seconds");
    delay(10000);
    WiFi.begin(WIFI_SSID, WIFI_PW);
  }
  Serial.println();
  Serial.print("connected: ");
  Serial.println(WiFi.localIP());

  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
}

unsigned long get_time() {
  return now();
}

String read_emg() {
  StaticJsonBuffer<MESSAGE_MAX_LEN> json_buffer;
  JsonObject &root = json_buffer.createObject();
  root["sensor"] = SENSOR;

  unsigned long time = get_time();
  if (std::isnan(time)) {
    root["time"] = NULL;
  } else {
    root["time"] = time;
  }

  int emg = analogRead(myo_sensor_pin);
  if (std::isnan(emg)) {
    root["emg"] = NULL;
    root["threshold"] = NULL;
  } else {
    root["emg"] = emg;
    root["threshold"] = emg > emg_threshold ? true : false;
  }

  char json[MESSAGE_MAX_LEN];
  size_t sz = root.printTo(json, MESSAGE_MAX_LEN);
  Serial.print("bytes written: ");
  Serial.print(sz);
  Serial.print(" ");
  Serial.println(json);
  return String(json);
}

void loop() {
  String emg_reading = std::move(read_emg());
  if (emg_reading.length() > 2) {
    Firebase.pushString("emg", emg_reading);
    if (Firebase.failed()) {
      Serial.print("setting /emg failed:");
      Serial.println(Firebase.error());  
      return;
    } else {
      Serial.println("set /emg");
    }
  }
  
  delay(3000);
}
