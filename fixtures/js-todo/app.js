import { router } from "./routes.js";
import { userService } from "./services/user.js";

export function createApp() {
  return {
    start() {
      router.register();
      userService.init();
    },
  };
}

// ciclo artificial: app.js -> routes.js -> app.js
export function helper() {
  return router;
}
