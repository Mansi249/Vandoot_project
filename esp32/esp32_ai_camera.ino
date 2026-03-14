#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#include <WiFi.h>
#include "esp_camera.h"
#include "esp_http_server.h"

#include <tflm_esp32.h>
#include <eloquent_tinyml.h>
#include <eloquent_tinyml/tf.h>

#include "model_data.h"

/* WIFI */

const char* ssid = "Hotspot";
const char* password = "12345678";

/* CAMERA PINS (AI THINKER) */

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5

#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

/* AI SETTINGS */

#define NUMBER_OF_INPUTS 9216
#define NUMBER_OF_OUTPUTS 4
#define TENSOR_ARENA_SIZE 25*1024

Eloquent::TF::Sequential<NUMBER_OF_OUTPUTS, TENSOR_ARENA_SIZE> ml;

float *input_data;

/* STREAM HANDLER */

static esp_err_t stream_handler(httpd_req_t *req)
{
    camera_fb_t *fb = NULL;

    httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");

    while (true)
    {
        fb = esp_camera_fb_get();

        if (!fb)
            continue;

        httpd_resp_send_chunk(req, "--frame\r\n", 9);
        httpd_resp_send_chunk(req, "Content-Type: image/jpeg\r\n\r\n", 28);
        httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len);
        httpd_resp_send_chunk(req, "\r\n", 2);

        esp_camera_fb_return(fb);
    }

    return ESP_OK;
}

/* START CAMERA SERVER */

void startCameraServer()
{
    httpd_config_t config = HTTPD_DEFAULT_CONFIG();
    httpd_handle_t server = NULL;

    httpd_uri_t stream_uri = {
        .uri = "/stream",
        .method = HTTP_GET,
        .handler = stream_handler,
        .user_ctx = NULL};

    if (httpd_start(&server, &config) == ESP_OK)
    {
        httpd_register_uri_handler(server, &stream_uri);
    }
}

/* AI TASK */

void aiTask(void *pvParameters)
{
    while (true)
    {
        camera_fb_t *fb = esp_camera_fb_get();

        if (!fb)
        {
            vTaskDelay(100);
            continue;
        }

        int pixels = fb->width * fb->height;

        if (pixels > NUMBER_OF_INPUTS)
            pixels = NUMBER_OF_INPUTS;

        for (int i = 0; i < pixels; i++)
            input_data[i] = fb->buf[i] * 0.003921;

        int prediction = ml.predict(input_data);

        float confidence = ml.outputs[prediction];

        Serial.printf("Prediction: %d  |  %.2f%%\n", prediction, confidence * 100);

        esp_camera_fb_return(fb);

        vTaskDelay(2000 / portTICK_PERIOD_MS);
    }
}

/* SETUP */

void setup()
{
    WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

    Serial.begin(115200);
    delay(2000);

    Serial.println("ESP32 AI Camera Starting...");

    /* WIFI */

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWiFi Connected");

    /* PSRAM */

    if (psramFound())
    {
        input_data = (float *)ps_malloc(NUMBER_OF_INPUTS * sizeof(float));
    }
    else
    {
        input_data = (float *)malloc(NUMBER_OF_INPUTS * sizeof(float));
    }

    if (!input_data)
    {
        Serial.println("Memory allocation failed");
        while (true);
    }

    /* LOAD MODEL */

    if (!ml.begin(vandoot_model))
    {
        Serial.println("Model load failed");
        while (true);
    }

    Serial.println("AI Model Loaded");

    /* CAMERA CONFIG */

    camera_config_t config;

    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;

    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;

    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;

    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;

    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;

    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;

    config.xclk_freq_hz = 20000000;

    config.pixel_format = PIXFORMAT_JPEG;

    config.frame_size = FRAMESIZE_QQVGA;

    config.fb_location = CAMERA_FB_IN_PSRAM;

    config.fb_count = 2;

    config.grab_mode = CAMERA_GRAB_LATEST;

    if (esp_camera_init(&config) != ESP_OK)
    {
        Serial.println("Camera init failed");
        while (true);
    }

    Serial.println("Camera Ready");

    /* START STREAM SERVER */

    startCameraServer();

    Serial.print("Camera Stream: http://");
    Serial.print(WiFi.localIP());
    Serial.println("/stream");

    /* START AI TASK */

    xTaskCreatePinnedToCore(
        aiTask,
        "AI Task",
        20000,
        NULL,
        1,
        NULL,
        1);
}

/* LOOP */

void loop()
{
    delay(1000);
}
