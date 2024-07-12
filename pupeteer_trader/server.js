import express from 'express'
import { buyCoin, initializePumpFun, closeBrowser, sellCoin } from './puppeteerHandler.js';

const app = express();
const PORT = 3000;

app.get('/buy/:coin', async (req, res) => {
    await buyCoin(req.params.coin);
    res.send('Bought!');
});

app.get('/sell/:coin', async (req, res) => {
    await sellCoin(req.params.coin);
    res.send('Sold!');
});

app.listen(PORT, async () => {
    await initializePumpFun();
    console.log(`Server is running on http://localhost:${PORT}`);
});

process.on('SIGINT', async () => {
    process.exit();
});