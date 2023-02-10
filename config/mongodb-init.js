db = db.getSiblingDB("grow-simplee");
db.createCollection("user");
db.createCollection("item");
db.createCollection("route");
db.createCollection("route_archive");

const user = require("/user.json");
const hub = require("/hub.json");

db.user.insertMany(user);
db.item.insertMany(hub);
