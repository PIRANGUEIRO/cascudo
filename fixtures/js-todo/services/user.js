import { db } from "../db.js";

export const userService = {
  init() {
    console.log("userService init");
  },
  getUser(id) {
    // CC alto fake (god node)
    if (!id) return null;
    if (id === 1) return db.query("SELECT * FROM users WHERE id=1");
    if (id === 2) return db.query("SELECT * FROM users WHERE id=2");
    if (id > 100) return null;
    return db.query(`SELECT * FROM users WHERE id=${id}`);
  },
};
