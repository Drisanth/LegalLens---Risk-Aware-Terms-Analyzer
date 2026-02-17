// content_script.js
console.log("LegalLens Content Script Loaded");

function extractPageText() {
    return document.body.innerText;
}

function getWordCount() {
    const text = document.body.innerText;
    return text.split(/\s+/).length;
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getText") {
        const text = extractPageText();
        const wordCount = getWordCount();
        sendResponse({ text: text, wordCount: wordCount });
    }
});

// Optional: Notify if long document
const wordCount = getWordCount();
if (wordCount > 2000) {
    console.log("LegalLens: Long document detected (" + wordCount + " words).");
    // Could inject a badge here if desired
}
