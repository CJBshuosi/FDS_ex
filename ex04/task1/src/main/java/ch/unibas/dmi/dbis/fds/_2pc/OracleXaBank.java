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
        try ( Connection c = this.getXaConnection().getConnection() ) {
            c.setAutoCommit( false );
            final Statement statement = c.createStatement();
            final ResultSet resultSet = statement.executeQuery( "SELECT balance FROM account WHERE iban = '" + iban + "'" );

            if ( resultSet.next() ) {
                return resultSet.getFloat( "balance" );
            }

            throw new SQLException( "Account with IBAN " + iban + " not found" );
        }
    }


    @Override
    public void transfer( final AbstractOracleXaBank TO_BANK, final String ibanFrom, final String ibanTo, final float value ) {
        Xid xidFrom = null;
        Xid xidTo = null;

        try {
            // Phase 1: Start transactions on both banks
            xidFrom = this.startTransaction();
            xidTo = TO_BANK.startTransaction( xidFrom );

            // Phase 2: Execute withdraw on source bank
            try ( Connection cFrom = this.getXaConnection().getConnection() ) {
                final Statement stmtFrom = cFrom.createStatement();
                stmtFrom.executeUpdate( "UPDATE account SET balance = balance - " + value + " WHERE iban = '" + ibanFrom + "'" );
            }

            // Phase 3: Execute deposit on destination bank
            try ( Connection cTo = TO_BANK.getXaConnection().getConnection() ) {
                final Statement stmtTo = cTo.createStatement();
                stmtTo.executeUpdate( "UPDATE account SET balance = balance + " + value + " WHERE iban = '" + ibanTo + "'" );
            }

            // Phase 4: End transactions (prepare phase)
            this.endTransaction( xidFrom, false );
            TO_BANK.endTransaction( xidTo, false );

            // Phase 5: Prepare phase - check if both can commit
            int prepareFrom = this.getXaResource().prepare( xidFrom );
            int prepareTo = TO_BANK.getXaResource().prepare( xidTo );

            // Phase 6: Commit phase - commit if both prepared successfully
            if ( prepareFrom == XAResource.XA_OK && prepareTo == XAResource.XA_OK ) {
                this.getXaResource().commit( xidFrom, false );
                TO_BANK.getXaResource().commit( xidTo, false );
            } else {
                // Rollback if any prepare failed
                this.getXaResource().rollback( xidFrom );
                TO_BANK.getXaResource().rollback( xidTo );
                throw new SQLException( "Transaction prepare failed" );
            }

        } catch ( Exception e ) {
            // Rollback on any error
            try {
                if ( xidFrom != null ) {
                    this.endTransaction( xidFrom, true );
                    this.getXaResource().rollback( xidFrom );
                }
                if ( xidTo != null ) {
                    TO_BANK.endTransaction( xidTo, true );
                    TO_BANK.getXaResource().rollback( xidTo );
                }
            } catch ( XAException xaEx ) {
                xaEx.printStackTrace();
            }
            throw new RuntimeException( "Transfer failed: " + e.getMessage(), e );
        }
    }
}
