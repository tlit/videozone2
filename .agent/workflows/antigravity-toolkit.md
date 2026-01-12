---
description: How to use the Antigravity Toolkit to interact with VideoZone
---

# Antigravity Toolkit Workflows

This toolkit allows you to interact with the running VideoZone application.

## Prerequisites
- The app must be running (`npm run dev`).
- The app must be open in the browser.

## 1. Check App Health (`check-health`)
Use this to see if the app is online and the backend is connected.

```javascript
// Run in browser_subagent
const state = window.__ANTIGRAVITY__.getState();
return state;
```

## 2. Inject Prompt (`inject-prompt`)
Use this to programmatically change the hallucination prompt.

```javascript
// Run in browser_subagent
// REQUIRED: 'prompt' variable
await window.__ANTIGRAVITY__.actions.injectPrompt("Your Prompt Here");
```

## 3. Run Diagnostic Journey (`run-diagnostics`)
Use this to verify the entire stack is functional.

1. Check State.
2. Ping Backend.
3. Inject Test Prompt.
4. Verify State Update.

```javascript
// Run in browser_subagent
const bridge = window.__ANTIGRAVITY__;
if (!bridge) throw new Error("Antigravity Bridge not found!");

const initial = bridge.getState();
console.log("Initial State:", initial);

const ping = await bridge.actions.pingBackend();
console.log("Backend Connected:", ping);

await bridge.actions.injectPrompt("ANTIGRAVITY DETECTED");

// Wait for update (optional, UI update might take a frame)
await new Promise(r => setTimeout(r, 500));

const final = bridge.getState();
console.log("Final State:", final);

return { initial, ping, final };
```
