import { userService } from "../services/user.js";

export const userController = {
  handle() {
    return userService.getUser(1);
  },
};
