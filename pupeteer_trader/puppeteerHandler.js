import puppeteer from "puppeteer-core";

let browser;
let page;

const amountToTrade = process.env.AMOUNT_TO_TRADE
const passwordToWallet = process.env.PASSWORD_TO_WALLET
const wsEndpoint = process.env.BROWSER_WS_ENDPOINT

const clickButton = async (context, text) => {
    await context.evaluate((text) => {
        const buttons = document.querySelectorAll('button');
        for (let button of buttons) {
            if (button.innerText.trim() === text) {
                button.click();
                break;
            }
        }
    }, text);
}

const delay = async (del) => {
    await new Promise((res) => setTimeout(res, del))
}

const phantomLogin = async () => {
    let tries = 0;
    let extensionPopup;
    while (!extensionPopup && tries++ < 10) {
        extensionPopup = await findPopup();
        await delay(500);
    }
    if(tries > 9) {
        return;
    }
    await extensionPopup.waitForSelector('button');
    await delay(500)
    await extensionPopup.type('input[placeholder="Password"]', passwordToWallet)
    await clickButton(extensionPopup, "Unlock")
    await delay(2000)
    await extensionPopup.waitForSelector('button[data-testid="primary-button"]');
    await delay(500)
    await extensionPopup.click('button[data-testid="primary-button"]')
    await confirmTransaction()
}

export async function initializePumpFun() {
    browser = await puppeteer.connect({
        browserWSEndpoint: wsEndpoint
    });
    
    page = await browser.newPage();
    console.info("Loading pump.fun...")
    await page.goto('https://pump.fun');
    await phantomLogin();
}

export async function buyCoin(coinHash) {
    console.log('Buying', coinHash);
    await page.goto(`https://pump.fun/${coinHash}`)
    await page.waitForFunction(() => {
        const loadingElement = document.querySelector('div[data-testid="oval-loading"][aria-busy="true"]');
        const targetElement = document.querySelector('button.p-2.text-center.rounded.bg-green-400.text-primary');
        return !loadingElement && targetElement;
      });
    await delay(500);
    console.log(amountToTrade)
    await page.type('input[placeholder="0.0"]', amountToTrade);
    await clickButton(page, 'place trade')
    await confirmTransaction()
    await delay(2000)
    await page.reload()
}

export async function sellCoin(coinHash) {
    console.log('Selling ', coinHash);
    if(page.url() != `https://pump.fun/${coinHash}`) {
        await page.goto(`https://pump.fun/${coinHash}`)
    }
    await page.waitForSelector('input[placeholder="0.0"]');
    await clickButton(page, "Sell")
    await clickButton(page, "100%")
    await clickButton(page, 'place trade')
    await confirmTransaction()
}

const confirmTransaction = async () => {
    let extensionPopup;
    while (!extensionPopup) {
        extensionPopup = await findPopup();
        await delay(500);
    }
    try {
        await extensionPopup.waitForSelector('input[placeholder="Password"]', { timeout: 200 });
        await extensionPopup.type('input[placeholder="Password"]', passwordToWallet)
        await delay(2000)
        await clickButton(extensionPopup, "Unlock")
        await delay(1500)
    } catch {}
    while (true) {
        try {
            await extensionPopup.waitForSelector('button[data-testid="primary-button"]', { timeout: 200 });
            await clickButton(extensionPopup, 'Confirm');
            await delay(500); // Delay before trying again
        } catch (e) {
            // If the button is not found within the timeout, check if the popup is still open
            const pages = await browser.pages();
            if (!pages.includes(extensionPopup)) {
                console.log('Popup closed');
                break;
            }
        }
    }
}

const findPopup = async () => {
    console.log(browser)
    const targets = await browser.targets();
    const popupTarget = targets.find(target => target.type() === 'page' && target.url().includes('chrome-extension://'));
    return popupTarget ? await popupTarget.page() : null;
};

export async function closeBrowser() {
    if (browser) {
        await browser.close();
    }
}