const express = require("express");
const app = express();
const path = require("path");
const { MongoClient } = require("mongodb");

const PORT = 5050;
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
//app.use(express.static("public"));
app.use(express.static(path.join(__dirname, "public")));

// Use env variable set in docker-compose
const MONGO_URL = "mongodb://admin:qwerty@mongo:27017/employee?authSource=admin";
const client = new MongoClient(MONGO_URL);

// GET all users
app.get("/getUsers", async (req, res) => {
    try {
        await client.connect();
        console.log("Connected successfully to MongoDB");
        const db = client.db("employee");
        const data = await db.collection("it_employees").find({}).toArray();
        res.json(data);
    } catch (err) {
        console.error(err);
        res.status(500).send("Error fetching users");
    } finally {
        await client.close();
    }
});

// POST new user
app.post("/addUser", async (req, res) => {
    try {
        await client.connect();
        console.log("Connected successfully to MongoDB");
        const db = client.db("employee");
        const result = await db.collection("it_employees").insertOne(req.body);
        res.json(result);
    } catch (err) {
        console.error(err);
        res.status(500).send("Error inserting user");
    } finally {
        await client.close();
    }
});

// Serve index.html at "/"
//app.get("/", (req, res) => {
//  res.sendFile(path.join(__dirname, "public", "index.html"));
//});

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});

