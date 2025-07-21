const express = require("express");
const router = express.Router();
const authController = require("./authController");
const auth = require("../middleware/auth");

router.post("/login", authController.login);
router.post("/register", authController.register);
router.delete("/delete", auth, authController.deleteAccount);

module.exports = router;
