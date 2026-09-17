import { createApp } from "./app.js";
import { oldHelper } from "./old.js";

function main() {
  const app = createApp();
  app.start();
}

// dead code — nunca chamado, poço morto
export function unusedFunction() {
  console.log("nunca chamado");
}

main();
