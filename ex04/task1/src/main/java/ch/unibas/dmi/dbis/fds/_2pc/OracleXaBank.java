package ch.unibas.dmi.dbis.fds._2pc;


import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

import javax.transaction.xa.XAException;
import javax.transaction.xa.XAResource;
import javax.transaction.xa.Xid;


/**
 * Check the XA stuff here --> https://docs.oracle.com/cd/B14117_01/java.101/b10979/xadistra.htm
 *
 * @author Alexander Stiemer (alexander.stiemer at unibas.ch)
 */
public class OracleXaBank extends AbstractOracleXaBank {


    public OracleXaBank( final String BIC, final String jdbcConnectionString, final String dbmsUsername, final String dbmsPassword ) throws SQLException {
        super( BIC, jdbcConnectionString, dbmsUsername, dbmsPassword );
    }


    @Override
    public float getBalance( final String iban ) throws SQLException {
        // TODO: your turn ;-)
        try ( Connection c = this.getXaConnection().getConnection()) {  // Get a connection from the XAConnection pool
            c.setAutoCommit(false);
            final Statement statement = c.createStatement();
            final ResultSet result  = statement.executeQuery("SELECT balance FROM account WHERE iban = '" + iban + "'");
            if (result.next()) {
                return result.getFloat("balance");
            }
            throw new SQLException("Account with IBAN " + iban + " not found."); 
        }
        
    }

    @Override
    public void transfer( final AbstractOracleXaBank TO_BANK, final String ibanFrom, final String ibanTo, final float value ) {
        // TODO: your turn ;-)
        Xid xidFrom = null;
        Xid xidTo = null;
        try {
            // step 1: Start transactions on both banks
            xidFrom = this.startTransaction();
            xidTo = TO_BANK.startTransaction(xidFrom);
            // step 2: Withdraw from source bank
            try( Connection c_from = this.getXaConnection().getConnection() ){
                c_from.setAutoCommit(false);
                final Statement statement = c_from.createStatement();
                statement.executeUpdate("UPDATE account SET balance = balance - " + value + " WHERE iban = '" + ibanFrom + "'");
            }
            // step 3: Deposit on target bank
            try( Connection c_to = TO_BANK.getXaConnection().getConnection()) {
                c_to.setAutoCommit(false);
                final Statement statement = c_to.createStatement();
                statement.executeUpdate("UPDATE account SET balance = balance + " + value + " WHERE iban = '" + ibanTo + "'");
            }
            // step 4: End transactions
            this.endTransaction(xidFrom, false);
            TO_BANK.endTransaction(xidTo, false);
            // step 5: Prepare -- check if both can commit
            int prepareFrom = this.getXaResource().prepare(xidFrom);
            int prepareTo = TO_BANK.getXaResource().prepare(xidTo);
            
            // step 6: Commit
            if(prepareFrom == XAResource.XA_OK && prepareTo == XAResource.XA_OK) {
                this.getXaResource().commit(xidFrom, false);
                TO_BANK.getXaResource().commit(xidTo, false);
                System.out.println("Transaction Successful.");
            } else {
                this.getXaResource().rollback(xidFrom);
                TO_BANK.getXaResource().rollback(xidTo);
                throw new SQLException("Prepare failed.");
            }
    
        } catch( Exception e) {
            // Rollback on both banks
            try {
                if(xidFrom != null) {
                    this.endTransaction(xidFrom, true);
                    this.getXaResource().rollback(xidFrom);
                }
                if( xidTo != null) {
                    TO_BANK.endTransaction(xidTo, true);
                    TO_BANK.getXaResource().rollback(xidTo);
                }
                System.out.println("Transaction failed. Rollback successful.");
            } catch (Exception e2) {
                e2.printStackTrace();
            }
            throw new RuntimeException(e);
        }
    }
}
