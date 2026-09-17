import java.util.*;
public class Main {
    public static void main(String[] args) {
        Helper h = new Helper();
        h.run();
    }
    public static void deadMethod() {
        System.out.println("dead");
    }
}
class Helper {
    public void run() { System.out.println("run"); }
}
