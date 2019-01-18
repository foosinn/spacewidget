const mqtt = require('mqtt');
const WebSocketClient = require('websocket').client;

// params

var ws_url = process.env.WS_URL || 'ws://localhost:8080/push';
var token = process.env.TOKEN || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVC9';
var mqtt_url = process.env.MQTT_URL || 'mqtt://localhost';
var topics = process.env.TOPICS;
if (topics) {
    topics = topics.split(',');
} else {
    topics = ['members'];
}
var cache = {};

// setup

var ws_client = new WebSocketClient();
ws_client.connect(ws_url);
var mqtt_client = mqtt.connect(mqtt_url, options={"keepalive": 5});

var mqtt_timer = null;
var ws_timer = null;

// mqtt connection handling

mqtt_client.on('close', () => {
    // mqtt already handles disconnects
    console.log('mqtt disconnected.');
});
mqtt_client.on('connect', (connection) =>  {
    console.log('mqtt connected.');
    mqtt_client.subscribe(topics, options={"rap": true, "rh": true});
});


// ws connection handling
function ws_connect() {
    console.log('ws disconnected!');
    ws_timer = setTimeout(() => {
        console.log('ws connecting...');
        ws_client.connect(ws_url);
    }, 1000);
}

ws_client.on('connectFailed', ws_connect);
ws_client.on('connect', (connection) => {
    console.log('websocket connected.');
    connection.sendUTF(`Authorization: Token ${token}`);
    Object.entries(cache).forEach((topic, message) => {
        connection.sendUTF(`${topic}: ${message}`);
    });

    // forward messages
    mqtt_client.on('message', function(topic, message) {
        console.log(topic, message.toString());
        cache[topic] = message;
        connection.sendUTF(`${topic}: ${message}`);
    });

    connection.on('close', ws_connect);
});
