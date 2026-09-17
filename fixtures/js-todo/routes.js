import { helper } from "./app.js";
import { userController } from "./controllers/user.js";

export const router = {
  register() {
    console.log("routes registered", helper);
    userController.handle();
  },
};
