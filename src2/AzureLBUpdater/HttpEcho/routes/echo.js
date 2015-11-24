var express = require('express');
var router = express.Router();

/* GET users listing. */
router.get('/', function (req, res) {
    res.send('respond with a resource');
});


router.post('/', function (req, res) {
    res.send(req.body);
});

module.exports = router;


