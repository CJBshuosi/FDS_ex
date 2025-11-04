import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class test-connection {
    public static void main(String[] args) {
        String username = "db_28";
        String password = "KBTzY8w4";
        String url1 = "jdbc:oracle:thin:@dmi-dbis-v10.dmi.unibas.ch:1521/XEPDB1";
        String url2 = "jdbc:oracle:thin:@dmi-dbis-v11.dmi.unibas.ch:1521/XEPDB1";
        
        System.out.println("Testing database connections...");
        System.out.println("Username: " + username);
        System.out.println("Password: " + password);
        System.out.println();
        
        // Test Bank X
        System.out.println("Testing Bank X (v10)...");
        System.out.println("URL: " + url1);
        try {
            Class.forName("oracle.jdbc.OracleDriver");
            Connection conn = DriverManager.getConnection(url1, username, password);
            System.out.println("✓ Bank X connection successful!");
            conn.close();
        } catch (Exception e) {
            System.out.println("✗ Bank X connection failed!");
            System.out.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
        
        System.out.println();
        
        // Test Bank Y
        System.out.println("Testing Bank Y (v11)...");
        System.out.println("URL: " + url2);
        try {
            Class.forName("oracle.jdbc.OracleDriver");
            Connection conn = DriverManager.getConnection(url2, username, password);
            System.out.println("✓ Bank Y connection successful!");
            conn.close();
        } catch (Exception e) {
            System.out.println("✗ Bank Y connection failed!");
            System.out.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

