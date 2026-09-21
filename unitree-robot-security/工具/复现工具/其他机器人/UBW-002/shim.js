// shim.js — 在 Node 中为 tim-js-sdk(web版) 补齐浏览器环境
const { JSDOM } = require('jsdom');
const dom = new JSDOM('<!doctype html><html><body></body></html>', {
  url: 'https://localhost/',
  pretendToBeVisual: true,
});
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.location = dom.window.location;
global.HTMLElement = dom.window.HTMLElement;
global.addEventListener = dom.window.addEventListener.bind(dom.window);
global.removeEventListener = dom.window.removeEventListener.bind(dom.window);
global.dispatchEvent = dom.window.dispatchEvent.bind(dom.window);
global.getComputedStyle = dom.window.getComputedStyle.bind(dom.window);
global.localStorage = dom.window.localStorage;
global.sessionStorage = dom.window.sessionStorage;
global.XMLHttpRequest = require('xhr2');
global.WebSocket = require('ws');
module.exports = dom;
